---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 10 min
tags:
    - python
title: 如何将 Python 写成文言文
---

## 绪论

俗话说得好：

!!! cite ""

    “用 Python 写程序就像是用白话写作文。”

既然如此，为何不试一试将 Python 写成文言文呢？对于一个像 Python 这样具有丰富语法糖的解释型语言来说，将其写成文言文是一件非常容易且有趣的事情。也正如某人所说：

!!! cite ""

    “（文学意义上的）文言文何尝不就是一个语法糖的合集呢？”

本篇博客的意义，便是介绍如何利用各种语法糖，将 Python 写成文言文。当然，如果你想在生产环境中用这种写法写 Python 程序，理论上也不是不行，但是你真的见过有人在自己的文章里写一大堆文言文吗？

## 写法示范

为了更好地运用语法糖，本博客涉及到的所有 Python 版本均为 Python 3.10。

### 1. 使用 `#!python filter()` 函数取代 `if-elif-else` 判断链

现代文：

```python
def calc_const(score: int | float, rating: float) -> float | None:
    if rating == 0:
        const = None
    elif score >= 1000e4:
        const = rating - 2
    elif score >= 980e4:
        const = rating - 1 - (score - 980e4) / 20e4
    elif score >= 950e4:
        const = rating - (score - 950e4) / 30e4
    else:
        const = None

    return const
```

文言文：

```python
def calc_const(score: int | float, rating: float) -> float | None:
    const_pattern: list[tuple[bool, float | None]] = [
        (rating == 0, None),  # if rating == 0: const = None
        (score >= 1000e4, rating - 2),  # elif score >= 1000e4: const = rating - 2
        (score >= 980e4, rating - 1 - (score - 980e4) / 20e4),
        (score >= 0, rating - (score - 950e4) / 30e4),
        (True, None),  # else: const = None
    ]

    return if_pattern(const_pattern)


def if_pattern(pattern: list[tuple[bool, _T]]) -> _T:
    return filter(lambda x: x[0], pattern).__next__()[1]
```

乍一看，文言文版本似乎比现代文版本更长一些，其实不然，如果我们将 `#!python if_pattern()` 函数合并到 `#!python calc_const()` 函数中，那么文言文版本就会更短一些。并且由于延长一个判断项，现代文版本需要增加两行，而文言文版本只需要一行，所以当判断链很长时，文言文版本会更短一些。

这个文言文版本的唯一缺点是，当进入 `#!python calc_const()` 函数时，需要计算 `const_pattern` 里所有布尔表达式的值，因此在性能上可能会稍稍逊色于现代文版本。

### 2. 使用 `#!python dict.get()` 方法取代 `match-case` 模式匹配

现代文：

```python
def return_relation_between_vn(relation: str) -> str:
    match relation:
        case 'seq':
            return '　续作　'
        case 'preq':
            return '　前作　'
        case 'set':
            return '同一设定'
        case 'alt':
            return '替代版本'
        case 'char':
            return '角色客串'
        case 'side':
            return '支线故事'
        case 'par':
            return '主线剧情'
        case 'ser':
            return '同一系列'
        case 'fan':
            return 'FanDisc'
        case 'orig':
            return '　原作　'
        case _:
            return '未知'
```

文言文：

```python
def return_relation_between_vn(relation: str) -> str:
    return {
        'seq': '　续作　',  # Sequel
        'preq': '　前作　',  # Prequel
        'set': '同一设定',  # Same setting
        'alt': '替代版本',  # Alternative version
        'char': '角色客串',  # Shares characters
        'side': '支线故事',  # Side story
        'par': '主线剧情',  # Parent story
        'ser': '同一系列',  # Same series
        'fan': 'FanDisc',  # Fandisc
        'orig': '　原作　',  # Original game
    }.get(relation, '未知')
```

由于 PEP 8 不允许我们将多个声明写在同一行上（`PEP 8: E701 multiple statements on one line (colon)`），故现代文版本将明显比文言文版本占据更多的行数。

