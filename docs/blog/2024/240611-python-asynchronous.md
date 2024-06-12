---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 15 min
title: 从协程、任务和 Future 入门 Python 异步 I/O
description: 本文将从协程、任务、Future 三个角度来介绍 Python 异步 I/O 的基本概念和使用方法，帮助你更好地理解 Python 异步 I/O 的工作原理。
---

!!! abstract "摘要"

    协程（Coroutine）、任务（Task）、Future 是 `asyncio` 库中定义的三种可等待对象，它们是构成异步 I/O 的基础。

    本文将从协程、任务、Future 三个角度来介绍 Python 异步 I/O 的基本概念和使用方法，帮助你更好地理解 Python 异步 I/O 的工作原理。

## 一、可等待对象与事件循环

### 1.1 前言

在入门 Python 异步 I/O 之前，我们有必要来了解两个重要概念——可等待对象（Awaitable Object）和事件循环（Event Loop）。

异步 I/O 的绝妙之处就在于异步，当操作系统遇到 I/O 操作时，不会等待 I/O 操作完成，而是立即返回让 CPU 干其他的事，等到稍后 I/O 操作结束后再通知 CPU。这样在很大程度上提高了 CPU 的利用率。

为此我们需要引入一个 “可等待对象” 的概念。所谓的 “可等待” 并不是指这个对象需要被谁一直等下去，而是指这个对象可以被挂起或者恢复执行。这样，当主线程遇到可等待对象的 I/O 操作时，可以立即挂起这个对象（此时它的 I/O 操作仍在继续），让主线程干其他的事，等到 I/O 操作结束后再恢复该对象的执行。

那么主线程如何去做 “其他的事” 呢？这就需要引入 “事件循环” 的概念。事件循环就像一个人，它会不断地检查所有的可等待对象，看看哪个对象已经准备好了，然后令主线程继续这个对象的执行。

### 1.2 回到 Python

可以在 `#!python await` 语句中使用的对象都是可等待对象（Awaitable）。你可以自己定义可等待对象，只要它实现了 `#!python __await__()` 魔法方法。

等待一个可等待对象，指的是对这个对象使用 `#!python await` 语句。

Python 标准库 `asyncio` 中已经预先定义了三种可等待对象：

  - 协程（Coroutine）
  - 任务（Task）
  - Future

可等待对象的调度是由事件循环（Event Loop）来完成的。事件循环会按照一定的规则调度可等待对象的执行，其调度的基本单位是任务（Task）。

所谓调度，就是将可等待对象的执行交给事件循环，由事件循环来决定何时执行、何时挂起、何时恢复。当一个可等待对象被调度时，并不总是意味着它可以立即执行。

请带着以下三个问题来阅读下面的章节：

 - 同样是异步 I/O 编程，为什么有的写法会像同步编程一样阻塞，为什么有的写法却可以并发？
 - 在等待一个可等待对象时，发生了什么？
 - 等待和调度的区别是什么？

## 二、协程

协程是可等待对象中最容易理解的一种，但是只使用协程是无法发挥异步 I/O 的全部实力的（无法异步并发）。

### 2.1 协程函数与协程对象

在 Python 中，协程有两个相关概念：

  - 协程函数（Coroutine Function）
  - 协程对象（Coroutine Object）

协程函数是使用 `#!python async def` 语法定义的函数。当这个函数被调用时，它的返回值是一个协程对象。

!!! warning "注意"
    
    协程函数依然是函数对象，依然具有函数对象的所有特性。

```python
async def coro():
    ...

type(coro)  # <class 'function'>  本身是函数
type(coro())  # <class 'coroutine'>  返回值是协程对象
```

在大多数场合，协程通常是指协程对象，因为协程对象可以直接被调度。不过，说调度一个协程函数，也并不会产生歧义，这意味着这个协程函数返回一个了协程对象，然后调度该协程对象。

### 2.2 协程的调度执行

