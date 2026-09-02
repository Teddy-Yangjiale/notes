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

## 专栏（合集）

多篇成体系的笔记可以收进一个"专栏"，在首页显示为一张合集卡片，点进去是按讲次排好的目录。

**开一个新专栏**：在 `src/lib/series.ts` 的 `SERIES` 数组里加一条：

```ts
{
  id: 'cs224n',                    // 网址 /series/cs224n/
  title: 'CS224N · 自然语言处理',
  badge: 'CS224N',                 // 卡片上的印章代号
  description: '一句话介绍…',
  color: 'moss',                   // sand/moss/sky/clay/plum/lilac
  weight: 3,                       // 首页排序
}
```

**把笔记归进专栏**：在 front matter 里写

```yaml
series: "cs224n"
order: 3                  # 专栏内顺序；>=90 的显示成 A/B/C（补充篇）
shortTitle: "词向量"       # 可选，列表里用它代替长标题
```

归入专栏的笔记不再单独出现在首页"散记"区。文章页会自动加上专栏面包屑，
上下篇也改为沿讲次走而不是按时间。

**批量导入一整门课**：

```bash
python3 scripts/import_series.py <目录> --series cs336 --prefix cs336 \
    --tags "大模型,系统" --dry-run     # 先预演，确认无误后去掉 --dry-run
```

它会从文件名解析讲次编号当 order、生成 front matter、把指向同目录其它讲的链接
改写成站内链接，并把指向目录外的失效链接降级成纯文本。

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