在 Python 版本低于 3.10 的情况下，由于无法使用 `match-case` 模式匹配（[PEP 634: Structural Pattern Matching](https://docs.python.org/3/whatsnew/3.10.html#pep-634-structural-pattern-matching)），这将导致只能降级使用 `if-elif-else` 判断链进行链式判断。

同理，你也可以使用 `#!python dict.get()` 方法执行一些函数，例如：

```python
def extract(path: str) -> None:
    return {
        '.zip': pyzipper.ZipFile,
        '.7z': py7zr.SevenZipFile,
        '.rar': rarfile.RarFile,
    }.get(path.split('.')[-1], None).extractall(path)
```

甚至使用 `#!python lambda` 表达式作为函数：

```python
Numeric = Union[int, float, complex, np.number]

def calc(a: Numeric, b: Numeric, op: str) -> Optional[Numeric]:
    return {
        '+': lambda: a + b,
        '-': lambda: a - b,
        '*': lambda: a * b,
        '/': lambda: a / b,
        '%': lambda: a % b,
        '**': lambda: a ** b,
        '//': lambda: a // b,
    }.get(op, lambda: None)()
```

### 3. 使用 `#!python ...` 方法取代 `#!python pass` 语句

现代文：

```python
try:
    a = 1 / 0
except ZeroDivisionError:
    pass
```

文言文：

```python
try:
    a = 1 / 0
except ZeroDivisionError:
    ...
```

首先，这两段代码的效果是一模一样的。

那么，`#!python ...` 到底是个什么东西呢？可以试一试 `#!python type(...)`，你会发现它返回的是 `<class 'ellipsis'>`。这个东西的具体用途可以见 [Built-in Constants - Ellipsis](https://docs.python.org/dev/library/constants.html#Ellipsis) 或 [What does the Ellipsis object do?](https://stackoverflow.com/a/773472)

虽然看上去没有什么用，但其实 `...` 相当于一个语气词，也是某键盘手的著名名言。你可以将其放到某些特定的 `#!python except` 语句块中，表示你对抛出的这个异常十分无语。例如：

```python
try:
    result = await get_user_best35(user_id)
except (
    socket.timeout,
    aiohttp.client_exceptions.ClientConnectionError,
    aiohttp.WSServerHandshakeError,
):
    ...
```

### 4. 将 `if-else` 块改为 `if-else` 三目运算符（伪）

现代文：

```python
if a > 0:
    b = 1
else:
    b = -1
```

文言文：

```python
b = 1 if a > 0 else -1
```

这个很多人应该都知道，就不赘述了。

这和三目运算符有点相似：

```C
b = a > 0 ? 1 : -1
```

### 5. 利用 `if-else` 三目运算符处理序列

现代文：

```python
msg = 'the fox jumped over the lazy dog'
new_msg = ''

for char in msg:
    if char == ' ':
        new_msg += ' '
    else:
        # 凯撒密码
        new_msg += chr((ord(char) - ord('a') + 1) % 26 + ord('a'))
```

文言文：

```python
msg = 'the quick brown fox jumps over the lazy dog'
new_msg = ''.join(' ' if char == ' ' else chr((ord(char) - ord('a') + 1) % 26 + ord('a')) for char in msg)
```

为了叙述方便，我们把文言文里出现的 `#!python chr((ord(char) - ord('a') + 1) % 26 + ord('a'))` 这个表达式称为 `caesar(char)`，即：

```python
msg = 'the quick brown fox jumps over the lazy dog'
new_msg = ''.join(' ' if char == ' ' else caesar(char) for char in msg)
```

需要注意的是，这里需要把 `#!python ' ' if char == ' ' else caesar(char)` 看作一个整体，而不是把 `#!python caesar(char) for char in msg` 看作一个整体。也就是说，这个复杂的表达式最终是一个生成器（由 `for-in` 语句制造），而不是一个表达式（`if-else` 三目运算符）。

另外，你也可以利用 `#!python map()` 函数和 `#!python lambda` 表达式写成以下的形式：

```python
new_msg = ''.join(map(lambda char: ' ' if char == ' ' else caesar(char), msg))
```

### 6. 利用 inline 循环移除列表中的重复元素

现代文：

```python
ls = [1, 1, 1, 2, 2, 3]
while 1 in ls:
    ls.remove(1)
```

文言文：

```python
ls = [1, 1, 1, 2, 2, 3]
ls = [item for item in ls if item != 1]
```

有没有感兴趣的同学来一波性能分析？

### 7. 使用 `#!python locals()` 取代 API 请求参数列表

现代文：

```python
async def user_best(user, usercode, songname, songid, difficulty, withrecent, withsonginfo) -> dict:

    user_best_params = dict(
        user=user,
        usercode=usercode,
        songname=songname,
        songid=songid,
        difficulty=difficulty,
        withrecent=withrecent,
        withsonginfo=withsonginfo,
    )
    
    return await _request(Endpoint.V1.User.best, user_best_params)
```

文言文：

```python
async def user_best(user, usercode, songname, songid, difficulty, withrecent, withsonginfo) -> dict: return await _request(Endpoint.V1.User.best, locals())
```

这样的好处不言而喻——不用每次写 API 函数都要复读一遍参数列表。甚至非常简洁——可以一行写完这个函数。

但是缺点也很明显：在调用 `#!python locals()` 函数之前，该函数内部不能定义任何变量，否则这个新变量将加入 API 的参数列表。

!!! 题外话

    若考虑传递给 API 的参数可能为 `#!python None` 的情况，那么必须在 `_request()` 函数中清理这些 `#!python None`，如下：
    
    ```python
    clear_params = {k: v for k, v in params.items() if v is not None}
    ```

    甚至可以将其包装为一个单独的 `set_params()` 函数：

    ```python
    def set_params(**kwargs): return {k: v for k, v in kwargs.items() if v is not None}
    ```

    无论是文言文版本还是现代文版本，这都是不可避免的。
