---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 8 min
tags:
    - ssl
    - letsencrypt
    - certbot
title: certbot 常用操作
---

## 安装

官网建议用 `snap` 安装。👉 https://certbot.eff.org/instructions?ws=other&os=ubuntufocal

```bash
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
```

## 申请多个域名证书

!!! 警告 danger

    无论你需要申请多少个证书，在申请之前，都请在你的 DNS 提供商处将你所需要申请 SSL 证书的域名解析到你的服务器上。
 
!!! 提示 tips

    根据你的 `80` 端口有没有被占用，你需要使用两种模式—— `nginx` 或者 `standalone`。

 - 你的 `80` 端口已经被 `nginx`（或者其他服务）占用了：

```bash
certbot certonly --nginx -d example.com -d www.example.com -d another.example.com
```

 - 你的 `80` 端口没有被任何服务占用：

```bash
certbot certonly --standalone -d example.com -d www.example.com -d another.example.com
```

## 申请泛域名证书（也叫通配符证书）

比较麻烦，需要在 DNS 服务提供商处设置 `TXT` 记录。并且**只能**通过这个方式来续期。

```bash
certbot certonly -d "*.example.com" -d "example.com" --manual --preferred-challenges dns --server https://acme-v02.api.letsencrypt.org/directory
```

执行之后会交给你一个或两个设置 `TXT` 记录的任务。去你的 DNS 服务提供商处设置好即可。

## 查看自动续期的计划任务

```bash
systemctl list-timers
```

## 手动为证书续期

 - 不加任何参数，没有临近到期时间的话会停止执行

```bash
certbot renew
```

 - 测试续期，不会真的续期

```bash
certbot renew --dry-run
```

 - 强制续期

```bash
certbot renew --force-renewal
```

## 为证书续期（泛域名）

泛域名证书不能通过 `certbot renew` 来续期，需要手动续期。否则会报错。

原因很简单，就是你在申请泛域名证书的时候在 DNS 服务商那里添加的 `TXT` 记录，这是一个会变化的值。

续期方法和申请方法一模一样，相当于重新申请一次。

```bash
certbot certonly -d "*.example.com" -d "example.com" --manual --preferred-challenges dns --server https://acme-v02.api.letsencrypt.org/directory
```

中途同样需要修改 DNS 的 `TXT` 记录这样的操作。有人可能会觉得很麻烦，麻烦你就去写个脚本啊。

事实上 certbot 的报错也说得很清楚了，他的意思就是要我们去写个脚本：

 > An **authentication script** must be provided with --manual-auth-hook when using the manual plugin non-interactively.

网上有各个版本的脚本，大概原理都是通过你 DNS 服务商提供的 Token，在服务器上直接修改 DNS 的 `TXT` 记录。一搜一大堆。

## 吊销（撤销）证书

这里直接引用 [Let's Encrypt 官网](https://letsencrypt.org/zh-cn/docs/revoking/)

 - 用颁发证书的账户吊销证书

```bash
certbot revoke --cert-path /etc/letsencrypt/archive/${YOUR_DOMAIN}/cert1.pem
```

 - 使用证书私钥吊销证书

```bash
certbot revoke --cert-path /PATH/TO/cert.pem --key-path /PATH/TO/key.pem
```

 - 使用其他授权帐户吊销证书

先从 [crt.sh](https://crt.sh/) 中下载证书，然后：

```bash
certbot revoke --cert-path /PATH/TO/downloaded-cert.pem
```

## 删除证书

```bash
certbot delete 
```
