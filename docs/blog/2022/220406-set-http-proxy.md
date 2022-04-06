---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 4 min
publish_date: 2022-04-06 17:55
tags:
    - python
    - pip
    - proxy
title: 解决使用代理后 pip 和 python 无法连接到网络的问题
---

## 问题

开启系统代理后，当使用 pip 安装包时，会报错：

```
ValueError: check_hostname requires server_hostname
```

以及使用某些网络操作库时（比如 `requests`）也会报这个错。

## 解决方法

在控制台运行 python 脚本前先指定代理地址：

```cmd
set http_proxy=http://127.0.0.1:8889
set https_proxy=http://127.0.0.1:8889
```

其中 `127.0.0.1:8889` 是代理服务器的地址
