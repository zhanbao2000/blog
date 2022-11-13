---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 7 min
tags:
    - guide
    - sharepoint
    - rclone
title: "通过 WebDAV 解决 Rclone 挂载 SharePoint 时遇到 Error: Auth Error"
description: 本文介绍了通过另一种方式，即 WebDAV，来实现 SharePoint 在 Rclone 中的挂载，以解决遇到 Auth Error 的问题。 
---

```
Failure!
Error: Auth Error
Description: No code returned by remote server
```

出现这个错误的原因可能是你所在组织的管理员长期未登录，而导致 OAuth 无法进行。别担心，这与你自己的账号没有关系。

~~这大多是因为该管理员较懒，因为长时间不登录会要求管理员修改自己的密码，一般人谁乐意啊。~~

实际上，如果你手动进行 OAuth 授权操作（而不进行跳转的话），你会发现，浏览器会给出如下提示：

```
Error: 
Invalid Client

Error Description:
AADSTS650051: Using application 'od4hath' is currently not supported for your organization [xxxxxx], because it's in an unmanaged state. An administrator needs to claim ownership of the company by DNS validation of [xxxxxx] before the application 'od4hath' can be provisioned.
```

此时我们不能再使用 SharePoint 本体进行 Rclone 操作，而需要使用 WebDAV 进行操作：

首先，登录我们的 SharePoint 账号，并进入 OneDrive，可以看到浏览器的 URL 应该是：

```
https://____domain____-my.sharepoint.com/personal/____email____/_layouts/15/onedrive.aspx
```

复制这个 URL，将其改写为：

```
https://____domain____-my.sharepoint.com/personal/____email____/Documents
```

现在，这个 URL 即为你的 WebDAV URL。复制这个 URL 并在浏览器打开，它应该重定向到你的 OneDrive 首页。

现在，我们可以使用 Rclone 进行操作了。

在你的云服务器上执行：

```bash
rclone config
```

会出现：

```
e) Edit existing remote
n) New remote
d) Delete remote
r) Rename remote
c) Copy remote
s) Set configuration password
q) Quit config
e/n/d/r/c/s/q>
```

选择 `n`，新建一个，并将该新 remote 命名，假设我们命名为 `od4hath`。

之后会出现：

```
Type of storage to configure.
Enter a string value. Press Enter for the default ("").
Choose a number from below, or type in your own value

31 / Webdav
   \ "webdav"

Storage>
```

选择 `31`，即 WebDAV。

然后按照提示输入你的 URL 与 WebDAV 账户名和密码：

```
** See help for webdav backend at: https://rclone.org/webdav/ **

URL of http host to connect to
Enter a string value. Press Enter for the default ("").
Choose a number from below, or type in your own value
 1 / Connect to example.com
   \ "https://example.com"
url>
```

输入先前复制的 URL 即可。

```
Name of the Webdav site/service/software you are using
Enter a string value. Press Enter for the default ("").
Choose a number from below, or type in your own value
 1 / Nextcloud
   \ "nextcloud"
 2 / Owncloud
   \ "owncloud"
 3 / Sharepoint
   \ "sharepoint"
 4 / Other site/service or software
   \ "other"
vendor>
```

选择 `3`，即 Sharepoint。

```
User name
Enter a string value. Press Enter for the default ("").
user>
```

这里的用户名是你的 Microsoft 账号，即你的邮箱。

```
Password.
y) Yes type in my own password
g) Generate random password
n) No leave this optional password blank (default)
y/g/n>
```

选择 `y`，输入你的密码。

```
Enter the password:
password:
Confirm the password:
password:
```

这里的密码是你的 Microsoft 账号密码。

```
Bearer token instead of user/pass (eg a Macaroon)
Enter a string value. Press Enter for the default ("").
bearer_token>
```

`bearer_token` 一栏留空，直接回车。

```
Edit advanced config? (y/n)
y) Yes
n) No (default)
y/n>
```

选择 `n`，不需要编辑高级配置。

之后你将获得一个已经配置好的 remote。
