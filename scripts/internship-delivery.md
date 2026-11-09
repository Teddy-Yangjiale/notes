# 实习专栏交付记录 · 2026-11-09

## 阅读入口

- 本地预览：http://127.0.0.1:4322/notes/series/internship/
- 文章源文件：`src/content/notes/internship-*/index.md`，共 18 篇。
- 图片、源码快照与可编辑图包：`public/internship/`。
- 原生绘图：`D:\Draw\out\internship_notes_20261109\`。
- 绘图操作与检查：`D:\Draw\.pptdraw\internship_notes_20261109\`。

首次交付在本地完成，随后用户于 2026-11-09 明确授权发布到 GitHub Pages。正式专栏地址为 https://teddy-yangjiale.github.io/notes/series/internship/ 。发布使用限定文件范围的提交，并从干净检出构建；正式页面检查脚本为 `internship-verify-published.py`。发布成功与否应以对应 GitHub Actions 和线上检查报告为准。已有服务器上的算法、模型、训练、服务均未修改。13 个当前端口的首页与进程、相关源文件、已有结果通过只读方式核对。8820 当前未监听，按历史版本单独说明。

## 内容与证据

覆盖总览、共同几何基础、8820–8833 各自的实现、ABot/SAM 3/DA3 模型拆解、最终 pipeline 与最小实验设计。

讲解使用问题、假设、变量、公式推导、数值例子、代码定位、真实结果与失败条件的顺序。源码课含真实节选、带行号完整文件、SHA-256 与版本信息。素材区分原始照片、模型输出、历史诊断和教学示意；缺少中间产物的步骤明确注明，未为补图运行模型。

## 已完成检查

- `npm run build`：退出码 0，整站 354 个生成页面，Pagefind 索引 135 篇页面。
- `python scripts/internship-verify.py`：18 篇新文章，39,652 个中文字，285 处 KaTeX 公式，55 张唯一引用图片，206 个唯一站内链接；错误 0。
- 52 份完整源码 HTML 快照；静态检查包含其行号锚点。
- 18 份原生 PPTX 经 PowerPoint 渲染，18 份机械 lint 无问题；已检查联系表与代表图。
- 浏览器实际检查专栏 18 篇目录、8827 正文、图片加载、公式、源码第 35 行跳转。
- 8827 在 1280 px 与 390 px 视口无整页横向溢出；修复新增导航导致的手机文字折行。长公式在框内滚动。
- 截图：`.work/internship/formula-desktop.png`。结构检查报告：`.work/internship/validation.json`。

浏览器检查是代表页面检查，并非所有设备、所有交互的穷举测试。额外 320 px 检查遇到浏览器标签同步超时，未计为通过；重新打开专栏已确认可访问，测试用视口覆盖已重置。

首次构建曾成功退出但读取旧内容索引，导致新专栏 404。备份并移出 `node_modules/.astro/data-store.json` 后重建，已恢复新文章与专栏；旧索引保存在 `.work/internship/`。最终再次构建并检查通过。

## 重新预览与验证

在 `D:\notes` 执行：

```powershell
npm run build
python scripts/internship-verify.py
npm run preview -- --host 127.0.0.1 --port 4322
```

若 4322 已被此次预览占用，直接打开阅读入口即可。源码及素材采集脚本用于复查，不是阅读或构建所必需。`internship-finalize.py` 会刷新自动生成的源码课附录与图包，正文人工编辑应放在附录标记之前。

模型和历史高斯结果具有各自快照日期；正文所列方案与最小实验均为设计，尚未执行。当前交付不声称得到新的重建精度或训练结果。
