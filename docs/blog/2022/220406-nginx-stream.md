---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 2 min
tags:
    - nginx
    - arcaea
title: nginx 如何设置 stream 转发
---

## 背景

帮 aw 做 AUA 转发节点的时候遇到了这个需求，因为 AUA 需要频繁向 616 请求 API，但是 616 对 同一个 IP 的请求数量有限制，所以 AUA 需要大量的转发节点来维持使用。

aw 的建议是用 `socat` (Linux server) 或者 `netsh` (Windows server)

=== "Linux server"

    ```bash
    socat -d TCP4-LISTEN:6161,reuseaddr,fork TCP4:arcapi-v2.lowiro.com:443
    ```

=== "Windows server"

    ```cmd
    netsh interface portproxy add v4tov4 listenport=6161 connectaddress=arcapi-v2.lowiro.com connectport=443
    ```

问题是我服务器上已经有 `nginx` 了，不是很想装 `socat`。

## 初次尝试

了解到 `nginx` 从 `1.9.0` 开始，新增加了一个 stream 模块，用来实现四层协议的转发、代理或者负载均衡等。用法是直接在 `nginx.conf` 中配置 `stream` 字段。

但是实际配置完成后发现，nginx 并不认识 stream 模块。使用 `nginx -t` 检查配置无法通过。报错提示 `unknown directive "stream" in /etc/nginx/nginx.conf`。

后来了解到，如果需要使 nginx 内置支持 stream 模块，需要在编译时指定 `--with-stream` 选项。即

```bash
./configure --with-stream
```

[官网的说法](http://nginx.org/en/docs/stream/ngx_stream_core_module.html)

这个方法实属过于麻烦，还要重装 nginx。

## 解决方案

从这篇文章了解到了不用重新编译也能支持 stream 模块的方法：

[unknown directive "stream" in /etc/nginx/nginx.conf:86 - Server Fault](https://serverfault.com/questions/858067/unknown-directive-stream-in-etc-nginx-nginx-conf86)

简单来说就是，即使我们没有在编译时指定 `--with-stream` 选项，nginx 也会将 stream 模块编译进来，但是并没有让 nginx 默认支持，而是需要我们自行导入，即：

```nginx
load_module /usr/lib/nginx/modules/ngx_stream_module.so;
```

如此一来便能正常使用 stream 模块。
