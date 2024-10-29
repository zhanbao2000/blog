---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 5 min
tags:
    - python
    - venv
    - pycharm
    - pip
title: 移动 python 项目文件夹位置后如何解决 PyCharm 找不到解释器与无法正常使用终端的问题
---

## 背景

因为项目需要，将部分 python 项目移动到了其他文件夹，导致在 PyCharm 中找不到解释器，也无法正常使用终端。

## 现象

我使用的 IDE 是 `PyCharm 专业版 2021.3.2`，具体表现为在 IDE 内打开终端后：

 - PyCharm 找不到解释器
 - 终端内执行 python 程序只能够使用全局包
 - 无法进入 venv 环境（包括 PyCharm 自动进入和手动进入）
 - 无法使用 pip

## 解决

### 找不到解释器

这个问题好解决，PyCharm 会自动检测当前目录下的 venv 文件夹，如果存在，则会将 `venv/Scripts/python` 设置为解释器。问题直接解决。

需要注意的是，因为我们是移动了 python 项目文件夹的，因此原来的解释器路径还保留在 PyCharm 内，所以需要手动将其删除。可以按照以下步骤进行操作：

找到 `文件` -> `设置` -> `项目` -> `Python 解释器`

选择当前解释器右边的齿轮图标，点击 `全部显示`，找到红色标记的解释器，点击删除即可。

### 无法新建解释器

在你移动了项目文件夹（甚至重装了 venv 对应的 Python 基本解释器）的情况下，可能会导致 PyCharm 无法新建同名解释器，具体体现为：

 - 使用原解释器名称和基本解释器版本新建解释器，PyCharm 只会在目标文件夹创建 `venv` 文件夹，但并未在解释器列表里添加这个新增的解释器。而且无论如何用什么添加方法都无法添加。
 - 为项目设置成 `无解释器`，此时 PyCharm 会自动检测到项目文件夹下的 `venv` 文件夹，会询问你是否要将这个 `venv` 设置为解释器。
 - 上述操作可以将 `venv` 设置为解释器，但是解释器名称会变成 `f'{原解释器名称}(2)'`，看起来是和原解释器冲突了。
 - 删除 `venv` 文件夹，使用不同的解释器名称（或者解释器版本）新建解释器，PyCharm 会正常添加。

总结一句话就是，不能和原来的解释器名称以及解释器版本冲突，两者不能同时都和旧解释器一样。

解决方法也很简单：

找到 `C:\Users\AkibaArisa\AppData\Roaming\JetBrains\PyCharm2024.2\options\jdk.table.xml` 文件，删除里面的旧解释器即可。

### 终端只能够使用全局包与无法进入 venv 环境

具体有以下几个表现：

 1. 自己的实际项目中有第三方库（例如 `aiohttp`），项目文件直接右键运行可以正常执行，但是在终端里面执行时会报错，提示 `ModuleNotFoundError: No module named 'aiohttp'`。

 2. 终端里直接执行 `where python` 显示的是全局 python 路径，而不是 venv 中的路径。

 3. 终端里直接执行 `pip list` 会提示只有 `pip` 和 `setuptools` 两个包，而我们项目里依赖的包一个都没有。

原因在于 PyCharm 自动进入 venv 环境的时候是从 `venv/Scripts/activate.bat` 进入的，这个文件定义了 `%PATH%`，当我们已经移动了项目文件夹后，`activate.bat` 里记录的路径并没有改，而原来的路径已经不存在了，所以我们放在 `venv` 下的 `python.exe` 并不会自动进入到 `%PATH%` 中。

解决方式很简单，直接编辑 `venv/Scripts/activate.bat` 文件，linux 同理。

