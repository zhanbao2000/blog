---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 3 min
tags:
    - cloudflare
    - proxy
title: 使用 Cloudflare WARP 解决 Google Scholar 403 问题
description: 
---

## 问题描述

因为代理服务器 IP 被 Google 拉入了黑名单，导致访问 Google Scholar 时出现 403 错误。但是更换服务器 IP 过于麻烦，因此尝试使用 Cloudflare WARP 来解决这个问题。

在使用 Cloudflare WARP 方案前，你应该首先考虑以下方案，如果还是解决不了，或者你不愿意，那么你可以试试本篇的方案。

 - 改 IPv6：[解决无法访问谷歌学术问题](https://jlhzabc.sbs/article/33)
 - 用 [谷歌上网助手](https://ghelper.net/)
 - 换代理 IP：自己去搜对应 VPS 服务商的教程

## 解决方案

### 安装 WARP

首先使用 docker 安装 WARP（来源：[TunMax/canal](https://github.com/TunMax/canal)）

```bash
docker run -d -p 127.0.0.1:1080:1080/tcp -p 127.0.0.1:1080:1080/udp -e SOCKS5_MODE=true --name canal tunmax/canal:latest
```

此时我们获得了一个运行在 `socks5://127.0.0.1:1080` 的代理。

### 配置代理

以 Hysteria2 为例，在配置文件 `config.yaml`后追加：

```yaml
outbounds:
  - name: warp
    type: socks5
    socks5:
      addr: 127.0.0.1:1080

acl:
  inline:
    - warp(geosite:google-scholar)
    - warp(142.250.68.100)
    - direct(all)
```

需要额外对 `142.250.68.100` 这个 IP 进行 ACL，因为某些客户端的 TUN 会先解析域名为 IP 再对该 IP 进行访问，这会导致服务端的 ACL 抓不到。

相关说明：

 - [outbounds 语法](https://hysteria.network/zh/docs/advanced/Full-Server-Config/#outbounds)
 - [ACL 语法](https://hysteria.network/zh/docs/advanced/ACL/#_6)
