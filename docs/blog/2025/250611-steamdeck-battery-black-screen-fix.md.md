---
author: Akiba Arisa
author_gh_user: zhanbao2000
tags:
    - steam
    - steamdeck
title: Steam Deck 因电池耗尽而黑屏，充电却再也无法开机的解决方法
description: 
---

前几天把 Steam Deck 玩到只剩 7% 的电就没管了。过了一天发现开不了机，故寻思可能是没电了，遂充电。充了好几个小时，依然无法开机。

上网查了下，似乎并不是个例[^1][^2]，看起来这是 Steam Deck 的一个 Bug。当然在查找的过程中也找到了正确的解决方法。

[^1]: [Steam Deck won't boot up properly; Black Screen :: Steam Deck 综合讨论](https://steamcommunity.com/app/1675200/discussions/0/3416557114763001833/)
[^2]: [Steam deck screen wont turn on when powering on : r/SteamDeck](https://www.reddit.com/r/SteamDeck/comments/zy3h69/steam_deck_screen_wont_turn_on_when_powering_on/)

## 故障描述

疑似电池已经快耗尽的情况下，进入了睡眠模式。一段时间后：

若按电源键，则白灯闪烁，其他任何硬件均无反应，此为电池耗尽之正常信号[^3]。

若插入电源，则白灯长亮，有开机声，屏幕无任何反应，风扇转速恒定为最大，触摸板有震动反应，但是无法进入系统。此时可以通过长按 5 秒强制关机。

不过，在充电一段时间后，再次按电源键仍然无法开机，这与是否插入电源线无关。此外，在关机状态下插入电源线会自动尝试开机进入系统，但是情况和上文一样。

[^3]: [Steam 客服 :: Steam Deck - 基本使用及故障排除指南](https://help.steampowered.com/zh-cn/faqs/view/69E3-14AF-9764-4C28)

## 解决方法

这里参考了 [Steam Deck won't boot up properly; Black Screen :: Steam Deck 综合讨论](https://steamcommunity.com/app/1675200/discussions/0/3416557114763001833/) 中所述的解决办法，一句话概括就是：让 Steam Deck 先进入电池存储模式，然后再退出来。

具体解决方法：

首先使用物理按键手动进入 Steam Deck 电池存储模式：

1. 移除电源线，并长按电源键 10 秒以上，确保 Steam Deck 完全关机。
2. 将电源线插入 Steam Deck，此时白灯会长亮，风扇转速恒定为最大，触摸板有震动反应，但是始终无法进入系统（即原始故障）。
3. 保持电源线插入，长按电源键 10 秒以上，确保 Steam Deck 完全关机。
4. 关机后，同时按住 “音量+” 和 “···” 按钮，持续 10 秒以上。
5. 保持第 4 步的按键不放，用你的脚或者嘴移除电源线（是的）。
6. 如果操作正确，你应该看到电源白灯闪烁 3 次，之后设备应该不会再对使用电源按钮做出任何反应。 

此时 Steam Deck 已经进入了电池存储模式。接下来需要将其从电池存储模式中唤醒，操作很简单，插入电源线，等待其自动开机即可。

## 关于电池存储模式

参考 [Steam 客服 :: Steam Deck - 基本使用及故障排除指南](https://help.steampowered.com/zh-cn/faqs/view/69E3-14AF-9764-4C28) 中的 “长期存放” 一节，若用户将会有一段时间不使用 Steam Deck，并希望使其处于存放模式以改善其长期的电池健康，则可以启用电池存储模式。要从存放模式中唤醒 Steam Deck，请插入所提供的外接电源，然后正常启动。

上文我们已经介绍了如何使用物理按键手动进入电池存储模式。但是更为常见的情况是，（如果 Steam Deck 可以正常开机）用户可以从 Steam Deck 的 BIOS 菜单中进入电池存储模式。

做法请参考 [如何启用Steam Deck的电池存储模式 - iFixit 维修指南](https://zh.ifixit.com/Guide/%E5%A6%82%E4%BD%95%E5%90%AF%E7%94%A8Steam+Deck%E7%9A%84%E7%94%B5%E6%B1%A0%E5%AD%98%E5%82%A8%E6%A8%A1%E5%BC%8F/149962)。