=== "CMD"

    ```bat title="activate.bat" linenums="1" hl_lines="3"
    @echo off
    
    set "VIRTUAL_ENV=I:\Developer\web\blog_mkdocs\venv"
    
    if defined _OLD_VIRTUAL_PROMPT (
        set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
    ) else (
        if not defined PROMPT (
            set "PROMPT=$P$G"
        )
        if not defined VIRTUAL_ENV_DISABLE_PROMPT (
            set "_OLD_VIRTUAL_PROMPT=%PROMPT%"
        )
    )
    if not defined VIRTUAL_ENV_DISABLE_PROMPT (
        set "ENV_PROMPT="
        if NOT DEFINED ENV_PROMPT (
            for %%d in ("%VIRTUAL_ENV%") do set "ENV_PROMPT=(%%~nxd) "
        )
        )
        set "PROMPT=%ENV_PROMPT%%PROMPT%"
    )
    
    REM Don't use () to avoid problems with them in %PATH%
    if defined _OLD_VIRTUAL_PYTHONHOME goto ENDIFVHOME
        set "_OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%"
    :ENDIFVHOME
    
    set PYTHONHOME=
    
    REM if defined _OLD_VIRTUAL_PATH (
    if not defined _OLD_VIRTUAL_PATH goto ENDIFVPATH1
        set "PATH=%_OLD_VIRTUAL_PATH%"
    :ENDIFVPATH1
    REM ) else (
    if defined _OLD_VIRTUAL_PATH goto ENDIFVPATH2
        set "_OLD_VIRTUAL_PATH=%PATH%"
    :ENDIFVPATH2
    
    set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"
    ```

