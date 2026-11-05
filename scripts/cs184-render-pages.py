# -*- coding: utf-8 -*-
"""把讲义 PDF 逐页渲染成课件截图（宽 1200 二倍图，量化到 256 色压缩体积）。

用法：python cs184-render-pages.py <pdf> <输出目录> [--pad 2|3]

页数超过 99 的讲次请用 --pad 3，否则文件名会变成 p01..p99 与 p100..p277 混杂，
按字符串排序会错乱，也很容易和正文引用对不上（踩过一次）。
"""
import argparse
import os

import fitz
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out")
    ap.add_argument("--pad", type=int, default=None, help="补零位数，默认按页数自动")
    ap.add_argument("--width", type=int, default=1200)
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    pad = args.pad or (3 if doc.page_count > 99 else 2)
    os.makedirs(args.out, exist_ok=True)
    for i, page in enumerate(doc):
        zoom = args.width / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        fn = os.path.join(args.out, ("p%0" + str(pad) + "d.png") % (i + 1))
        pix.save(fn)
        im = Image.open(fn).convert("RGB")
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                    dither=Image.Dither.FLOYDSTEINBERG).save(fn, optimize=True)
    print("%d pages -> %s (pad=%d)" % (doc.page_count, args.out, pad))
    doc.close()


if __name__ == "__main__":
    main()
