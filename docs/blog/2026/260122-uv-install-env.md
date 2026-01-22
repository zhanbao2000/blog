---
author: Akiba Arisa
author_gh_user: zhanbao2000
tags:
    - uv
    - python
title: 使用 uv 虚拟环境时，如何替代 setup.py 安装
description: 使用 uv 虚拟环境时，因默认不带 pip 导致 `python setup.py develop` 报错，可用 `uv pip install -e .` 进行可编辑安装替代。
---

## 背景

在复现 [AnimeSR](https://github.com/TencentARC/AnimeSR) 的时候，需要执行如下命令来准备环境：

```bash
python setup.py develop
```

但是执行该命令时，报错提示：

```linenums="1" hl_lines="16"
(.venv) C:\Develop\Projects\AnimeSuperResolution\AnimeSR git:[main]
python setup.py develop
C:\Develop\Projects\AnimeSuperResolution\.venv\Lib\site-packages\setuptools\__init__.py:92: _DeprecatedInstaller: setuptools.installer and fetch_build_eggs are deprecated.
!!

        ********************************************************************************
        Requirements should be satisfied by a PEP 517 installer.
        If you are using pip, you can try `pip install --use-pep517`.

        This deprecation is overdue, please update your project and remove deprecated
        calls to avoid build errors in the future.
        ********************************************************************************

!!
  dist.fetch_build_eggs(dist.setup_requires)
C:\Develop\Projects\AnimeSuperResolution\.venv\Scripts\python.exe: No module named pip
Traceback (most recent call last):
  File "C:\Develop\Projects\AnimeSuperResolution\.venv\Lib\site-packages\setuptools\installer.py", line 121, in _fetch_build_egg_no_warn
    subprocess.check_call(cmd)
  File "C:\Develop\envs\Python\3.12\Lib\subprocess.py", line 413, in check_call
    raise CalledProcessError(retcode, cmd)
subprocess.CalledProcessError: Command '['C:\\Develop\\Projects\\AnimeSuperResolution\\.venv\\Scripts\\python.exe', '-m', 'pip', '--disable-pip-version-check', 'wheel', '--no-deps', '-w', 'C:\\Users\\AKIBAA~1\\AppData\\Local\\Temp\\tmpqop76gzt', '--quiet', 'cython']' returned non-zero exit status 1.

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Develop\Projects\AnimeSuperResolution\AnimeSR\setup.py", line 90, in <module>
    setup(
  File "C:\Develop\Projects\AnimeSuperResolution\.venv\Lib\site-packages\setuptools\__init__.py", line 114, in setup
    _install_setup_requires(attrs)
  File "C:\Develop\Projects\AnimeSuperResolution\.venv\Lib\site-packages\setuptools\__init__.py", line 87, in _install_setup_requires
    _fetch_build_eggs(dist)
  File "C:\Develop\Projects\AnimeSuperResolution\.venv\Lib\site-packages\setuptools\__init__.py", line 92, in _fetch_build_eggs
    dist.fetch_build_eggs(dist.setup_requires)
  File "C:\Develop\Projects\AnimeSuperResolution\.venv\Lib\site-packages\setuptools\dist.py", line 766, in fetch_build_eggs
    return _fetch_build_eggs(self, requires)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Develop\Projects\AnimeSuperResolution\.venv\Lib\site-packages\setuptools\installer.py", line 54, in _fetch_build_eggs
    resolved_dists = [_fetch_build_egg_no_warn(dist, req) for req in needed_reqs]
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Develop\Projects\AnimeSuperResolution\.venv\Lib\site-packages\setuptools\installer.py", line 123, in _fetch_build_egg_no_warn
    raise DistutilsError(str(e)) from e
distutils.errors.DistutilsError: Command '['C:\\Develop\\Projects\\AnimeSuperResolution\\.venv\\Scripts\\python.exe', '-m', 'pip', '--disable-pip-version-check', 'wheel', '--no-deps', '-w', 'C:\\Users\\AKIBAA~1\\AppData\\Local\\Temp\\tmpqop76gzt', '--quiet', 'cython']' returned non-zero exit status 1.
```

在第 16 行报错处可以看到提示没有 `pip` 模块。

## 解决方法

考虑到我用的是 [uv](https://github.com/astral-sh/uv)，而 uv 虚拟环境是不默认带 pip 模块的，因此可以采用 uv 自带的 [可编辑安装](https://docs.astral.sh/uv/pip/packages/#editable-packages)：

```bash
uv pip install -e .
```

`-e` 或 `--editable` 参数表示可编辑安装。可编辑软件包无需重新安装即可使其源代码的更改生效。这同等于 `python setup.py develop` 中 `develop` 的含义。

即可正确安装。

## 扩展

`#!bash python setup.py *` 这种命令已经被 [废弃](https://packaging.python.org/en/latest/discussions/setup-py-deprecated/#what-commands-should-be-used-instead)，需要使用以下命令来代替：

| Deprecated                    | Recommendation                       |
|-------------------------------|--------------------------------------|
| `python setup.py install`     | `python -m pip install .`            |
| `python setup.py develop`     | `python -m pip install --editable .` |
| `python setup.py sdist`       | `python -m build`                    |
| `python setup.py bdist_wheel` | `python -m build`                    |
