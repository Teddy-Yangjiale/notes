# -*- coding: utf-8 -*-
"""把讲义 PDF 逐页渲染成课件截图（宽 1200，二倍图），量化到 256 色压缩体积。

用法：python cs184-l02-render-pages.py <pdf> <输出目录>
"""
import os
import sys
import fitz
from PIL import Image

pdf = sys.argv[1] if len(sys.argv) > 1 else \
    r"D:\CS184\CS184_2026\fa26\lectures\L02-drawing-triangles.pdf"
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
    os.path.dirname(__file__), "..", "src", "content", "notes",
    "cs184-02-drawing-triangles", "images")
out = os.path.normpath(out)
os.makedirs(out, exist_ok=True)

W = 1200
doc = fitz.open(pdf)
for i, page in enumerate(doc):
    zoom = W / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    fn = os.path.join(out, "p%02d.png" % (i + 1))
    pix.save(fn)
    im = Image.open(fn).convert("RGB")
    im.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.FLOYDSTEINBERG).save(fn, optimize=True)
print("%d pages -> %s" % (doc.page_count, out))
doc.close()
