---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 20 min
tags:
    - python
title: Python 个人代码风格指导
description: 这是一篇简要的 Python 代码风格指导，代表了我个人所倾向的代码风格。使用这些风格可以让你的代码看起来更 Pythonic，更精炼地描述你代码所作的工作，或许也可以减轻你的重构压力。
---

!!! abstract "摘要"

    这是一篇简要的 Python 代码风格指导，代表了我个人所倾向的代码风格。使用这些风格可以让你的代码看起来更 Pythonic，更精炼地描述你代码所作的工作，或许也可以减轻你的重构压力。

    每个人的风格可能大同小异，也有可能大相径庭，写在这里并不代表我的就是最好的。我所希望的是，读者阅读完此篇文章后能够有所启发，或是发现自己从未使用过的优雅方法，或是改善自己从未意识到的丑陋写法，如此一来我就已经很满足了。

    这里面的很多示例代码（包括坏代码）来源于我修改自己的代码而得出的经验与风格，我也正是在修改并美化这些代码的过程中产生了写这么一篇文章的想法。

## 一、绪论

### 1.1 Python 之禅：`#!python import this`

Python之禅最早由 Tim Peters 在 Python [邮件列表](https://mail.python.org/pipermail/python-list/1999-June/001951.html) 中发表，它包含了影响 Python 编程语言设计的19条软件编写原则。

```python
import this
```

=== "英文版 🇬🇧"

    ``` linenums="1"
    Beautiful is better than ugly.
    Explicit is better than implicit.
    Simple is better than complex.
    Complex is better than complicated.
    Flat is better than nested.
    Sparse is better than dense.
    Readability counts.
    Special cases aren't special enough to break the rules.
    Although practicality beats purity.
    Errors should never pass silently.
    Unless explicitly silenced.
    In the face of ambiguity, refuse the temptation to guess.
    There should be one-- and preferably only one --obvious way to do it.
    Although that way may not be obvious at first unless you're Dutch.
    Now is better than never.
    Although never is often better than *right* now.
    If the implementation is hard to explain, it's a bad idea.
    If the implementation is easy to explain, it may be a good idea.
    Namespaces are one honking great idea -- let's do more of those!
    ```

=== "中文版 🇨🇳"

    ``` linenums="1"

    ``` linenums="1"
    优美优于丑陋
    明了优于隐晦
    简单优于复杂
    复杂优于繁杂
    扁平优于嵌套
    稀疏优于稠密
    可读性很重要
    特例亦不可违背原则
    即使实用比纯粹更优
    错误绝不能悄悄忽略
    除非它明确需要如此
    面对不确定性，拒绝妄加猜测
    任何问题应有一种，且最好只有一种，显而易见的解决方法
    尽管这方法一开始并非如此直观（除非你是荷兰人）
    做优于不做
    然而不假思索还不如不做
    很难解释的，必然是坏方法
    很好解释的，可能是好方法
    命名空间是个绝妙的主意，我们应好好利用它
    ```

### 1.2 PEP-8

[PEP-8](https://www.python.org/dev/peps/pep-0008/) 全称 `PEP 8 – Style Guide for Python Code`，它给出了构成 Python 主发行版中标准库的 Python 代码的编码规范。

遵守 PEP-8 是一个很好的习惯，它并不是一个必须的规范。然而我自己的建议是：

***无论在任何情况下，都请遵守 PEP-8 规范***。

PEP-8 可以让你的代码看起来更规范，更简洁，更易读。尤其是统一的格式，更容易被人阅读。

一些 IDE（例如 PyCharm）可以自动标记你代码中不遵守 PEP-8 的情况。除此以外，你也可以通过以下方式来检查你的代码是否遵守了 PEP-8 规范：

```bash
python -m pep8 --statistics my_file.py
```

~~习惯性遵守 PEP-8 可能会让您变成 PEP-8 的受害者，导致您使用其他语言时仍然保留了 PEP-8 中的习惯，尽管这些语言中并没有类似的要求。~~

## 二、该使用什么

### 2.1 使用合适的对象作为数据结构

Python 中有多种对象——列表、字典、集合、元组和字符串，以下是对比：

|     | 元素可重复 | 元素可追加 | 对象可哈希 | 元素可索引 |
|-----|:-----:|:-----:|:-----:|:-----:|
| 列表  |  🟢   |  🟢   |  🔴   |  🟢   |
| 字典  |  🔴   |  🟢   |  🔴   |  🔴   |
| 集合  |  🔴   |  🟢   |  🔴   |  🔴   |
| 元组  |  🟢   |  🔴   |  🟢   |  🟢   |
| 字符串 |  🟢   |  🔴   |  🟢   |  🟢   |

!!! note "注："

    1. 字典的不可重复指的是，字典中的键不能重复。
    2. 是否可追加的标准是，首先这个对象可以追加新元素，其次在追加前后，使用 `#!python id()` 函数计算出的指针是否一致（即是否仍为同一个对象）。
    3. 可以使用 `#!python hash()` 函数或是 `#!python __hash__()` 魔法方法的对象视为可哈希。
    4. 由于所有的可迭代对象（上面5个都是）都可以使用 `#!python sorted()` 函数进行排序，采用这个标准来进行比较是没有意义的，所以不采用元素是否有序作为这5个对象的对比项目。
    5. 元素可索引指的是对象中的元素是否可以按顺序索引（或者说是否具有类似线性表一样的存储结构），而不是指该对象是否具有 `#!python __setitem__()` 魔法方法。

除字符串外，其余4个通常用于表示一组数据（或映射，例如字典）。以下是我总结的**在什么时候使用什么样的数据结构**：

列表（`#!python list`）-> **绝大多数情况下的最佳选择**
:   你的数据是按顺序索引的，并且需要频繁地修改、追加、删除。（换句能听懂的人话：链表）

字典（`#!python dict`）
:   你需要使用一个类似哈希表（散列表）的数据结构。

集合（`#!python set`）
:   你的数据需要频繁地追加、删除，并且你确信你可能会追加相同的数据，而这是你想要避免的。

元组（`#!python tuple`）
:   你的数据只需要定义一次，并且从不修改、追加、删除。或者当你的数据总是组队出现时（例如坐标、TCP四元组）。

~~可能此时某些人看完会钻牛角尖，非得搁这纠结什么链表和数组性能差异和实现上的不同，我已经说得很清楚了，和线性表这类东西作比较**仅仅是为了打比方**。你要这么纠结你就去用 `np.ndarray`，或者干脆别用 Python 了，直接去用你心爱的 C/C++，而不用在这纠结 Python 的几个对象。~~

### 2.2 积极使用类型注释

使用类型注释可以让你的 IDE 和其他开发者更好地阅读你的代码，并且在后期的重构时，能更大胆地进行代码复用，而无须纠结参数的类型。

!!! Example

    Good:
    ```python
    def foo(x: int, y: int) -> int:
        return x + y
    ```

    Bad:
    ```python
    def foo(x, y):
        return x + y
    ```

可以使用 `typing` 标准库来编写更高级的类型注释，例如：

!!! Example

    ```python
    from typing import TypeVar, Union
    
    RealNumeric = TypeVar('RealNumeric', int, float)
    
    def create_complex(re: RealNumeric = 0, im: RealNumeric = 0) -> Union[RealNumeric, complex]:
        return re + im * 1j
    ```

甚至使用泛型：

!!! Example

    ```python
    from typing import TypeVar

    _T = TypeVar('_T')
    
    def if_pattern(pattern: list[tuple[bool, _T]]) -> _T:
        return filter(lambda x: x[0], pattern).__next__()[1]
    ```
### 2.3 函数的功能应具有专一性

!!! Example

    Ugly:
    ```python
    def calc(const: Optional[float], rating: Optional[float], score: Optional[float]) -> float:
        if const is None:
            return calc_const(rating, score)
        if rating is None:
            return calc_rating(const, score)
        if score is None:
            return calc_score(const, rating)
        else:
            raise ValueError('Invalid input!')
    ```

请注意，这是我曾经用于计算某个🇬🇧游戏的一些数值时采用的函数写法，现在我觉得它奇丑无比。

## 三、该取代什么

### 3.1 使用**优美**的现有方法取代**丑陋**的自行实现

以判断字典中是否有某个键的方法为例：

!!! Example
    
    Good:
    
    ```python
    if 'some_key' in d:
        ...
    ```
    
    Bad:
        
    ```python
    if d.__contains__('some_key'):
        ...

    if d.has_key('some_key'):
        ...
    ```

并且请注意：事实上，`#!python dict` 类的 `#!python has_key()` 方法已经 [在 Python3 中被移除](https://docs.python.org/3.1/whatsnew/3.0.html#builtins)，所以大部分情况下你也用不着它（或者没法用它）。

由于 Python 自身的性质，使用 Python 实现一个特定的功能非常容易，但也正因为如此，有不少初学者在学习前期会使用大量的自行实现，这种自行实现又常常被称为 `重复发明轮子`。

重复发明轮子并不一无是处，对于初学者而言，这常常是一种提升自身基本能力的有效手段。然而对于并非初学者的我们，重复发明轮子已经不再有任何用途了，因此需要极力避免这种情况发生。

一般来说，选择具体的实现方法时，考虑以下优先顺序：

 - 语句、[`Builtins` 函数](https://docs.python.org/zh-cn/3/library/functions.html)
 - [魔法方法](https://rszalski.github.io/magicmethods/)、方法
 - [Python 标准库](https://docs.python.org/zh-cn/3/library/index.html)
 - 第三方库
 - 自行实现

在多种实现的复杂度相差无几时，上面排序越靠前的实现方法看起来越优雅，而越往后的实现方法看起来越丑陋。只有在你发现靠前的方法无法满足你的需求（或过于复杂）时，才有必要考虑靠后的方法。

### 3.2 使用括号换行取代换行符换行

Python 中的括号有个 [特性](https://docs.python.org/2/reference/lexical_analysis.html#implicit-line-joining)，就是括号中的表达式可以在一个行上直接分割，而无须使用 `\` 换行。

以 `#!python import` 语句为例：

!!! Example
    
    Good:
    
    ```python
    from .make_score_image import (
        moe_draw_recent, guin_draw_recent, bandori_draw_recent,
        andreal_v1_draw_recent, andreal_v2_draw_recent, andreal_v3_draw_recent, andreal_draw_b30,
        song_list, draw_b30,
    )
    ```
    
    Bad:
    
    ```python
    from .make_score_image import moe_draw_recent, guin_draw_recent, bandori_draw_recent, song_list, draw_b30, \
        andreal_v1_draw_recent, andreal_v2_draw_recent, andreal_v3_draw_recent, andreal_draw_b30
    ```

值得注意的是，在括号内进行换行后，请注意缩进。要么使用垂直缩进，要么使用悬挂缩进。

以 `#!python if` 语句为例：

!!! Example

    Good:
    
    ```python
    # 4空格悬挂缩进
    if (
        this_vid != last_vid
        or this_vid == last_vid and (
            this_lang in ['zh-Hans', 'zh']
            or this_lang == 'ja' and last_lang not in ['zh-Hans', 'zh']
            or this_lang == 'en' and last_lang not in ['zh-Hans', 'zh', 'ja']
        )
    ):
        ...

    # 使用垂直缩进
    if (this_vid != last_vid
        or this_vid == last_vid and (this_lang in ['zh-Hans', 'zh']
                                     or this_lang == 'ja' and last_lang not in ['zh-Hans', 'zh']
                                     or this_lang == 'en' and last_lang not in ['zh-Hans', 'zh', 'ja'])):
        ...
    ```

    Bad:
    
    ```python
    # 无任何缩进
    if this_vid != last_vid or this_vid == last_vid and (this_lang in ['zh-Hans', 'zh'] or this_lang == 'ja' and last_lang not in ['zh-Hans', 'zh'] or this_lang == 'en' and last_lang not in ['zh-Hans', 'zh', 'ja']):
        ...

    # 使用丑陋的 \ 进行换行
    if this_vid != last_vid or this_vid == last_vid \
        and (this_lang in ['zh-Hans', 'zh'] or this_lang == 'ja' \
             and last_lang not in ['zh-Hans', 'zh'] or this_lang == 'en' \
             and last_lang not in ['zh-Hans', 'zh', 'ja']):
        ...

    # 4空格悬挂缩进对齐到 if
    if this_vid != last_vid or this_vid == last_vid and (this_lang in ['zh-Hans', 'zh'] or this_lang == 'ja' and last_lang 
        not in ['zh-Hans', 'zh'] or this_lang == 'en' and last_lang not in 
        ['zh-Hans', 'zh', 'ja']):
        ...
    ```

以字符串的多行拼接为例：

!!! Example

    Good:

    ```python
    text = (
        f'项目：{repo.name}\n'
        f'作者：{owner}\n'
        f'大小：{repo.size} KB\n'
        f'语言：{repo.language or "无"}\n'
        f'许可证：{license_}\n'
        f'🐞:{repo.open_issues_count} ⭐:{repo.stargazers_count} 🍴:{repo.forks_count}\n'
        f'创建时间：{format_time(repo.created_at)}\n'
        f'上次提交：{format_time(repo.pushed_at)}\n'
        f'描述：{repo.description or "无"}\n'
        f'标签：{tags}'
    )
    ```

    Bad:

    ```python
    text = f'项目：{repo.name}\n' \
           f'作者：{owner}\n' \
           f'大小：{repo.size} KB\n' \
           f'语言：{repo.language or "无"}\n' \
           f'许可证：{license_}\n' \
           f'🐞:{repo.open_issues_count} ⭐:{repo.stargazers_count} 🍴:{repo.forks_count}\n' \
           f'创建时间：{format_time(repo.created_at)}\n' \
           f'上次提交：{format_time(repo.pushed_at)}\n' \
           f'描述：{repo.description or "无"}\n' \
           f'标签：{tags}'
    ```

提示：对于需要很多换行的字符串，使用 `"""` 搭配 [`textwrap.dedent()`](https://docs.python.org/zh-cn/3/library/textwrap.html#textwrap.dedent) 是**最优**的选择：

!!! Example

    ⭐**Best:**

    ```python
    import textwrap

    text = textwrap.dedent(f"""
        项目：{repo.name}
        作者：{owner}
        大小：{repo.size} KB
        语言：{repo.language or "无"}
        许可证：{license_}
        🐞:{repo.open_issues_count} ⭐:{repo.stargazers_count} 🍴:{repo.forks_count}
        创建时间：{format_time(repo.created_at)}
        上次提交：{format_time(repo.pushed_at)}
        描述：{repo.description or "无"}
        标签：{tags}
    """)
    ```

`textwrap` 是 Python 标准库之一，其中的 `dedent()` 函数可以移除 `text` 中每一行的任何相同前缀空白符。这可以用来清除三重引号字符串行左侧空格，并在源码中仍然显示为缩进格式。

## 四、该避免什么

### 4.1 避免迷惑命名

!!! cite "引用"

    改名不仅仅是修改名字而已。如果你想不出一个好名字，说明背后很可能潜藏着更深的设计问题。为一个恼人的名字所付出的纠结，常常能推动我们对代码进行精简。

    —— 《重构：改善既有代码的设计》

命名是程序员最难解决的一个问题之一，而迷惑命名将导致后期重构时无法正确理解对象的含义。

虽然我们无法做到 100% 的完美命名，使每个对象的名字都恰到好处，但是我们可以避免出现迷惑命名。一个不佳的命名可能仅仅会给阅读代码带来困难，而迷惑命名则会使我们完全混淆代码的含义。以下列举了一些迷惑命名的例子：

1. 混淆使用元素列表命名

    !!! Example
    
        ```python
        for user in user_list:
            print(user)
        ```
    
        ```python
        for user in users:
            print(user)
        ```

    `user_list` 和 `users` 都可以表示一个存储用户信息的列表。假如一个过程内同时定义了 `user_list` 和 `users`，你会怎样去区分呢？最好的方法是只使用其中的一种命名方式，而我选择的是前者（后者当然也行，但请不要混淆使用！）

2. 混淆使用下划线

    !!! Example
    
        ```python
        song_list: list[Song] = []
        songlist: dict[str, Any] = {}
        ```
    
    以上写法非常令人迷惑，`song_list` 和 `songlist` 可能都是表示某个🇬🇧游戏的歌曲列表，但是表示这个 “列表” 的数据结构却是不同的。在同一个过程内部同时使用这两个变量将会使其他开发者（甚至自己！）在调用它们时罔知所措。

    得亏这是有 typing hint 的情况，要是遇到一些没有标注 typing hint 还这样写的代码（~~例如我的早期代码~~），那就真的让人背地里想骂人了。

3. 变量名加入累赘的前/后缀

    !!! Example
    
        ```python
        user: dict[str, Any] = {}
        user_data: dict[str, Any] = {}
        user_info: dict[str, Any] = {}
        user_detail: dict[str, Any] = {}
        user_metadata: dict[str, Any] = {}
        user_information: dict[str, Any] = {}
        ```

    这种命名何止是迷惑，简直是令人恼火！假如一个过程内同时定义了 `user`、`user_data`、`user_info`、`user_detail`、`user_metadata` 和 `user_information`，如果我要获取用户的信息，请问我该调用那个变量呢？

    建议在新的变量命名之前，仔细检查已经命名过的变量，如果出现这种多个不同后缀表示同一数据的情况，则可能说明**这已经不是简单的命名问题了**。

4. 不恰当的缩写

    !!! Example

        Good:

        ```python
        def get_classifier_K_nearest_neighbors(dataset: Dataset, k: int) -> Classifier:
            ...
        ```
 
        Bad:

        ```python
        def get_classifier_KNN(dataset: Dataset, k: int) -> Classifier:
            ...
        ```
    
    `KNN` 指的是 `K-近邻算法`，是一种用于分类和回归的非参数统计方法，借由计算与已知类别案例之相似度，来评估未知类别案例可能的分类。

    使用缩写的方式，可能会使代码更加简洁，但是也会使代码更加难以理解，尤其是以上这种只有在专业领域才会用到的缩写。

5. 混淆使用自定义异常的后缀

    !!! Example

        ```python
        class PotentialHiddenError(RuntimeError):
            ...

        class PotentialHiddenException(RuntimeError):
            ...
        ```

    假设一个月前你在 `exceptions.py` 里定义了这两个异常，一个月之后你项目的其他贡献者写代码的时候需要抛出一个 “用户潜力值被隐藏” 的异常，请问该抛出谁？这种迷惑（混淆）情形和先前提到的简直是殊途同归。

    此外，需要注意的是，在 Python 中，更常用的异常的后缀是 `Error`，而不是 `Exception`。（见官方文档中的 [用户自定义异常](https://docs.python.org/zh-cn/3/tutorial/errors.html#user-defined-exceptions)）

命名的具体写法并不是该节的讨论重点，驼峰命名法、下划线命名法和匈牙利命名法的具体内容也已人尽皆知，这里便不再赘述。

具体可以参照 Python 之父 Guido 推荐的规范：

| Type                       | Public               | Internal                                                                 |
|:---------------------------|:---------------------|:-------------------------------------------------------------------------|
| Modules                    | `lower_with_under`   | `_lower_with_under`                                                      |
| Packages                   | `lower_with_under`   |                                                                          |
| Classes                    | `CapWords`           | `_CapWords`                                                              |
| Exceptions                 | `CapWords`           |                                                                          |
| Functions                  | `lower_with_under()` | `_lower_with_under()`                                                    |
| Global/Class Constants     | `CAPS_WITH_UNDER`    | `_CAPS_WITH_UNDER`                                                       |
| Global/Class Variables     | `lower_with_under`   | `_lower_with_under`                                                      |
| Instance Variables         | `lower_with_under`   | `_lower_with_under` (protected) <br/> `__lower_with_under` (private)     |
| Method Names               | `lower_with_under()` | `_lower_with_under()` (protected) <br/> `__lower_with_under()` (private) |
| Function/Method Parameters | `lower_with_under`   |                                                                          |
| Local Variables            | `lower_with_under`   |                                                                          |

和 PEP-8 一样，某些 IDE（例如 PyCharm）或者插件（例如 SonarLint）也可以自动标记你代码中不遵守上述命名法的情况。

### 4.2 避免过长的函数

如果你发现一个函数的长度超过了50行，那么大概率说明这个函数需要精简。

TODO

### 4.3 避免构造重复的函数

TODO

### 4.4 避免滥用 `#!python try except` 语句

不要懒惰到让 `#!python try except` 语句来帮你找到错误！

`#!python try except` 语句通常是用于处理错误和异常的，但这不意味着所有的错误和异常都必须经过它的手处理。如果是一些显而易见的错误，则应当避免使用 `#!python try except` 语句，而是直接消化这个可能抛出的异常。

!!! Example

    Good:

    ```python
    def get_player_name(play_record: dict[str, Any]) -> str:
        if play_record and 'name' in play_record[0]:
            return play_record[0]['name']
        else:
            return 'Unknown'
    ```

    Bad:

    ```python  
    def get_player_name(play_record: dict[str, Any]) -> str:
        try:
            return play_record[0]['name']
        except (KeyError, IndexError):
            return 'Unknown'
    ```

此举是为了明确错误的原因。以上面为例，在对一个 `#!python list` 或 `#!python dict` 反复使用 `#!python __getitem__` 时（例如有些构造复杂的 json 可能会嵌套好几层），可能会导致 `#!python KeyError` 和 `#!python IndexError` 的错误。但是简单地接住错误并不能知道具体是哪个地方调用 `#!python __getitem__` 方法时出错了，是一种晦涩的处理方法。

### 4.5 不要消化自己不该处理的错误

什么是自己不该处理的错误？

举个例子，你需要创建一个函数，它读取一个 json 文件，并将其转换为一个 `#!python dict` 对象。

那么问题来了：

 - 如果文件不存在，函数怎么办？
 - 如果文件内容不是一个 json 字符串，函数怎么办？

一些开发者可能会让该函数遇到错误时返回一个空字典，或者返回 `#!python None` 对象。我个人是很不赞同这个做法的。

第一个问题显然不是它需要关心的事情，因此如果遇到文件不存在的情况，它原则上应该照常向上抛出 `#!python FileNotFoundError` 异常，而不是私自消化掉这个异常。

第二个问题显然才是它需要关心的事，但处理方式也绝不是当作没有错误发生并返回一个空字典或是 `#!python None` 对象。正确的处理方式依然是向上抛出一个异常，这个异常可以是 `#!python RuntimeError` 或是继承自它的自定义异常。

事实上，Python 标准库中的 json 库（`#!python json.load()` 函数）便是这么做的。

 - `如果文件不存在，函数怎么办？`

    不可能在 `#!python json.load()` 函数中触发该异常，因为它并不直接读取文件，而是只使用传递到参数的文件指针，即它的第一个形参：`#!python fp: SupportsRead[str | bytes]`。

    而抛出 `#!python FileNotFoundError` 异常的函数通常是构造文件指针的函数，即 `#!python open()` 函数。

 - `如果文件内容不是一个 json 字符串，函数怎么办？`

    `#!python json.load()` 会向上抛出 `#!python json.decoder.JSONDecodeError` 异常，而绝不是私自消化它。

一个私自消化不该处理的异常的函数，就像是一个唯唯诺诺的小男孩，当受到了欺负的时候，被家长问起来也只是一问三不知，丝毫不透露自己发生了什么事情。

只有当你很明确这个函数该消化这个异常的时候，才去处理它，不该消化的时候，记得直接向上抛出！只有这样，Python 的 traceback 才能更加清晰地显示出错的原因。
