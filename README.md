# 笔记本

用 Astro 搭的个人笔记站，写 markdown、push、自动发布到 GitHub Pages。

## 日常使用

```bash
npm run dev      # 本地预览 http://localhost:4321，改文件即时刷新
npm run build    # 构建 + 生成全文搜索索引到 dist/
npm run preview  # 预览构建结果
```

新笔记 = 在 `src/content/notes/` 里放一个 `.md` 文件。
可用字段见 `src/content.config.ts`（title / date 必填，其余可选：
summary、tags、updated、draft、pinned、color）。

带图片的笔记做成文件夹：`notes/某篇/index.md` + `notes/某篇/图片.png`，
正文里用相对路径 `![说明](./图片.png)` 引用。

导入已有的 markdown：

```bash
python3 scripts/import.py ~/Documents/某篇笔记.md --tags "标签1,标签2"

# 带图片的：--bundle 会把引用到的图片目录一起搬过来
python3 scripts/import.py ~/笔记/某篇.md --bundle --tags "标签"

# --strip-toc 删掉正文里手写的目录（站点会自动生成侧边目录）
```

## 部署

目标地址：**https://teddy-yangjiale.github.io/notes/**

配置已经写好在 `astro.config.mjs`：

```js
site: 'https://teddy-yangjiale.github.io',
base: '/notes',          // = 仓库名
```

### 首次推送

```bash
git remote add origin git@github.com:Teddy-Yangjiale/notes.git
git push -u origin main
```

然后到仓库 **Settings → Pages → Source**，选 **GitHub Actions**。
之后每次 push 到 `main` 都会自动构建部署。

### 换仓库名要改三处

1. `astro.config.mjs` 的 `base`
2. git remote 地址
3. 本文件里的地址

> ⚠️ 站内链接一律用 `withBase()` 生成（见 `src/lib/notes.ts`）。
> 直接写 `href="/tags/"` 在有 base 的部署下会 404。

## 目录结构

```
src/
  content/notes/     ← 你的笔记都在这里
  content.config.ts  ← front matter 字段定义
  lib/notes.ts       ← 排序、标签、配色、阅读时长
  layouts/           ← 页面外壳（主题切换、进度条、入场动画）
  components/        ← Header / Footer / NoteCard
  pages/             ← 路由
  styles/global.css  ← 设计系统：纸感底色、便签色板、深浅双主题
scripts/import.py    ← markdown 导入工具
```
