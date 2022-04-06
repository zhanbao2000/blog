---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 15 min
publish_date: 2022-04-07 00:24
tags:
    - github actions
    - github pages
    - mkdocs
title: GitHub Pages 文档自动化部署 - MkDocs
---

这篇文章讲述了如何使用 GitHub Actions / Pages 自动化部署文档，以及遇到的坑。

如你所见，这个博客也是使用 GitHub Actions 自动部署在 GitHub Pages 上的。

这篇文章将以 [MkDocs](https://www.mkdocs.org/) 为例讲述。

## 本地部署测试

首先你自己搭建的文档得在本地能用嘛，首先测试下本地是否能用：

```cmd 
mkdocs serve
```

!!! 小提示

    使用以下参数可以使 mkdocs 运行在指定地址和端口上：
    ```
    mkdocs serve -a localhost:8001
    mkdocs serve --dev-addr localhost:8001
    ```

## 创建本地 VCS 并和 GitHub 关联

这里以 PyCharm 为例：

### 创建本地 VCS

``` mermaid
graph LR
  A[VCS] --> B;
  B[启用版本控制集成] --> C;
  C[选择 Git] --> D[确定];
```

!!! 注意有坑 attention

    记得在提交之前先创建好 `.gitignore` 文件，否则你提交之后还要继续提交一次 `.gitignore` 文件。

然后选择提交。

### 和 GitHub 关联

这一步其实是在 GitHub 上自动创建一个同名仓库。如果仓库已经存在的话，可能需要 Merge 或者 Rebase。

``` mermaid
graph LR
  A[Git] --> B;
  B[GitHub] --> C;
  C[在 GitHub 上共享项目] --> D[确定];
```

## 在 GitHub 上创建 Actions 任务

这一步坑巨多。

首先点击 `Actions` -> `set up a workflow yourself`

按照任何一个你能找到的 Pages 部署文档来写这个 `yml` 文件，这里我们采用 [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/publishing-your-site/#with-github-actions) 的模板。

!!! 小提示

    用 MkDocs [官网](https://www.mkdocs.org/user-guide/deploying-your-docs/) 的也行，只不过人家不会告诉你怎么写这个 `yml` 文件。

在 `2022年4月6日` 的时候我从这里找到的模板是这样的，随着时间的推移可能会有变更，建议从原文档去复制。

```yaml title="main.yml" linenums="1"
name: ci 
on:
  push:
    branches:
      - master 
      - main
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.x
      - run: pip install mkdocs-material 
      - run: mkdocs gh-deploy --force
```

!!! 注意有坑 attention

    首先他这个流程，很明显只用 `pip` 安装了 `mkdocs-material`，但是它并没有安装 `mkdocs`。其实这无所谓，因为 `mkdocs-material` 的 `requirements.txt` 中已经包含了 `mkdocs`，会一并安装。  
    重点的地方是，如果你在本地构建的时候依赖了其他的库（比如 `mkdocs-blogging-plugin`），那你得在 `run:` 中通过 `pip install` 安装这些库。

!!! 注意有坑 attention

    坑还没完，如果你和我一样是 `mkdocs-blogging-plugin` 的使用者，你还会遇到网站的渲染问题，这里官网也给了解决方案。  
    https://liang2kl.codes/mkdocs-blogging-plugin/#publish-with-github-pages  
    注意，请不要跟随官网那篇文档里所说的设定 `locale: zh-CN` 这个键，后面会说到原因。

最终我的 `main.yml`（后来重命名成 `ci.yml` 了）长这样：

```yaml title="main.yml" linenums="1" hl_lines="11 12 18"
name: ci 
on:
  push:
    branches:
      - master 
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:  # mkdocs-blogging-plugin 给出的渲染问题解决方案
          fetch-depth: 0
      - uses: actions/setup-python@v2
        with:
          python-version: 3.x
      - run: pip install mkdocs
      - run: pip install mkdocs-material
      - run: pip install mkdocs-blogging-plugin  # 记得安装其他依赖的库
      - run: mkdocs gh-deploy --force
```

这个时候你就可以在 Actions 页面点 `Start commit` 了。只要你的本地部署可以通过，在 Actions 上应该也是可以通过的。

如果 Actions 的 `build` 或者 `deploy` 阶段出现了问题，说明可能是那几个 `run` 里出现了错误，那你应该在本地试一下：

 - 是不是有包忘了 `pip install` ？
 - 本地能正常 `mkdocs build` 嘛？

之前遇到了一个典型的问题导致 build 失败：

!!! 注意有坑 attention

    `mkdocs-blogging-plugin` 的官网 [文档](https://liang2kl.codes/mkdocs-blogging-plugin/#publish-with-github-pages) 里说，要在 `blogging` 里建一个 `locale: zh-CN` 来设置时间格式，但是实际这样做会报错：`ValueError: expected only letters, got 'zh-cn'`，  
    解决方法：不要写 `locale: zh-CN`，要写 `locale: zh_CN` 或者干脆写 `locale: zh`

    ```yaml title="mkdocs.yml" linenums="1" hl_lines="3"
    plugins:
      - blogging:
          locale: zh_CN
    ```

坑还没结束，继续往下看

## 设置 Pages

你以为这样就结束了？

还没有！

Actions 结束后会给你一个页面（当然也可以自己去找），你点开这个页面会直接告诉你 `404`。

这是因为你还没有为 Pages 指定具体的页面。

!!! 小提示

    这里简单说一下，很多人认为 `Actions` 和 `Pages` 是一个东西，因为很多人经常用这俩一起来部署页面。但是其实这俩的功能是各有分工。  
     - `Actions` 的主要功能是编译，就是你指定一个环境，给出一些编译中要执行的命令行，然后给出你的源代码（这里的源代码 GitHub 会自动从你的 repo 里获取所以不用管），GitHub Actions 就会从源代码里编译出对应的静态文件，这些静态文件可能是各种文件，比如二进制文件，或者是网页。  
     - `Pages` 的主要功能是在 `<user>.github.io` 上部署网页。

Actions 毕竟只是 Actions，他又不是和 Pages 联动的，所以你就算 Actions 编译出了网页也是不会给你自动部署到 Pages 上的。

接下来手动设置 Pages：

``` mermaid
graph LR
  A[打开你的项目仓库] --> B;
  B[Settings] --> C;
  C[Pages] --> D[Source];
```

选择分支为 `gh-pages`，这是 Actions 自动构建的文件所存放的分支，目录选择 `/`。

点 `save`，这下是真没问题了。

## （可选）使用自定义域名

使用自定义域名又会带来两个坑，无语。

首先你在设置 `Source` 的时候，能看到下面一栏是 `Custom domain`，这个就是设置自定义域名的地方，比如我这个博客构建在了 https://zhanbao2000.github.io/blog_mkdocs ，但是我想让 https://blog.arisa.moe/ 指向这个博客，就得修改这玩意。

!!! 小提示

    现在访问 https://zhanbao2000.github.io/blog_mkdocs 会被 `301` 重定向到 https://blog.arisa.moe/

直接在框框里写你的域名肯定是不行的，应该遵循以下步骤，以本站为例：

 1. 找到你域名的 DNS 服务商，添加一个 CNAME 记录：
    ```dns
    blog.arisa.moe.	1	IN	CNAME	zhanbao2000.github.io.
    ```
    
 2. 在刚刚那个框里输入 `blog.arisa.moe`，点 `save`。

过一会就好了。

你以为这样就完了？

!!! 注意有坑 attention

    如果你以为这样就完了，等你下次再通过 `git push` 提交文档/博客的时候，你就会发现你的自定义域名已经变成 `404` 了。  
    此时你打开 GitHub 对应仓库的 Settings 一看，好家伙，框框里什么都没有了。

先说解决方法再说原因。

解决方法是，在 `docs` 文件夹里创建一个 `CNAME` 文件，内容写上你的自定义域名，下次 Actions 运行的时候，Pages 就会自动把这个域名设置成自定义域名了。

参考以下：

 - [Deploying seems to overwrite custom domain #213](https://github.com/tschaub/gh-pages/issues/213)
 - [gh-pages -d dist overwrites custom domain #127](https://github.com/tschaub/gh-pages/issues/127)
 - [MkDocs - Custom Domains](https://www.mkdocs.org/user-guide/deploying-your-docs/#custom-domains) 👉 其实 MkDocs 官网有写

这些 issues 无一例外都提到了要创建一个 `CNAME` 文件来指示自己的自定义域名。但是距离 issue 提出好像已经过了5年了也没见到 GitHub 官方修复这个问题。

我自己推测的原因是这样的：

在 Pages 页面设置自定义域名的时候，实际上是在项目生成目录里自动创建了一个 `CNAME` 文件的，和我们手动创建的效果一样。但是在 Actions 运作的时候，会覆盖掉整个项目生成目录，包括这个 `CNAME` 文件。

那么就有两个办法来解决：

 - 每次 Actions 结束之后，手动去 Pages 页面添加自定义域名。
 - 让 Actions 结束之后，项目生成目录里始终有这个 `CNAME` 文件。

于是我们选择了后者。