=== "Bash"

    ```bash title="activate" linenums="1" hl_lines="47"
    # This file must be used with "source bin/activate" *from bash*
    # you cannot run it directly
    
    
    if [ "${BASH_SOURCE-}" = "$0" ]; then
        echo "You must source this script: \$ source $0" >&2
        exit 33
    fi
    
    deactivate () {
        unset -f pydoc >/dev/null 2>&1 || true
    
        # reset old environment variables
        # ! [ -z ${VAR+_} ] returns true if VAR is declared at all
        if ! [ -z "${_OLD_VIRTUAL_PATH:+_}" ] ; then
            PATH="$_OLD_VIRTUAL_PATH"
            export PATH
            unset _OLD_VIRTUAL_PATH
        fi
        if ! [ -z "${_OLD_VIRTUAL_PYTHONHOME+_}" ] ; then
            PYTHONHOME="$_OLD_VIRTUAL_PYTHONHOME"
            export PYTHONHOME
            unset _OLD_VIRTUAL_PYTHONHOME
        fi
    
        # The hash command must be called to get it to forget past
        # commands. Without forgetting past commands the $PATH changes
        # we made may not be respected
        hash -r 2>/dev/null
    
        if ! [ -z "${_OLD_VIRTUAL_PS1+_}" ] ; then
            PS1="$_OLD_VIRTUAL_PS1"
            export PS1
            unset _OLD_VIRTUAL_PS1
        fi
    
        unset VIRTUAL_ENV
        if [ ! "${1-}" = "nondestructive" ] ; then
        # Self destruct!
            unset -f deactivate
        fi
    }
    
    # unset irrelevant variables
    deactivate nondestructive
    
    VIRTUAL_ENV='I:\Developer\web\blog_mkdocs\venv'
    if ([ "$OSTYPE" = "cygwin" ] || [ "$OSTYPE" = "msys" ]) && $(command -v cygpath &> /dev/null) ; then
        VIRTUAL_ENV=$(cygpath -u "$VIRTUAL_ENV")
    fi
    export VIRTUAL_ENV
    
    _OLD_VIRTUAL_PATH="$PATH"
    PATH="$VIRTUAL_ENV/Scripts:$PATH"
    export PATH
    
    # unset PYTHONHOME if set
    if ! [ -z "${PYTHONHOME+_}" ] ; then
        _OLD_VIRTUAL_PYTHONHOME="$PYTHONHOME"
        unset PYTHONHOME
    fi
    
    if [ -z "${VIRTUAL_ENV_DISABLE_PROMPT-}" ] ; then
        _OLD_VIRTUAL_PS1="${PS1-}"
        if [ "x" != x ] ; then
            PS1="${PS1-}"
        else
            PS1="(`basename \"$VIRTUAL_ENV\"`) ${PS1-}"
        fi
        export PS1
    fi
    
    # Make sure to unalias pydoc if it's already there
    alias pydoc 2>/dev/null >/dev/null && unalias pydoc || true
    
    pydoc () {
        python -m pydoc "$@"
    }
    
    # The hash command must be called to get it to forget past
    # commands. Without forgetting past commands the $PATH changes
    # we made may not be respected
    hash -r 2>/dev/null
    ```

=== "FishShell"

    ```fish title="activate.fish" linenums="1" hl_lines="60"
    # This file must be used using `source bin/activate.fish` *within a running fish ( http://fishshell.com ) session*.
    # Do not run it directly.
    
    function _bashify_path -d "Converts a fish path to something bash can recognize"
        set fishy_path $argv
        set bashy_path $fishy_path[1]
        for path_part in $fishy_path[2..-1]
            set bashy_path "$bashy_path:$path_part"
        end
        echo $bashy_path
    end
    
    function _fishify_path -d "Converts a bash path to something fish can recognize"
        echo $argv | tr ':' '\n'
    end
    
    function deactivate -d 'Exit virtualenv mode and return to the normal environment.'
        # reset old environment variables
        if test -n "$_OLD_VIRTUAL_PATH"
            # https://github.com/fish-shell/fish-shell/issues/436 altered PATH handling
            if test (echo $FISH_VERSION | head -c 1) -lt 3
                set -gx PATH (_fishify_path "$_OLD_VIRTUAL_PATH")
            else
                set -gx PATH "$_OLD_VIRTUAL_PATH"
            end
            set -e _OLD_VIRTUAL_PATH
        end
    
        if test -n "$_OLD_VIRTUAL_PYTHONHOME"
            set -gx PYTHONHOME "$_OLD_VIRTUAL_PYTHONHOME"
            set -e _OLD_VIRTUAL_PYTHONHOME
        end
    
        if test -n "$_OLD_FISH_PROMPT_OVERRIDE"
           and functions -q _old_fish_prompt
            # Set an empty local `$fish_function_path` to allow the removal of `fish_prompt` using `functions -e`.
            set -l fish_function_path
    
            # Erase virtualenv's `fish_prompt` and restore the original.
            functions -e fish_prompt
            functions -c _old_fish_prompt fish_prompt
            functions -e _old_fish_prompt
            set -e _OLD_FISH_PROMPT_OVERRIDE
        end
    
        set -e VIRTUAL_ENV
    
        if test "$argv[1]" != 'nondestructive'
            # Self-destruct!
            functions -e pydoc
            functions -e deactivate
            functions -e _bashify_path
            functions -e _fishify_path
        end
    end
    
    # Unset irrelevant variables.
    deactivate nondestructive
    
    set -gx VIRTUAL_ENV 'I:\Developer\web\blog_mkdocs\venv'
    
    # https://github.com/fish-shell/fish-shell/issues/436 altered PATH handling
    if test (echo $FISH_VERSION | head -c 1) -lt 3
       set -gx _OLD_VIRTUAL_PATH (_bashify_path $PATH)
    else
        set -gx _OLD_VIRTUAL_PATH "$PATH"
    end
    set -gx PATH "$VIRTUAL_ENV"'/Scripts' $PATH
    
    # Unset `$PYTHONHOME` if set.
    if set -q PYTHONHOME
        set -gx _OLD_VIRTUAL_PYTHONHOME $PYTHONHOME
        set -e PYTHONHOME
    end
    
    function pydoc
        python -m pydoc $argv
    end
    
    if test -z "$VIRTUAL_ENV_DISABLE_PROMPT"
        # Copy the current `fish_prompt` function as `_old_fish_prompt`.
        functions -c fish_prompt _old_fish_prompt
    
        function fish_prompt
            # Run the user's prompt first; it might depend on (pipe)status.
            set -l prompt (_old_fish_prompt)
    
            # Prompt override provided?
            # If not, just prepend the environment name.
            if test -n ''
                printf '%s%s' '' (set_color normal)
            else
                printf '%s(%s) ' (set_color normal) (basename "$VIRTUAL_ENV")
            end
    
            string join -- \n $prompt # handle multi-line prompts
        end
    
        set -gx _OLD_FISH_PROMPT_OVERRIDE "$VIRTUAL_ENV"
    end
    ```

=== "Xonsh"

    ```xsh title="activate.xsh" linenums="1" hl_lines="31"
    """Xonsh activate script for virtualenv"""
    from xonsh.tools import get_sep as _get_sep
    
    def _deactivate(args):
        if "pydoc" in aliases:
            del aliases["pydoc"]
    
        if ${...}.get("_OLD_VIRTUAL_PATH", ""):
            $PATH = $_OLD_VIRTUAL_PATH
            del $_OLD_VIRTUAL_PATH
    
        if ${...}.get("_OLD_VIRTUAL_PYTHONHOME", ""):
            $PYTHONHOME = $_OLD_VIRTUAL_PYTHONHOME
            del $_OLD_VIRTUAL_PYTHONHOME
    
        if "VIRTUAL_ENV" in ${...}:
            del $VIRTUAL_ENV
    
        if "VIRTUAL_ENV_PROMPT" in ${...}:
            del $VIRTUAL_ENV_PROMPT
    
        if "nondestructive" not in args:
            # Self destruct!
            del aliases["deactivate"]
    
    
    # unset irrelevant variables
    _deactivate(["nondestructive"])
    aliases["deactivate"] = _deactivate
    
    $VIRTUAL_ENV = r"I:\Developer\web\blog_mkdocs\venv"
    
    $_OLD_VIRTUAL_PATH = $PATH
    $PATH = $PATH[:]
    $PATH.add($VIRTUAL_ENV + _get_sep() + "Scripts", front=True, replace=True)
    
    if ${...}.get("PYTHONHOME", ""):
        # unset PYTHONHOME if set
        $_OLD_VIRTUAL_PYTHONHOME = $PYTHONHOME
        del $PYTHONHOME
    
    $VIRTUAL_ENV_PROMPT = ""
    if not $VIRTUAL_ENV_PROMPT:
        del $VIRTUAL_ENV_PROMPT
    
    aliases["pydoc"] = ["python", "-m", "pydoc"]
    ```

### 无法使用 pip

通过修改 `activate.bat` 使得能正常进入 venv 环境后，会迎来第三个问题，就是无法使用 pip 安装包。

具体表现为，使用 `pip` 命令后，终端会报错：`Fatal error in launcher: unable to create process using: 'XXXXXXX/python.exe' 'XXXXXXXXX/pip.exe'`。

我一看，这个所谓的 `'XXXXXXX/python.exe'` 正是我们在移动项目文件之前的 venv 的 python 路径，可是我们已经修改了 `activate.bat` 中的路径，怎么还是会出现这个问题呢。

参考了 [Fatal error in launcher: Unable to create process using](https://blog.csdn.net/FY_2018/article/details/110204630) 这篇文章，了解到 `pip.exe` 同样也保存了路径，而且就保存在 `pip.exe` 这个二进制文件里，如果想要修改也不是不行，用 `WinHex` 这类工具改就行。

但是我们没必要这么麻烦，我的建议是直接原地重装 `pip`，步骤如下：

 1. 首先有了上一步的铺垫，我们已经能够进入 venv，那么进入 venv

    ```bat
    I:\Developer\web\blog_mkdocs\venv\Scripts\activate.bat
    ```

 2. 然后重装 `pip`（注意此时你已经在 venv 里了）

    ```bat
    python -m pip install --upgrade --force-reinstall pip
    ```

此时，该 venv 里的 `pip` 应该可以正常使用。

同理，继续检查 `venv/Scripts` 下的其他二进制文件，例如 `mkdocs.exe`，这些都要通过相同方式重装才能正常用。

```bat
pip install --upgrade --force-reinstall mkdocs
```