直接调用协程函数会返回一个协程对象，而并不会使这个协程函数被调度执行。要想实际调度协程函数，你有以下几种方式：

 - 使用 `#!python asyncio.run()` 函数。通常作为执行协程最简单的方法。
   
    ```python linenums="1" hl_lines="7"
    import asyncio
   
    async def say_after(delay, what):
        await asyncio.sleep(delay)
        print(what)
   
    asyncio.run(say_after(1, 'Hello, World!'))
    ```
 
 - 使用 `#!python await` 语句等待它。这要求这行代码必须在协程函数内部。

    !!! warning "注意"

        等待一个协程，会隐式地将该协程包装成一个任务，然后调度这个任务（见 [3.1 任务和其他可等待对象的关系](#31)）。

    ```python linenums="1" hl_lines="4 8"
    import asyncio
   
    async def say_after(delay, what):
        await asyncio.sleep(delay)
        print(what)
   
    async def main():
        await say_after(1, 'Hello, World!')
   
    asyncio.run(main())
    ```
 
 - 使用 `#!python asyncio.create_task()` 或者 `#!python asyncio.ensure_future()` 函数。这会将协程包装为 `#!python Task` 对象，并立即调度。这要求你的代码在一个事件循环中执行。

    这种方法使用较为特殊，稍后将在 [3.2 任务的创建与调度](#32) 中详细介绍。

    !!! warning "注意"
    
        `#!python loop.run_until_complete()` 本质上就是调用了 `#!python asyncio.ensure_future()`，属于这里的第三种调度方法。

在所有的这些方式中，协程函数都被调用，并返回了一个协程对象。因此在所有的调度方式中，你都可以先生成协程对象，然后稍后再调度这个对象：

```python linenums="1" hl_lines="8 9 10"
import asyncio

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

coro = say_after(1, 'Hello, World!')

pass

asyncio.run(coro)
```

### 2.3 协程的挂起

等待协程函数会使协程函数挂起，直到 `#!python await` 语句中的可等待对象执行完毕。

```python linenums="1"
import asyncio

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)
    
async def main():
    await say_after(1, 'Hello')
    await say_after(2, 'World')

asyncio.run(main())
```

像这样只使用协程，不使用任务的写法就是异步阻塞，这和同步编程中的函数调用是类似的。

尽管事件循环可以挂起当前任务从而使主线程去处理另外的任务，但在这种写法下，事件循环中的所有任务都存在依赖关系，因为这些任务全部是由存在调用关系的协程包装而来的（见 [3.1 任务和其他可等待对象的关系](#31)）。

因此事件循环无法切换至其他任何任务，只能当前任务执行完毕，并按照调用关系逐个完成任务（见 [3.3 任务的并发执行](#33)）。

上面这段代码一共需要等待 3 秒钟才能执行完毕。

### 2.4 协程的返回值

三种调度方式，除了 `#!python asyncio.create_task()` 函数较为复杂外，获取返回值的写法都很简单：

```python linenums="1" hl_lines="7 9"
import asyncio

async def return_1():
    return 1

async def coro():
    return await return_1()  # 以 await 语句作为右值获取返回值

result = asyncio.run(coro())  # 直接获取 asyncio.run 的返回值
```

!!! warning "注意"

    若需要对等待后的返回值执行 `#!python __getitem__()` 或 `#!python __getattr__()` 等操作，你需要把整个 `#!python await` 语句用括号括起来：

    ```python hl_lines="2"
    async with Client() as client:
        result = (await client.get('http://example.com')).json()
    ```

    ```python hl_lines="3"
    async with ClientSession() as session:
        async with session.get('http://example.com') as response:
            data = (await response.json())['data']
    ```

## 三、任务

如果只在协程层面进行异步 I/O 编程，那么每当协程被挂起时，事件循环都将被阻塞，直到这个协程恢复执行或执行完毕。

这样和同步编程没有任何区别，在异步编程中不能并发地执行代码，这是毫无意义的。

于是引入了任务（Task）这一概念。将协程包装成任务后，便可以在事件循环中并发地调度这些协程。因此，任务也是事件循环调度的基本单位。

### 3.1 任务和其他可等待对象的关系

任务与其他可等待对象关系密切，理解了任务的概念，就能更好地理解其他可等待对象。

当一个协程被等待时，事件循环会将这个协程隐式地包装为一个任务对象，然后调度这个任务对象。此外，当使用协程作为 `#!python loop.run_until_complete()` 或 `#!python asyncio.run()` 等函数的实参时，这些函数会自动将协程隐式包装为任务对象。

Task 是 Future 的子类，因此他们的很多用法基本相同（例如回调）。

`asyncio` 库中的一些基本函数是接收 Future 对象作为参数的，因此你可以也将任务对象传递给这些函数。同理，如果你将协程传递给这些函数，它们可能会自动将协程包装为任务对象。

### 3.2 任务的创建与调度

你可以使用 `#!python asyncio.create_task()` 或 `#!python asyncio.ensure_future()` 函数来创建一个任务。这个函数接受一个协程对象作为参数，并返回一个任务对象，然后调度这个任务对象。

```python linenums="1" hl_lines="8"
import asyncio

async def my_coroutine():
    await asyncio.sleep(1)
    print('Hello, World!')

async def main():
    task = asyncio.create_task(my_coroutine())  # 创建并调度任务对象
    await task  # 等待任务对象

asyncio.run(main())
```

!!! warning "注意"

    任务对象的创建和调度必须依赖事件循环，因此你必须在一个事件循环中运行这段代码，故一般将 `#!python asyncio.create_task()` 函数写在协程函数中。

!!! warning "注意"

    任务对象的创建和调度是同时的，即 `#!python asyncio.create_task()` 函数会立即调度任务对象，但不意味着事件循环会立即执行这个任务对象。
    
    事件循环会自动分析所有被调度任务之间的依赖关系，并在适当的时机执行特定的任务对象。

### 3.3 任务的并发执行

```python
import asyncio

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    task1 = asyncio.create_task(say_after(1, 'Hello'))
    task2 = asyncio.create_task(say_after(2, 'World'))

    result1 = await task1
    result1 = await task2

asyncio.run(main())
```

在上面这个例子中，创建并调度了两个任务，在任何一个 `#!python await` 语句之前，事件循环都不会开始执行任何任务。

在遇到第一个 `#!python await` 语句之后，事件循环开始调度所有任务，这两个任务被并发执行。

执行的结果是，1 秒钟后打印出 `Hello`，再过 1 秒钟后打印出 `World`。可见这两个任务是并发执行的。

!!! warning "注意"

    这里值得注意的是，即使没有第二个 `#!python await` 语句，第二个任务也会被执行，见 [3.4 任务的等待](#34)。

!!! tips "提示"

    一般来说，通过 `#!python asyncio.create_task()` 函数创建的任务，相互之间都是独立的，它们一般都可以在事件循环中并发执行。

    而通过 `#!python await` 语句从协程隐式包装的任务，相互之间都是有依赖关系的，类似于函数调用关系，因此他们之间通常无法并发执行。

    像上面这个例子，事件循环发现两个任务之间没有依赖关系，因此就会开始并发地执行这两个任务。

    而 [2.3 协程的挂起](#23) 中的例子，事件循环发现全部的任务之间都有依赖关系，因此就会按照调用关系逐个执行这些任务。

如果需要并发执行大量任务，除了使用 `#!python for` 循环逐个等待以外，还可以使用 `#!python asyncio.gather()` 函数：

```python linenums="1" hl_lines="11"
import asyncio

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    task1 = asyncio.create_task(say_after(1, 'Hello'))
    task2 = asyncio.create_task(say_after(2, 'World'))

    result = await asyncio.gather(task1, task2)

asyncio.run(main())
```

`#!python asyncio.gather()` 函数返回了一个 Future 对象（见 [4.1 Future 表示异步操作的最终结果](#41)），这个对象表示了所有任务的结果。

在使用 `#!python await` 语句等待该 Future 后，Future 对象会等待所有任务执行完毕，并将结果作为一个 `#!python list` 返回。

`#!python asyncio.gather()` 函数也可以直接接收协程对象作为参数：

```python linenums="1" hl_lines="9 10"
import asyncio

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    await asyncio.gather(
       say_after(1, 'Hello'),
       say_after(2, 'World')
    )

asyncio.run(main())
```

这段代码与上面那段代码是等价的。当使用协程对象作为实参时，`#!python asyncio.gather()` 会将协程隐式地包装为任务，并调度。

### 3.4 任务的等待

当你等待一个任务时，意味着你期望获取这个任务的**结果**。因此事件循环会确保这个任务执行完毕，然后将结果保存到任务对象中，从而允许你使用 `#!python await` 语句获取这个结果。

在任务的等待中，有三个值得注意的方面非常容易被新手忽略：

第一，即使不等待任务，任务也可能被执行。

```python linenums="1" hl_lines="12"
import asyncio

async def say_after(delay, what):
    print(f'waiting {delay}s ...')
    await asyncio.sleep(delay)
    print(what)

async def main():
    task1 = asyncio.create_task(say_after(1, 'Hello'))
    task2 = asyncio.create_task(say_after(2, 'World'))

    result1 = await task1

asyncio.run(main())
```

运行结果：

```
waiting 1s ...
waiting 2s ...
Hello
```

任务什么时候开始执行，是由事件循环决定的，而不是由它在哪一行被等待决定的（它甚至可能没有被等待！）。当一个任务被创建时，它就处于被调度的状态，随时可以被事件循环执行。

上面这段代码，虽然只等待了 `#!python task1`，但是控制台依然同时打印出了 `waiting 1s ...` 和 `waiting 2s ...`。这意味着 `#!python task2` 有被实际执行，且执行时机与 `#!python task1` 一致。

第二，若不等待任务，任务可能会被取消。

还是刚刚上面那段代码，控制台虽然打印出了 `waiting 2s ...`，但却没有打印出后续理应出现的 `World`。这说明 `#!python task2` 没被执行完。

这是因为事件循环可以知道你想要获取哪些任务的结果（取决于你等待了哪些任务），若你等待的任务全部执行完毕，那么事件循环会关闭。

`#!python task2` 需要 2 秒才能执行完毕，而此时只过了 1 秒钟事件循环便关闭了，此时 `#!python task2` 会被取消（执行 `#!python Task.cancel()` 方法）。如果你熟悉任务相关操作，你可以尝试为 `#!python task2` 添加回调函数从而证实它被取消。

如果我们将代码改成这样：

```python linenums="1" hl_lines="10"
import asyncio

async def say_after(delay, what):
    print(f'waiting {delay}s ...')
    await asyncio.sleep(delay)
    print(what)

async def main():
    task1 = asyncio.create_task(say_after(1, 'Hello'))
    task2 = asyncio.create_task(say_after(0.5, 'World'))

    result1 = await task1

asyncio.run(main())
```

这样即便只等待了 `#!python task1`，但仍然打印出了 `World`。可见 `#!python task2` 因为执行时间只需要 0.5 秒，赶在事件循环关闭之前执行完了。不过显然 `World` 的打印时间早于 `Hello`。

第三，注意对应协程函数中有无等待。

如果任务对应的协程函数中没有等待，即不包含 `#!python await` 语句，那么即使没有等待该任务，事件循环也会立即执行这个任务对象。

相反，如果对应的协程函数中包含 `#!python await` 语句，那么该任务必须被等待，否则这个任务永远不会被执行。

```python linenums="1" hl_lines="7"
import asyncio

async def coro():
    print('Hello, World!')

async def main():
    task = asyncio.create_task(coro())  # 将直接打印，无需 await task

asyncio.run(main())
```

### 3.5 任务的回调函数

可以为每个任务添加回调函数，当任务执行完毕或被取消后，回调函数会被调用。

它的用法和 Future 对象的回调函数一样，请参考 [4.2 Future 的回调函数](#42-future)

## 四、Future

Future 是一种特殊的**低层级**可等待对象，表示一个异步操作的**最终结果**。这通常是由库和框架开发者来创建和使用的，不要面向用户的接口暴露 Future 对象。

在底层异步 I/O 编程中，Future 同协程、任务关系不大，它主要是为了模拟 `#!python concurrent.futures.Future` 类在底层上实现真正的并行。

### 4.1 Future 表示异步操作的最终结果

当一个 Future 对象被等待时，它的结果可能还没有准备好，也有可能已经准备好了。开发者应主动使用 `#!python set_result()` 方法来为该 Future 对象设置结果。

下面是三个例子，根据其结果有没有准备好，Future 对象在被等待时有着不同的表现：

```python linenums="1" hl_lines="10 14"
import asyncio

def set_future_result(future):
    print('Setting future result...')
    future.set_result('Hello, World!')

async def main():
    future = asyncio.Future()

    set_future_result(future)  # 先设置结果
    
    await asyncio.sleep(1)

    print(await future)  # 然后等待

asyncio.run(main())
```

在上面这个例子中，Future 对象在被等待之前就已经设置了结果，因此在等待时，它的结果已经准备好了。因此执行的结果应该是先打印出 `Setting future result...`，1 秒钟后再打印出 `Hello, World!`。

```python linenums="1" hl_lines="6"
import asyncio

async def main():
    future = asyncio.Future()

    print(await future)  # 不设置结果直接等待

asyncio.run(main())
```

在上面这个例子中，没有任何代码为 Future 对象设置结果，因此在等待时会一直等下去，程序和事件循环永远不会结束。

```python linenums="1" hl_lines="10 12"
import asyncio

def set_future_result(future):
    print('Setting future result...')
    future.set_result('Hello, World!')

async def main():
    future = asyncio.Future()

    asyncio.get_running_loop().call_later(1, set_future_result,future)  # 1 秒钟后再设置结果

    print(await future)  # 等待

asyncio.run(main())
```

在上面这个例子中，我们将 `#!python set_future_result()` 交由事件循环调度，并使用 `#!python loop.call_later()` 方法令其在 1 秒钟后执行。因此 Future 对象在被等待时，其结果还没有准备好，程序将会等待。

1 秒钟后，`#!python set_future_result()` 函数被调度执行，Future 对象的结果被设置，程序继续执行，打印出 `Setting future result...` 和 `Hello, World!`。

### 4.2 Future 的回调函数

在异步 I/O 编程中，Future 对象通常用于支持底层回调式代码。即在 Future 对象获取结果或者被取消后，调用该回调函数：

```python linenums="1" hl_lines="12 13"
import asyncio

def callback1(future):
    print('Callback1:', future.result())

def callback2(future):
    print('Callback2:', future.result())
    
async def main():
    future = asyncio.Future()

    future.add_done_callback(callback1)
    future.add_done_callback(callback2)
    
    future.set_result('Hello, World!')

asyncio.run(main())
```

在上面这个例子中，Future 对象被要求完成后调用 `#!python callback1()` 和 `#!python callback2()` 两个回调函数。

回调函数不能是协程函数，如果你想在回调函数中执行异步操作，你需要使用 `#!python asyncio.create_task()` 函数：

```python linenums="1" hl_lines="8"
import asyncio

async def coroutine_func():
    print("Coroutine callback function is running.")

def callback(future):
    print("Callback function is running.")
    asyncio.get_running_loop().create_task(coroutine_func())

async def main():
    future = asyncio.Future()
    
    future.add_done_callback(callback)
    
    future.set_result('Hello, World!')

asyncio.run(main())
```

!!! warning "注意"

    回调函数将会在 Future 对象被设置结果后执行，而不是在 Future 对象被等待时执行。

    等待 Future 和回调函数都可以获取 Future 对象的结果。但是等待 Future 会阻塞事件循环，直到 Future 对象的结果准备好，而回调函数是在 Future 对象的结果准备好后才会被调用，因此不会阻塞事件循环。

### 4.3 Future 的等待

同一个 Future 对象可以被多次等待，但它们的结果将是相同的。因为 Future 对象表示的是一个异步操作的最终结果，而不是异步操作本身。

```python linenums="1" hl_lines="12-15"
import asyncio
from random import randint

def set_future_result(future):
    future.set_result(randint(0, 100))

async def main():
    future = asyncio.Future()

    set_future_result(future)

    print(await future)
    print(await future)
    print(await future)
    print(await future)

asyncio.run(main())
```

在上面这个例子中，尽管 Future 对象的结果由 `#!python randint(0, 100)` 随机生成，但是在等待时，4 次打印的结果都是相同的。
