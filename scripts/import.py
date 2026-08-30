#!/usr/bin/env python3
"""把一个已有的 markdown 文件导入笔记本。

用法:
    python3 scripts/import.py <文件.md> [选项]

选项:
    --tags 标签1,标签2   逗号分隔
    --slug 自定义名       默认由标题生成
    --title 标题          默认取正文第一个 # 一级标题
    --draft               导成草稿(线上不发布)
    --bundle              建成 <slug>/index.md, 并把引用到的本地图片目录一起搬过来
    --strip-toc           删掉正文里手写的"目录"小节(站点会自动生成侧边目录)

做的事:
  1. 猜标题(第一个 # 一级标题, 否则用文件名), 并把它从正文里删掉,
     避免和页面上的大标题重复
  2. 猜摘要(第一段有实际内容的文字, 截到 ~90 字)
  3. 生成 YAML front matter, 日期取文件的修改时间
  4. 写进 src/content/notes/
"""
import argparse, datetime, pathlib, re, shutil, sys, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "src" / "content" / "notes"

IMG_RE = re.compile(r"!\[[^\]]*\]\(\s*<?([^)>\s]+)")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^\w一-鿿-]", "", text)      # 保留中文, 去掉标点
    return re.sub(r"-{2,}", "-", text).strip("-") or "note"


def yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def extract_title(lines: list[str]) -> str | None:
    """取出第一个一级标题并把它(以及紧随的空行)从正文中删掉。"""
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            lines.pop(i)
            while i < len(lines) and not lines[i].strip():
                lines.pop(i)
            return title
    return None


def strip_toc(lines: list[str]) -> None:
    """删掉手写的目录小节: 从 '## 目录' 到下一个同级标题之前。"""
    start = next(
        (i for i, l in enumerate(lines)
         if re.match(r"^#{2,3}\s*(目录|目 录|Contents|Table of Contents)\s*$", l.strip())),
        None,
    )
    if start is None:
        return
    depth = len(lines[start]) - len(lines[start].lstrip("#"))
    end = len(lines)
    for j in range(start + 1, len(lines)):
        m = re.match(r"^(#{1,6})\s", lines[j])
        if m and len(m.group(1)) <= depth:
            end = j
            break
    del lines[start:end]
    # 顺手清掉可能孤立在前面的分隔线
    while start > 0 and lines[start - 1].strip() in ("", "---"):
        if lines[start - 1].strip() == "---":
            del lines[start - 1]
            break
        start -= 1


def make_summary(body: str) -> str:
    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if not p or p.startswith(("#", ">", "|", "```", "$$", "---")):
            continue
        if p.startswith(("-", "*")) and not p.startswith("**"):
            continue
        p = re.sub(r"^\d+[.、)]\s*", "", p)              # 有序列表: 去序号照用
        p = re.sub(r"\$\$?[^$]*\$\$?", "", p)            # 公式不进摘要
        p = re.sub(r"\*\*(.+?)\*\*", r"\1", p)
        p = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", p)
        p = re.sub(r"[`*_]", "", p)
        p = " ".join(p.split())
        if len(p) < 24:                                  # 太短的引导句不算摘要
            continue
        return p[:90] + ("…" if len(p) > 90 else "")
    return ""


def copy_assets(body: str, src_dir: pathlib.Path, out_dir: pathlib.Path) -> list[str]:
    """把正文里引用到的本地图片(连同它们所在的目录)复制到 bundle 里。"""
    copied: list[str] = []
    roots: set[str] = set()
    for raw in IMG_RE.findall(body):
        if raw.startswith(("http://", "https://", "data:", "/")):
            continue
        rel = raw.lstrip("./")
        top = rel.split("/")[0]
        roots.add(top)

    for top in sorted(roots):
        src = src_dir / top
        if not src.exists():
            print(f"  ⚠ 找不到图片资源: {src}", file=sys.stderr)
            continue
        dst = out_dir / top
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            copied.extend(f"{top}/{p.name}" for p in sorted(src.iterdir()) if p.is_file())
        else:
            shutil.copy2(src, dst)
            copied.append(top)
    return copied


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=pathlib.Path)
    ap.add_argument("--tags", default="")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--summary", default=None)
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--bundle", action="store_true")
    ap.add_argument("--strip-toc", action="store_true")
    args = ap.parse_args()

    if not args.src.is_file():
        print(f"找不到文件: {args.src}", file=sys.stderr)
        return 1

    raw = args.src.read_text(encoding="utf-8")
    if raw.lstrip().startswith("---"):
        print(f"跳过 {args.src.name}: 它已经有 front matter 了", file=sys.stderr)
        return 1

    lines = raw.splitlines()
    title = args.title or extract_title(lines) or args.src.stem
    if args.strip_toc:
        strip_toc(lines)

    body = "\n".join(lines).strip()
    summary = args.summary if args.summary is not None else make_summary(body)
    date = datetime.date.fromtimestamp(args.src.stat().st_mtime)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    slug = args.slug or slugify(title)

    fm = ["---", f"title: {yaml_quote(title)}", f"date: {date.isoformat()}"]
    if summary:
        fm.append(f"summary: {yaml_quote(summary)}")
    fm.append("tags: [" + ", ".join(yaml_quote(t) for t in tags) + "]")
    if args.draft:
        fm.append("draft: true")
    fm.append("---")

    if args.bundle:
        out_dir = DEST / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "index.md"
        assets = copy_assets(body, args.src.parent, out_dir)
    else:
        DEST.mkdir(parents=True, exist_ok=True)
        out = DEST / f"{slug}.md"
        assets = []

    out.write_text("\n".join(fm) + "\n\n" + body + "\n", encoding="utf-8")
    print(f"✓ {args.src.name}  →  {out.relative_to(ROOT)}")
    for a in assets:
        print(f"    ↳ 图片 {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
