---
author: Akiba Arisa
author_gh_user: zhanbao2000
read_time: 15 min
tags:
    - github actions
    - github pages
    - vuepress
title: GitHub Pages 文档自动化部署 - VuePress
---

上一篇博客说到了 MkDocs 部署遇到的坑，这篇文章来说说 VuePress 的部署。

!!! 注意 attention

    我使用的是 [VuePress v1.x](https://vuepress.vuejs.org/zh/)，跨版本出现的坑本人一概不知。

## 本地部署测试

首先同样是本地部署

=== "npm"

    ```bash
    npm run docs:build
    ```

=== "yarn"

    ```bash
    yarn docs:build
    ```

要是本地编译都没法通过，那就别继续了。

## 在 GitHub 上创建 Actions 任务

让我们跳过创建本地 VCS 并和 GitHub 关联的步骤，因为上一篇博客已经说的很明确了，这篇博客我们直接从 `yam` 文件怎么写开始说起。

同样是去找官方文档，注意 `1.x` 和 `2.x` 的文档有所不同。

=== "1.x"

    ```yaml title="main.yml（请勿直接使用）" linenums="1" hl_lines="15 16 18"
    name: Build and Deploy
    on: [push]
    jobs:
      build-and-deploy:
        runs-on: ubuntu-latest
        steps:
        - name: Checkout
          uses: actions/checkout@master
    
        - name: vuepress-deploy
          uses: jenkey2011/vuepress-deploy@master
          env:
            ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
            TARGET_REPO: username/repo
            TARGET_BRANCH: master
            BUILD_SCRIPT: yarn && yarn build
            BUILD_DIR: docs/.vuepress/dist
            CNAME: https://www.xxx.com
    ```

=== "2.x（仅做示范，不标注）"

    ```yaml title="main.yml（请勿直接使用）" linenums="1" 
    name: docs
    
    on:
      # 每当 push 到 main 分支时触发部署
      push:
        branches: [main]
      # 手动触发部署
      workflow_dispatch:
    
    jobs:
      docs:
        runs-on: ubuntu-latest
    
        steps:
          - uses: actions/checkout@v2
            with:
              # “最近更新时间” 等 git 日志相关信息，需要拉取全部提交记录
              fetch-depth: 0
    
          - name: Setup Node.js
            uses: actions/setup-node@v1
            with:
              # 选择要使用的 node 版本
              node-version: '14'
    
          # 缓存 node_modules
          - name: Cache dependencies
            uses: actions/cache@v2
            id: yarn-cache
            with:
              path: |
                **/node_modules
              key: ${{ runner.os }}-yarn-${{ hashFiles('**/yarn.lock') }}
              restore-keys: |
                ${{ runner.os }}-yarn-
    
          # 如果缓存没有命中，安装依赖
          - name: Install dependencies
            if: steps.yarn-cache.outputs.cache-hit != 'true'
            run: yarn --frozen-lockfile
    
          # 运行构建脚本
          - name: Build VuePress site
            run: yarn docs:build
    
          # 查看 workflow 的文档来获取更多信息
          # @see https://github.com/crazy-max/ghaction-github-pages
          - name: Deploy to GitHub Pages
            uses: crazy-max/ghaction-github-pages@v2
            with:
              # 部署到 gh-pages 分支
              target_branch: gh-pages
              # 部署目录为 VuePress 的默认输出目录
              build_dir: docs/.vuepress/dist
            env:
              # @see https://docs.github.com/cn/actions/reference/authentication-in-a-workflow#about-the-github_token-secret
              GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ```

!!! 注意有坑 attention

    上面标注的地方，看到没有？全都是坑！  
    尤其是第15行这个 `#!yaml TARGET_BRANCH: master`，简直是一键删库跑路级别的坑。

首先说下15行这个。

`TARGET_BRANCH` 的意思是，指定 build 出来的 HTML 页面存放的分支，而不是指定 markdown 文件存放的分支。当初就被这个东西坑了，以为是从 `TARGET_BRANCH` 这个分支获取 markdown，我就设置的默认的 `master`，结果他把生成的 HTML 全部给 rebase 到我的 `master` 分支了。好了，我写的 markdown 被全部覆盖了。

正确的做法是：`#!yaml TARGET_BRANCH: gh-pages`

这样他就会把生成的 HTML 存放到 `gh-pages` 分支，这也是大多数自动化 Pages 应用（比如 `MkDocs`）生成的页面所在分支。

然后是16行这个 `#!yaml BUILD_SCRIPT: yarn && yarn build`。

你这咋 build？

改成：`#!yaml BUILD_SCRIPT: yarn && yarn docs:build`

然后是18行这个 `CNAME`，这个已经在上一篇博客里提到了，就是用来自动设置自定义域名的，这里改成你想要的域名就可以了。没什么大坑。

最后改一下 `#!yaml TARGET_REPO: username/repo`，指向你自己的 repo，这里以我的 [mokabot2](https://github.com/MokaDevelopers/mokabot2) 为例。

最终的成品应该是这样的：

```yaml title="main.yml" linenums="1"
name: Build and Deploy
on: [push]
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@master

    - name: vuepress-deploy
      uses: jenkey2011/vuepress-deploy@master
      env:
        ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
        TARGET_REPO: MokaDevelopers/mokabot2
        TARGET_BRANCH: gh-pages
        BUILD_SCRIPT: yarn && yarn docs:build
        BUILD_DIR: docs/.vuepress/dist
        CNAME: docs-mokabot.arisa.moe
```

## 设置密钥

这一步必不可少，不然即使 Actions 可以生成，但是 `vuepress-deploy` 没法部署到你的 `gh-pages` 分支里。

看这个 [文档](https://github.com/jenkey2011/vuepress-deploy/blob/master/README.zh-CN.md#%E8%AF%A6%E7%BB%86%E6%95%99%E7%A8%8B) 就行。

## 完成

设置完这些之后，就可以正常通过 `push` 操作触发 Actions 流程自动构建文档了。
