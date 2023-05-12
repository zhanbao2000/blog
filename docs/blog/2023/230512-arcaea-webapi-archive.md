---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 15 min
tags:
    - arcaea
    - archive
title: （存档）什么是 webapi 查分方案
description: 作为 mokabot 旧文档的备份之一，这里简单描述了 2021 年 6 月至 2022 年 3 月期间使用的 Arcaea webapi 查分方案。
---

!!! info

    作为 mokabot 旧文档的备份之一，这里简单描述了 2021 年 6 月至 2022 年 3 月期间使用的 Arcaea webapi 查分方案。

    因 mokabot 重构，删除了一些过时的旧文档，其中也包括此篇文档。

    本来这篇文档也是被删除的对象之一，但鉴于 webapi 查分方案作为 2021 年 6 月至 2022 年 3 月期间（我）查分的最后手段，是具有一定历史意义的，因此特地将文档存档至博客。

    这篇文档的原始地址是 https://github.com/MokaDevelopers/mokabot2/blob/master/docs/advanced/whats_webapi.md

以下正文开始：

!!! warning 注意

    注意 这不是一个长久之计

## 原理（面向开发者）

webapi 查分方案利用了 Arcaea 官网的登录机制。

当你在官网进行 [登录](https://arcaea.lowiro.com/zh/login) 之前，请打开浏览器的开发者模式（一般是按下 ++f12++）并切换到网络选项卡，在登录完成后在网络请求中筛选出包含 `webapi` 的 url。

找到一个 `https://webapi.lowiro.com/webapi/user/me` 的 url，观察其响应 json。

👍👍👍

如果你是一个对 Arcaea 的 API 非常熟悉的人，看到这个 json 的内容，此时你已经猜到我下一步要怎么做了。但是这个方案最大的缺点就是，webapi 仅能实现 `登录` 这一个操作，其他自动化操作（例如，`添加好友`、`删除好友` 和 `好友歌曲成绩`等 API）均无法实现，因此暂时只能人工上号添加好友并且不删除它。

受限制于每个账号默认只有 10 个好友位，因此需要大量账号来组成一个账号集群。

## 原理（面向用户）

我将以一个用户能看懂的方式来描述这一（半）自动化行为。

#### STEP1: 用户向mokabot提交绑定信息

```http
arc绑定 114514191
arc绑定用户名 FuLowiriCk
```

此时好友码和用户名都绑定完毕。

#### STEP2: mokabot提醒我添加好友

```
收到新的arc用户名绑定（用户名:FuLowiriCk，好友码:114514191，QQ:12345678），请记得加好友
```

#### STEP3: 我将你添加到 `PArisa` 的好友列表中

打开手机上的 Arcaea 客户端，登录到 PArisa，输入你的好友码 `114514191`，然后你成为了 PArisa 的 Arcaea 好友。


#### STEP4: 你此时可以使用`arc最近`指令

```
arc最近
```

#### STEP5: mokabot 试图获取你的成绩

mokabot 登录到 PArisa 的账号，从所有好友的成绩中一一筛选，直到找到你的好友名（这也是使用 webapi 查分方案需要绑定好友名的根本原因）。

#### STEP6: mokabot 找到了你的成绩，分析并发送

## PArisa

`PArisa` 是一个使用 webapi 查分方案的账号集群，目前约有 50 个账号，可以提供大约 500 个 Arcaea 好友位容量。

当本文档中提到 `PArisa` 时，你总是可以将其视为一个具有 500 个好友位的巨型缝合账号。
