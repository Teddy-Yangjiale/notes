#!/usr/bin/env python3
"""把一整个文件夹的 markdown 导入成一个专栏。

用法:
    python3 scripts/import_series.py <目录> --series cs336 --prefix cs336 \
        --tags "大模型,系统" [--dry-run]

做的事:
  1. 扫描目录下所有 .md, 从文件名里解析讲次编号当作 order
  2. 生成 front matter(title / date / summary / tags / series / order / shortTitle)
  3. 重写指向同目录其它讲的链接 -> 站内相对链接
  4. 把指向目录外本地文件的失效链接降级成纯文本(保留文字, 去掉链接)
  5. 写进 src/content/notes/<prefix>-<NN>.md
"""
import argparse, datetime, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "src" / "content" / "notes"

NUM_RE = re.compile(r"(?:lecture[_-]?|L|第)(\d{1,2})", re.I)
SUP_RE = re.compile(r"补充\s*(?:篇\s*)?([A-Za-z])")
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_order(name: str) -> int:
    """讲次编号；补充篇排到 90 之后；README 当作 0(总览)。"""
    if name.lower().startswith("readme"):
        return 0
    m = SUP_RE.search(name)
    if m:
        return 90 + (ord(m.group(1).upper()) - ord("A") + 1)
    m = NUM_RE.search(name)
    return int(m.group(1)) if m else 999


def split_title(h1: str) -> tuple[str, str]:
    """把 'Lecture 3：现代 Transformer 架构' 拆成 (完整标题, 列表里用的短标题)。"""
    t = h1.strip()
    short = re.sub(r"^(?:Lecture\s*\d+|L\d+|补充篇?\s*[A-Za-z])\s*[·:：\-—]?\s*", "", t)
    short = re.sub(r"（[^）]*）\s*$", "", short).strip()   # 去掉结尾的英文括注
    return t, (short or t)


def make_summary(body: str) -> str:
    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if not p or p.startswith(("#", ">", "|", "```", "$$", "---")):
            continue
        if p.startswith(("-", "*")) and not p.startswith("**"):
            continue
        p = re.sub(r"^\d+[.、)]\s*", "", p)
        p = re.sub(r"\$\$?[^$]*\$\$?", "", p)
        p = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", p)
        p = LINK_RE.sub(r"\1", p)
        p = re.sub(r"\*\*(.+?)\*\*", r"\1", p)
        p = re.sub(r"[`*_]", "", p)
        p = " ".join(p.split())
        if len(p) < 24:
            continue
        return p[:100] + ("…" if len(p) > 100 else "")
    return ""


def rewrite_links(body: str, slug_of: dict[str, str]) -> tuple[str, int, int]:
    """同专栏内部链接 -> 站内相对链接; 目录外的本地链接 -> 纯文本。"""
    fixed = dead = 0

    def sub(m: re.Match) -> str:
        nonlocal fixed, dead
        label, target = m.group(1), m.group(2).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        clean = target.split("#")[0].split("?")[0]
        base = pathlib.PurePosixPath(clean).name
        if base in slug_of:
            fixed += 1
            # 笔记页都在 /<base>/<slug>/ 这一层, 所以同级用 ../<slug>/
            return f"[{label}](../{slug_of[base]}/)"
        # 指向压缩包外面的文件, 站上不存在 —— 保留文字, 去掉链接
        dead += 1
        return label

    return LINK_RE.sub(sub, body), fixed, dead


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=pathlib.Path)
    ap.add_argument("--series", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--tags", default="")
    ap.add_argument("--overview-title", default="课程总览与阅读路线")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = sorted(args.src.glob("*.md"), key=lambda f: parse_order(f.name))
    if not files:
        print(f"{args.src} 下没有 .md", file=sys.stderr)
        return 1

    # 先建立 文件名 -> slug 的映射, 重写链接时要用
    slug_of: dict[str, str] = {}
    for f in files:
        o = parse_order(f.name)
        slug_of[f.name] = (
            f"{args.prefix}-00-overview" if o == 0
            else f"{args.prefix}-{o:02d}" if o < 90
            else f"{args.prefix}-sup-{chr(ord('a') + o - 91)}"
        )

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    total_fixed = total_dead = 0

    for f in files:
        raw = f.read_text(encoding="utf-8")
        if raw.lstrip().startswith("---"):
            print(f"  跳过 {f.name}: 已有 front matter", file=sys.stderr)
            continue

        lines = raw.splitlines()
        h1 = next((l[2:] for l in lines if l.startswith("# ")), f.stem)
        for i, l in enumerate(lines):
            if l.startswith("# "):
                lines.pop(i)
                while i < len(lines) and not lines[i].strip():
                    lines.pop(i)
                break

        order = parse_order(f.name)
        title, short = split_title(h1)
        if order == 0:
            title = short = args.overview_title

        body = "\n".join(lines).strip()
        body, fixed, dead = rewrite_links(body, slug_of)
        total_fixed += fixed
        total_dead += dead

        fm = [
            "---",
            f"title: {yaml_quote(title)}",
            f"date: {datetime.date.fromtimestamp(f.stat().st_mtime).isoformat()}",
        ]
        summary = make_summary(body)
        if summary:
            fm.append(f"summary: {yaml_quote(summary)}")
        fm.append("tags: [" + ", ".join(yaml_quote(t) for t in tags) + "]")
        fm.append(f"series: {yaml_quote(args.series)}")
        fm.append(f"order: {order}")
        if short != title:
            fm.append(f"shortTitle: {yaml_quote(short)}")
        fm.append("---")

        out = DEST / f"{slug_of[f.name]}.md"
        if args.dry_run:
            print(f"  [dry] {f.name}  →  {out.name}  (order={order})  {title[:34]}")
        else:
            DEST.mkdir(parents=True, exist_ok=True)
            out.write_text("\n".join(fm) + "\n\n" + body + "\n", encoding="utf-8")
            print(f"  ✓ {out.name:24} order={order:<4} {title[:36]}")

    print(f"\n  链接：站内重写 {total_fixed} 处，失效链接降级为纯文本 {total_dead} 处")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
