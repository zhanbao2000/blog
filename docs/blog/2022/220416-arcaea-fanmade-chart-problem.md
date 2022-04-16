---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 2 min
tags:
    - arcaea
title: Arcaea 自制谱移植常见问题
---

一、Arcade 生成的自制谱（以及 Arcaoid 谱）没有确定 `base_bpm`，但是 `songlist` 中这个值比较重要，这体现在：

 - `bpm` 字段不影响谱面基准流速，只影响选曲界面的显示效果，因此可以设置为任意值，或者写一些奇奇怪怪的东西（比如定数）
 - `bpm_base` 的值与 `timing` 语句中声明的 bpm 的比值决定该段 timing 内的实际流速倍率（？）。
    - 这个比值越小，流速越快
    - 一般情况下建议把 `bpm_base` 直接设置为 `t=0` 的 `timing` 语句中规定的 bpm，因为**绝大部分**情况下这个值都是这首歌的 bpm 值
    - 但当遇到某些谱面开头流速异常（例如白魔王）时，建议把 `base_bpm` 设置成其他 `timing` 语句中规定的 bpm 值

我们以白魔王为例：

``` aff title="pragmatism_2.aff" linenums="1" hl_lines="1 8"
timing(0,87.00,2.00);
timing(11034,174.00,4.00);
timing(33103,348.00,1.00);
timing(34482,174.00,4.00);
timing(57930,87.00,2.00);
timing(68964,130.50,3.00);
timing(78620,174.00,4.00);
timing(103447,0.00,4.00);
timing(104826,87.00,4.00);
...
```

注意，白魔王的 `base_bpm` 在 `songlist` 里设置为 `174`。

因此，`0~11034` 内谱面速度会降到原来的一半，而 `103447~104826` 内谱面速度变成 `0`（骤停效果）。

二、虽然官方曲子的 `base.jpg` 是 512x512，`base_256.jpg` 是 256x256，但是实际上这个尺寸是可以随便设计的，甚至不是正方形都行。

三、某些自制谱中 `aff` 文件的语句不符合 Arcaea 规范。这些谱面在 Arcade 中能正常播放，但是在 Arcaea 中选曲完成后会立即闪退。以下是我找到的一些问题：

 - `timing` 语句中，`beats` 参数不能为 `0.00`，很多自制谱为了不出现节拍线会设置成 `0.00`
 - 每个谱面有且仅有一个 `t=0 `的 `timing` 语句，且其 `bpm` 参数不可为负数。
 - `timing` 语句中，`bpm` 参数必须保留两位小数
 - `camera` 语句的第 2-7 个参数（即 `transverse`, `bottomzoom`, `linezoom`, `steadyangle`, `topzoom`, `angle`）必须保留两位小数
 - `arc` 语句中 `color` 参数的值只能是 `0/1/2`，某些自制谱会写 `-1`
 - `arc` 语句中 `t1`、`t2` 参数的值均为非负整数，某些自制谱会写成负数

我写了一个简单的 patch 函数来解决这个问题：

``` python linenums="1"
def patch_line(line: str) -> str:
    timing_params = re.match(r'timing\((.+),(.+),(0\.00)\);', line)
    camera_params = re.match(r'camera\((.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+)\);', line)
    arc_params = re.match(r'arc\((.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+)\)(.+)?;', line)
    if timing_params:
        t, bpm, beats = timing_params.groups()
        # timing 函数中，beats 不能为 0.00（一些自制谱常见问题），否则必然客户端闪退（闪退时不会发出声音）
        if beats == '0.00':
            beats = '4.00'
        # timing 函数中，bpm 必须保留两位小数，否则必然客户端闪退
        if '.' not in bpm or bpm.split('.')[1] != '00':
            bpm = f'{float(bpm):.2f}'
        return f'timing({t},{bpm},{beats});\n'
    elif camera_params:
        t, *params, easing, lastingtime = camera_params.groups()
        for index, param in enumerate(params):
            # camera 函数的 2-7 个参数必须保留两位小数（一些自制谱常见问题），否则必然客户端闪退
            if '.' not in param or param.split('.')[1] != '00':
                params[index] = f'{float(param):.2f}'
        return f'camera({t},{",".join(params)},{easing},{lastingtime});\n'
    elif arc_params:
        t1, *params, color, FX, skylineBoolean, arc_taps = arc_params.groups()
        print(arc_params.groups())
        # arc的t1、t2均为非负整数，某些自制谱会写成负数，这将导致闪退
        if t1.startswith('-'):
            t1 = '0'
        # arc的蛇的颜色参数，只能是0\1\2，某些自制谱会写-1，这将导致闪退
        if color == '-1':
            color = '2'
        if not arc_taps:
            arc_taps = ''
        return f'arc({t1},{",".join(params)},{color},{FX},{skylineBoolean}){arc_taps};\n'
    else:
        return line

def patch_aff(song_dir):
    for file in os.listdir(song_dir):
        if file.endswith('.aff'):
            with open(f'{song_dir}/{file}', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(f'{song_dir}/{file}', 'w', encoding='utf-8') as f:
                f.writelines(map(patch_line, lines))
```