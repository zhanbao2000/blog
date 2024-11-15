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

我们使用 ACL 的方法，在服务端过滤出 Google Scholar 的请求，然后使用 WARP 代理。

以 Hysteria2 为例，在配置文件 `config.yaml` 后追加：

```yaml
outbounds:
  - name: warp
    type: socks5
    socks5:
      addr: 127.0.0.1:1080

acl:
  inline:
    - warp(geosite:google-scholar)
    - direct(all)
```

上述配置**只适用于使用系统代理的用户**。对于使用 TUN 的用户，可能会遇到仍然 403 的问题。这是因为 TUN 会先解析域名为 IP 再对该 IP 进行访问，这会导致服务端的 ACL 抓不到。

有两个方式可以解决：

 - [为 IP 添加 ACL](#ip-acl)
 - [协议嗅探](#_4)

### 为 IP 添加 ACL

在 `direct(all)` 之前添加一行

```yaml
  - warp(142.250.68.100)
```

这会使访问 `142.250.68.100` 的请求也使用 WARP 代理。具体的 IP 需要在客户端使用 `nslookup scholar.google.com` 来获取。

不过 Google Scholar 的 IP 会随时变换，因此这个方法不是很好，需要经常上去更新 IP 地址，而且也会遇到客户端和服务端解析出来的 IP 不一致的问题。因此只适用于临时使用的情况。

### 协议嗅探

开启协议嗅探后，服务端能通过 DPI 从上层协议中获取目标域名，将 IP 请求转换为域名请求。

在配置文件 `config.yaml` 后继续追加：

```yaml
sniff:
  enable: true 
  timeout: 2s 
  rewriteDomain: false 
  tcpPorts: 80,443,8000-9000 
  udpPorts: all
```

但是协议嗅探可能会对服务端的性能以及响应速度产生影响，因此需要根据实际情况来决定是否开启。

## 相关文档

 - [outbounds 语法](https://hysteria.network/zh/docs/advanced/Full-Server-Config/#outbounds)
 - [ACL 语法](https://hysteria.network/zh/docs/advanced/ACL/#_6)
 - [协议嗅探 (Sniff)](https://hysteria.network/zh/docs/advanced/Full-Server-Config/#sniff)
