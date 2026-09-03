---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 5 min
tags:
    - android
    - kotlin
    - debug
title: 记一次 Android 选图导致 EXIF 信息丢失的 Debug 踩坑之旅
description: 本文记录了 Android 系统下，通过 Photo Picker / SAF 选图导致图片 EXIF 信息被系统强制脱敏丢失的排查过程及最终解决方案。
---

!!! info "省流版"

    Android 系统为了保护隐私，使用新版照片选择器 `PickMultipleVisualMedia()` 或在未授权的情况下通过系统 SAF 获取的图片流，会被底层强制脱敏，抹除 EXIF 信息。
    
    最终解决方案：放弃新版照片选择器，改用传统的 `GetMultipleContents()`，并动态申请 `READ_MEDIA_IMAGES` 与 `ACCESS_MEDIA_LOCATION` 权限。授权后，系统将放行完整的原图字节流。

## 一、起因：离奇丢失的 EXIF 信息

最近在开发 Android 应用时，遇到了一个诡异的问题：应用无法获取原始 EXIF 信息。

调查发现，当你通过代码从 `ContentResolver.openInputStream(uri)` 获取 InputStream，并交给 `ExifInterface` 解析时，解析出来的对象要么是全空，要么只能读到 `ImageWidth`、`ImageLength` 等少数几个 Tag，且具体的值全是 `00`。

但是，把原图导出到电脑上看，所有的 EXIF 信息明明都完好无损地存在。

## 二、排查过程

### 1. 怀疑是 InputStream 不支持 Seek 导致解析失败

最初，我怀疑是因为 `ContentResolver` 返回的 `InputStream` 只能顺序读取，而 EXIF 的 IFD 偏移量通常需要向后或向前跳转 seek。这经常导致 `ExifInterface` 解析出错。

于是我们将方案改为获取 `FileDescriptor`，甚至是把输入流直接拷贝到本地的一个带有 `.jpg` / `.png` 扩展名的临时文件中，再让 `ExifInterface` 直接去解析这个临时文件。

结果：依然全空

### 2. CRC32 校验比对

这不禁让人怀疑：到底是从一开始就没读到，还是解析的问题？

我在代码中加入了一段逻辑，在把流保存为临时文件后，打印出它的 CRC32：

```kotlin
val crc32 = java.util.zip.CRC32()
tempFile.inputStream().use { input ->
    val buffer = ByteArray(8192)
    var bytesRead: Int
    while (input.read(buffer).also { bytesRead = it } != -1) {
        crc32.update(buffer, 0, bytesRead)
    }
}
val crc32Hex = String.format("%08X", crc32.value)
Log.d("EXIF_DEBUG", "tempFile CRC32: $crc32Hex")
```

结论：从 `InputStream` 读取后算出的 CRC32，与原图真实的 CRC32 不一致。

### 3. 交叉验证

为了排除偶然因素，我又进行了不同环境的选图交叉验证

 - 在应用内点击加号，通过原生 SAF / Photo Picker 选图：**CRC32 不一致**。
 - 在系统相册中点击分享，发送到我的应用：**CRC32 不一致**。
 - 在第三方开源文件管理器（如质感文件）中点击分享，发送到我的应用：**CRC32 一致**

## 三、真相大白

结合交叉验证的结果，这就彻底破案了：问题根本不在代码怎么写，而是 Android 系统的隐私保护策略的问题。

1. 当你使用 Android 13 引入的 **Photo Picker**（`PickMultipleVisualMedia`）或者在**没给足权限**的情况下使用原生相册提供文件时，Android MediaStore底层会作为一个代理。为了保护用户的地理位置等隐私，系统会在内存里动态把文件复制一遍并把 EXIF 信息强行抹除。
2. 而质感文件这类拥有所有文件访问权限的第三方文件管理器，它是通过自己的 `FileProvider` 直接把硬盘上原始的文件字节流推给你的 App，完全绕过了 Android 系统的脱敏代理。

由于在底层拿到的字节流在物理上就已经是被阉割过的副本，这就解释了为什么不管我们在代码里怎么调整 `ExifInterface`，都无法读出数据。

## 四、最终解决方案

要彻底解决这个问题，想要在 App 中通过常规选择器拿到带 EXIF 的原图，就不能使用 Photo Picker。

### 第一步：放弃 Photo Picker

根据 Google 官方 [文档](https://developer.android.com/training/data-storage/shared/media?hl=zh-cn#kotlin)，Photo Picker 永远会强制抹除图片的 GPS 位置 EXIF 数据。即使你申请并获得了 ACCESS_MEDIA_LOCATION 权限，你也无法从 Photo Picker 返回的文件里拿到位置信息。

我起初也头铁尝试了文档中提到的 `MediaStore.setRequireOriginal(uri)` 这一 API，试图要求系统交出未经修改的原图流。但遗憾的是，系统直接抛出了异常：

```text
Require Original is not supported for Picker URI content://media/picker/0/com.android.providers.media.photopicker/media/1000155558?requireOriginal=1
```

也有人给 Google 发了 [issue](https://issuetracker.google.com/issues/243294058)。

事实证明，Photo Picker 对于隐私的隔离是绝对且彻底的。

因此，如果你的业务硬性要求完整保留包含位置在内的所有 EXIF 数据，我们必须将 `ActivityResultContracts.PickMultipleVisualMedia()` 替换回 `ActivityResultContracts.GetMultipleContents()` 或 `OpenMultipleDocuments()`。

### 第二步：动态申请专属媒体权限

只有当 App 拥有了读取媒体和位置的对应权限，系统的 SAF 框架（以及系统相册）才会认定你的 App 属于受信任的访客，从而撤销脱敏拦截，交出原文件。

我们需要在 `AndroidManifest.xml` 中加入：

```xml
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.ACCESS_MEDIA_LOCATION" />
```

并在调起选图界面前，动态请求这些权限。一旦用户授权，再通过 `GetMultipleContents()` 选图时，你会发现 CRC32 终于吻合了，EXIF 信息也终于重新出来了。

话说怎么不早点推出 [这个东西](https://www.reddit.com/r/androiddev/comments/1vuk8fr/introducing_the_location_metadata_api_for_the/) 呢？
