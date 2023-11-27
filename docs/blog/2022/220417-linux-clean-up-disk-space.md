---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 6 min
tags:
    - linux
title: Linux 清理磁盘空间常见操作
---

使用如下方式可以清理 Linux 的绝大部分垃圾。

## 清理 journal 日志

一般可以清理 2~3 GB。

 - 查看 journal 日志占用的硬盘空间：

    ```bash
    journalctl -x --disk-usage
    ```

 - 一次性清理 journal 日志：

    ```bash
    journalctl --vacuum-size=10M  # 清理日志到只剩下 10M
    journalctl --vacuum-time=1d   # 清理一天前的日志
    ```

!!! 注意 attention

    这两个操作只是一次性清除日志，**并不能限制以后的日志文件不会超过这个大小**。很多博客里说这两个操作可以限制日志文件的大小，属实是误导人。

    如果需要永久限制日志文件的大小，需要修改 `/etc/systemd/journald.conf` 文件。

 - 永久限制 journal 日志的大小：

    ```conf title="journald.conf"
    [Journal]
    SystemMaxUse=10M   # 硬盘中只保留最近 10M 的日志
    RuntimeMaxUse=10M  # 内存中只保留最近 10M 的日志
    ```
   
 - 不保留日志

    ```conf title="journald.conf"
    [Journal]
    Storage=none       # 丢弃所有的日志，不保存到内存或磁盘
    ```
   
!!! 危险 danger

    不要使用 `rm` 命令来删除 journal 日志。参考 [删除日志释放空间最好不要用rm](https://www.cnblogs.com/pennychen/p/8681119.html)
   
## 清理 apt-get 缓存

一般可以清理数百 MB。

```bash
apt-get clean
```

## 清理 pip 缓存

一般可以清理两三百 MB。

```bash
rm -r ~/.cache/pip
```

## 清理旧版本 snap 包

一般每个旧的 snap 包可以清理 100 MB。

 - 列出所有的 snap 包：

    ```bash
    snap list --all
    ```

    可以见到很多标记为 `disabled` 的 snap 包，这些包是可以直接卸载的。

    ``` hl_lines="3 5"
    Name     Version    Rev    Tracking       Publisher     Notes
    certbot  1.26.0     1952   latest/stable  certbot-eff✓  classic
    cmake    3.23.0     1070   latest/stable  crascit✓      disabled,classic
    cmake    3.23.1     1082   latest/stable  crascit✓      classic
    core     16-2.55.2  12941  latest/stable  canonical✓    core,disabled
    core     16-2.54.4  12834  latest/stable  canonical✓    core
    core18   20220309   2344   latest/stable  canonical✓    base
    core20   20220318   1405   latest/stable  canonical✓    base
    ```

 - 删除这些重复的 snap 包：

    ```bash
    snap remove XXXX --revision YYYY   # XXXX 是软件的 name，YYYY 是软件的 Rev
    ```
 
 - 也可以使用这个脚本清除：

    来自 [How to Clean Up Snap Package Versions in Linux](https://itsfoss.com/clean-snap-packages/)

    ```bash
    #!/bin/bash
    # Removes old revisions of snaps
    # CLOSE ALL SNAPS BEFORE RUNNING THIS
    set -eu
    snap list --all | awk '/disabled/{print $1, $3}' |
        while read snapname revision; do
            snap remove "$snapname" --revision="$revision"
        done
    ```
   
## 清理登录日志

这个文件是记录错误登录的日志，如果有人每天试你的密码来暴力破解你的 ssh，那你的这个文件就会很大。

```bash
echo "" > /var/log/btmp
```

该文件同理

```bash
echo "" > /var/log/auth.log
```

同理，不应当使用 `rm` 而是使用 `echo` 来清空这两个日志。

## 清理 docker

 - 查看空间占用情况

    ```bash
    docker system df
    ```
    
    ```
    TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
    Images          5         1         645.4MB   611.9MB (94%)
    Containers      1         1         0B        0B
    Local Volumes   1         1         69.54kB   0B (0%)
    Build Cache     0         0         0B        0B
    ```

 - 清理 Build Cache

    ```bash
    docker system prune --volumes
    ```
   
    这会清除所有：

     - 停止的 Container
     - 未被任何 Container 所使用的 Network
     - 未被任何 Container 所使用的 Volume
     - 无实例的 Image
     - 无实例的 Build Cache

 - 清理 Images

    上一步中可能不会清理 Images，从而在 `#!bash docker system df` 中仍然能看到 Images 的空间占用。这一步可以清理这些 Images。

    查看所有的 Image

    ```bash
    docker images -a
    ```

    清理指定的 Image

    ```bash
    docker rmi <IMAGE ID>
    ```
