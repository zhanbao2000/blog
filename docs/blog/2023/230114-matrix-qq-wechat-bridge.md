---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 60 min
tags:
    - matrix
    - qq
    - wechat
    - cloudflare
    - cloudflare-workers
    - nginx
title: "通过 Matrix 协议实现代理接收 QQ 和微信消息 —— 从入坑到入土"
description: "QQ 与微信客户端在各个平台上均存在不同程度上的作恶行为，包括但不限于：后台常驻保活、占用大量存储空间、远程聊天记录管理不善等，与之形成强烈反差的是 Telegram 客户端。我们急切需要一个像 Telegram 一样友好的工具来代理接收和发送 QQ 和微信消息。"
---

## 一、绪论

QQ 与微信客户端在各个平台上均存在不同程度上的作恶行为，包括但不限于：后台常驻保活、占用大量存储空间、远程聊天记录管理不善等，与之形成强烈反差的是 Telegram 客户端。我们急切需要一个像 Telegram 一样友好的工具来代理接收和发送 QQ 和微信消息。

目前，QQ 和微信早就有了完善的 Bot 支持，例如 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 和 [ComWeChatRobot](https://github.com/ljc545w/ComWeChatRobot)。那么有没有一种可能，我们寻找（甚至设计）一个客户-服务端，将服务端部署于 VPS 上运行 Bot 程序从而接收来自 QQ 和微信的消息，并在终端设备上运行更友好的客户端呢？

事实上，我们无需设计，这个思路早就有前人实践过了。这个服务端就是 [Synapse](https://github.com/matrix-org/synapse/)（又被称为 Matrix homeserver），这个客户端就是 [Element](https://github.com/vector-im)（全平台支持），他们之间通过 [Matrix](https://matrix.org/) 协议进行通信（以下将该方案简称为 `bridge 转发方案`）

本文主要介绍了如何通过 bridge 转发方案实现代理接收 QQ 和微信消息，以及三个月后我为什么最终放弃了它。

本文假定读者已经了解 Matrix 协议，如果不了解，可以参考 [Matrix 协议简介](https://matrix.org/docs/guides/introduction)。

## 二、入坑

### 2.1 服务端与服务端的坑

关于服务端的部署，可直接参阅 Duo 的这篇博客：[Matrix, QQ and Wechat](https://duo.github.io/posts/matrix-qq-wechat/)

按照上述博客部署服务端时会遇到很多问题（例如采用 nginx 时很多地方均与教程有出入），现总结如下：

#### 关于宿主 80 被 nginx 占用时的解决方法

我主机上的 443 端口被 trojan-go 占用，会自动将 443 的所有的 https 请求解密为 http 传递到 nginx，因此只需要改 80 端口即可。其他情况可类比参考。

所作的事就是将所有来自 `matrix.example.com` 的消息转发到容器内的 `8008` 端口。

不创建 Caddy 容器，而是在 `docker-compose.yml` 的 `synapse` 中加入端口映射：

```yaml
ports:
  - 127.0.0.1:8082:8008
```

然后在宿主的 nginx 上加入 `80` 端口到 `8082` 的反代

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name matrix.example.com;

    # 反代到 synapse
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:8082;
    }
}
```

!!! warning "注意"

    如果你的 bridge 是微信，那么这还没完（见后面关于反代 agent 的补充）。

#### 使用 Cloudflare CDN 时的情况

透过 CDN 时，使用 [Matrix Federation Tester](https://federationtester.matrix.org/) 会自然检测失败，因为它通过 DNS 查询之后尝试用 IP 连接，这显然是没法透过 CDN 的。

此时可以访问 https://matrix.example.com/_matrix/federation/v1/version 或通过 https://app.element.io 来测试可用性。

#### 使两个 bot 自动创建 QQ 和 WeChat 空间以区分不同来源的消息

分别在 QQ 和 WeChat 的两个 `config.yaml` 中修改：

```yaml
personal_filtering_spaces: true
```

如果你已经来晚了（即：有些聊天房间已经处在 Space 外面），那么在 Bot 中执行 `sync space` 即可。

#### 自动清除服务端媒体文件以免服务器硬盘满

`homeserver.yaml` 中加入：

```yaml
media_retention:
    local_media_lifetime: 3d
    remote_media_lifetime: 14d
```

最主要的容量占用来自 `local_xxxxx`，bridge 会自动下载 QQ/WeChat 上的所有媒体到这个文件夹里，我设置的是最多保留 3 天，具体各位结合自己实际情况改。

#### 发送媒体文件大于 XXX MB 时发送失败

1. `max_upload_size` 值的问题

    `homeserver.yaml` 中修改设置：
    
    ```yaml
    max_upload_size: 50M
    ```
    
    这个值如果没有在配置文件中定义，那默认是 50M。

2. 反代的问题

    参考 [Using a reverse proxy with Synapse](https://matrix-org.github.io/synapse/latest/reverse_proxy.html#using-a-reverse-proxy-with-synapse)
    
    以 nginx 为例，将对应的 `location` 加入以下两句：
    
    ```nginx
    client_max_body_size 50M;
    proxy_http_version 1.1;
    ```
    
    nginx 默认的 `client_max_body_size` 很小，不足以接收或发送大型媒体

#### nginx 反代 matrix-wechat-agent

所作的事就是将所有来自 `matrix.example.com/_wechat` 的消息转发到容器内的 `20002` 端口。

同上，在 `docker-compose.yml` 的 `synapse` 中加入端口映射：

```yaml
ports:
  - 127.0.0.1:8083:20002
```

注意：`matrix-wechat-agent` 使用 WebSocket 进行工作，nginx 反代时和 http 反代配置稍有不同：

```nginx
location /_wechat {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_pass http://127.0.0.1:8083;
}
```

#### 部署 `matrix-wechat-agent`

首先，从 `matrix-wechat/config.yaml` 里找到 `listen_secret` 的值并记录。

然后去 [duo/matrix-wechat-agent](https://github.com/duo/matrix-wechat-agent/releases) 下载 `matrix-wechat-agent.exe`。

接下来，从 [ljc545w/ComWeChatRobot](https://github.com/ljc545w/ComWeChatRobot/releases) 处下载必要的 dll 文件，并放在 `matrix-wechat-agent.exe` 同目录下。

运行：

```cmd
matrix-wechat-agent.exe -h wss://matrix.example.com/_wechat -s %LISTEN_SECRET%
```

即可在 `matrix-wechat-agent` 与 `matrix-wechat-bridge` 之间建立 WebSocket 连接。

最后在 Bot 内执行 `login`，并扫码登陆即可。

出现问题最多的地方在于微信版本问题，你的微信版本号必须与 `ComWeChatRobot.dll` 的版本号一致，否则要么加载不出登录二维码，要么干脆连微信都调用不起来。

当时的 `ComWeChatRobot.dll` 版本号是 `3.7.0.30`，但官网微信版本早就不是这个版本了。

!!! danger "危险"

    我是从这里找到老版本微信的，但我无法保证链接安全性，请自行甄别，出现问题概不负责：

     - https://sszs.oss-cn-hangzhou.aliyuncs.com/WeChatSetup3.7.0.30.exe

#### 使用 nginx 时无法加入其他 homeserver 上的房间

在使用 Caddy 部署时，有一个步骤是向 `Caddyfile` 中加入：

```caddy
example.com {
	header /.well-known/matrix/* Content-Type application/json
	header /.well-known/matrix/* Access-Control-Allow-Origin *

	respond /.well-known/matrix/server `{"m.server": "matrix.example.com:443"}`
	respond /.well-known/matrix/client `{"m.homeserver":{"base_url":"https://matrix.example.com"}}`
}
```

而我们在 nginx 部署时没有进行这个步骤，因此需要手动添加。

!!! warning "注意"

    当初我自己尝试的是使用 nginx 语法重现上述功能，但是不知道是 Cloudflare 还是 nginx 自己的问题，这两个 headers 添加之后仍然会受到同源策略影响导致跨域问题，因此我最后使用了 Cloudflare Workers 来实现这个 Respond。

不就是个带 headers 的 Respond 嘛，直接 Workers 开写：

```js
addEventListener('fetch', event => {
  const respond = {
    "m.server": "matrix.example.com:443",
    "m.homeserver": {
      "base_url": "https://matrix.example.com"
    }
  };  // 别忘了替换 example.com

  const json = JSON.stringify(respond, null, 2);

  return event.respondWith(
    new Response(json, {
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      },
    })
  );
});
```

将其路由到 `example.com/.well-known/matrix/*` 即可。

### 2.2 客户端与客户端的坑

推荐使用 [Element](https://github.com/vector-im) 作为 Matrix 协议的客户端，Element 的前身是 Riot.im，但是很显然它现在已经被 Element 代替。

Element 客户端的使用基本处于上手即用的级别，但需要注意的是，Matrix 协议采用 “房间” 的形式进行管理，即多人房间则为群聊，两人房间即为私聊。

#### 贴纸

习惯 Telegram 的朋友和用多了 QQ 的朋友看到这里都沉默了，没有贴纸 / 表情包这怎么活？

事实上，Element（或者其他 Matrix 客户端）对贴纸（还包括挂件、Bot 等）的支持十分鸡肋，因为这些东西需要由管理集成服务器（例如 [scalar.vector.im](https://scalar.vector.im/)）统一管理。单就贴纸而言，所有的贴纸均来自独立的管理集成服务器（服务器甚至可以与你的 homeserver 不同），发送贴纸的流程极其诡异，以至于我对这玩意都说不清楚。但目前可以确定的是，所有贴纸均**不属于**用户个人，用户只能在已经部署好的管理集成服务器中选择其中提供的贴纸，而不能自己上传，这就好像一个不能上传的图床。

不过我们可以曲线救国，通过添加挂件的方式变相实现管理集成服务器的功能，具体操作可见竹林里有冰的博客：[为Element 添加自己喜欢的贴纸](https://zhul.in/2022/08/10/add-sticker-support-for-element/)。

#### 贴纸的坑

没错这里又有坑。

简单来说，创建一个贴纸挂件需要将贴纸上传到任意一个 homeserver（那当然就是我们的这个 homeserver），但是 Synapse 对服务端上保留的所有媒体文件有时间限制，例如我们之前就将 `local_XXXX` 的保留时间限制为 3 天，也就意味着我们上传的贴纸将在 3 天后过期，后续再发送包含贴纸的消息 homeserver 只能响应给你 404。此时我们只能通过 [Protect](https://matrix-org.github.io/synapse/latest/admin_api/media_admin_api.html#protecting-media-from-being-quarantined) API 来避免被删除。为此，我写了一个 Python 脚本来进行批量 Protect：

（请先向 homeserver 上传完所有贴纸后再进行该 Protect 操作）

```python title="protect.py"
import os
import json

from aiohttp import ClientSession


def get_media_id_list() -> list:
    result = []
    for root, dirs, files in os.walk(r'D:\path\to\web\packs'):
        for file in files:
            if file == 'index.json':
                continue
            if file.endswith('.json'):
                # load the json
                with open(os.path.join(root, file), 'r') as f:
                    j = json.load(f)
                for sticker in j['stickers']:
                    media_id = sticker['url'].split('/')[-1]
                    result.append(media_id)

    return result


async def protect():
    headers = {"Authorization": "Bearer 111111111111111111111111111111111111111"}
    # async with ClientSession() as sess, sess.post(url, data=data, headers=headers) as resp:
    #     return (await resp.json())["content_uri"]
    async with ClientSession() as session:
        for media_id in get_media_id_list():
            url = f'https://matrix.example.com/_synapse/admin/v1/media/protect/{media_id}'
            async with session.post(url, headers=headers) as resp:
                print(url)
                print(await resp.json())


if __name__ == '__main__':
    import asyncio
    asyncio.run(protect())
```

请注意修改其中的 `Bearer token` 和 `example.com` 以及 `os.walk()` 的路径。

这样的话，所有我们上传到 homeserver 的贴纸都将永久保存而不被删除，从而实现贴纸的持久化。

## 三、入土

虽然我指望 bridge 转发方案能够取代臃肿的 QQ 和微信客户端，并以此永久删除电脑、手机和 iPad 上的客户端，但现实是残酷的，它并不能永久取代。

并且由于服务器的负担不断加剧，使得我不得不最终放弃了 bridge 转发方案并决定将 homeserver 从服务器上删除。

我最终放弃这个方案的原因是多样的，主要是组成 bridge 转发方案的各个方面都有着自己的局限性或者缺陷：

### 3.1 服务器

#### 内存

运行一个实时聊天服务端并不是一件很 “轻量” 的事情，于是首当其冲的就是内存的使用。

<figure markdown>
  ![mem](images/230114-matrix-qq-wechat-bridge/mem.png)
  <figcaption>12% 的数据库占用与 10% 的 homeserver 占用</figcaption>
</figure>

我运行了两个 bridge，并加入了若干个公共房间。这还仅仅是在聊天消息低峰期的内存占用量，在高峰期时会更多。

由此带来的问题是，每当聊天高峰期来临时（晚上 20 ~ 25 点），服务器上的其他进程便面临着 Killed 的风险。

其次，在公共房间内解密历史消息时（尤其是图片等媒体），CPU 占用率也会立即达到 100%，甚至曾出现过 `50, 45, 40` 这样几十的负载，这不是一个单核 CPU 的服务器能承受的。

#### 存储空间

众所周知，我们作为一个实时聊天服务端，需要存储大量聊天的数据和媒体，长期积累下来，这些数据和媒体会占用大量的存储空间。

<figure markdown>
  ![mem](images/230114-matrix-qq-wechat-bridge/storage.png)
  <figcaption>数据库占用和媒体占用</figcaption>
</figure>

仅仅是两个 bridge 和若干个公共房间，并且我的设置是：

```yaml
media_retention:
    local_media_lifetime: 3d
    remote_media_lifetime: 7d
```

这同样也是只有 25G 硬盘的 VPS 承受不了的。

### 3.2 homeserver

#### 贴纸

先前已经说过，如果我们想要在 Element 客户端里发送贴纸，必须借助其他的小挂件，而这些小挂件必须由我们亲自构建。这个构建过程是相当麻烦的，虽然有脚本支持，但并不是全自动的，我们仍然需要将生成的 `web` 文件夹手工上传到静态托管页面上。

而在已经有现成小挂件的基础上添加新的贴纸，则需要先上传贴纸后将两个 `web` 文件夹及其 json 文件进行合并，html 文件的合并难度不多做说明，而它生成的 json 文件是极其复杂的，只能再写一个脚本来进行合并操作。

相比之下，QQ 无论是添加新的表情还是收藏其他人的表情都比它方便更多，即使是稍微复杂一点的 Telegram 也比它方便。我们原本就是为了取代 QQ 客户端，但在这一点上 bridge 转发方案显然不如他，仍然坚持这种舍本逐末的行为是很愚蠢的。

#### 查看图片

另一个十分致命的局限性是，Synapse 并不原生支持将多张图片发送在同一个消息内，也不支持文字和图片发送在同一个消息内，而这在 QQ 里显然是支持的。

为了实现这个特性，`matrix-qq-bridge` 只能通过 markdown 的形式将多张图片以及文字发送在同一个消息内，这导致了一个相当影响体验的问题：无法点开这些图片从而查看大图，这导致有个时候我必须打开 QQ 客户端才能看其中感兴趣的图片。

### 3.3 客户端

Element 本身是一个好的客户端，但是对我们（只用到了 bridge 转发方案）来说，它的功能实在是太多了，甚至有点浪费，例如投票、发送位置等。

<div markdown>

![zoom](images/230114-matrix-qq-wechat-bridge/zoom.jpg){ align=right width=50% }

另一方面，Element 的 iOS、Android 和 Web 客户端对图片缩略图的尺寸处理不是很好，无论多大还是多小的图片，当他们在 Element 客户端上显示时，都将被等比缩放直到某一最大宽度或是最大高度（疑似）。对于大尺寸图片来说这无可厚非，但是对于小尺寸图片（尤其是表情包）来说，这样的处理方式看起来让人十分不爽。

比如像这样，将一个小小的表情放大至页面接近三分之一的面积，对于常常使用或接收表情的用户来说是相当痛苦的。

<div style="clear:both"></div>

</div>

此外，Element 客户端中还有一些细节令我十分不爽：

 - @ 人时会自动添加一个冒号在后面
 - 点击聊天图片查看大图，返回时将直接返回到聊天记录最底部而不是原来图片的位置（新版本 Bug）

### 3.4 bridge

#### 头像昵称同步

我们能在 Element 中看到来自 QQ 和微信的头像，这是因为 bridge 会将这些头像下载下来。但是当用户更换头像（还包括昵称、群昵称）时，bridge 并不能及时更新这些信息，从而在显示上出现延迟。作为 Bot 开发者，我很清楚这是一个技术局限问题，只能通过定期或手动同步才能解决。

bridge 本身是定期同步，我们也可以手动同步，向 Bot 发送以下消息即可（QQ 和微信的 bridge 都适用）：

```
sync contacts --contact-avatars
sync groups
```

#### 微信

微信的 bridge 和 agent 都是很优秀的设计，但是仍然存在一些问题。

长时间没有收到微信消息后，我猜想可能是 agent 和 bridge 之间存在连接问题或是登录失效，于是尝试 `ping` 指令，发现提示 `You're not logged into Wechat.`，尝试 `login` 登录，提示 `Get QR code timed out. Please restart the login.`。

事实上这个时候已经重连成功了，再次输入 `login` 可能会提示 `You're already logged in`，或者输入 `ping` 会提示 `Logged in as wxid_xxxxxx, connection to Wechat OK (probably)`。

另一种情形是，Bot 突然向我发送一条消息：`You're not logged into Wechat.`，于是尝试 `login` 指令，可是无论发送多少条 `login` 指令，Bot 都不会给我任何回应，尝试 `ping` 永远提示我 `You're not logged into Wechat.`。

这种情况下，无论是操作 Bot 还是重启 agent 都无济于事，只能人工上 VPS 进行 `docker restart xxxx` 重启 bridge 才能修好这个问题。讽刺的是，重启 bridge 之后，等待 agent 自动重连，你甚至不需要再次输入 `login` 指令，它就已经在正常运作了。

几乎每周都会发生两到三次这种问题，以至于我将 `docker restart xxxx` 这条命令写入了 crontab 中，每天凌晨 3 点自动重启 bridge。

另外，受限于微信 agent 本身，你在其他微信客户端上向好友发送的消息，并不会被 agent 同步到 bridge 之中。

甚至还遇到过从 Element 发送的消息，无法到达微信客户端的情况。

以上所有问题，均检查过日志无异样，并且在 duo 的上述 [博客](https://duo.github.io/posts/matrix-qq-wechat/) 中有其他用户提及过类似的问题。由于问题难以稳定复现（或者说复现周期过长），并且我已经决定不再使用 bridge 转发方案了，因此我没有去提 issue 的打算。

## 四、尾声

目前已经重新回归 QQ 和微信官方客户端，并删除服务器上的 homeserver。
