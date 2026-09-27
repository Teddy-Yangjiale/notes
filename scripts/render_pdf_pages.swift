import Foundation
import PDFKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

// 用法: render <input.pdf> <outDir> <目标宽度px>
let args = CommandLine.arguments
guard args.count >= 4,
      let doc = PDFDocument(url: URL(fileURLWithPath: args[1])),
      let targetW = Double(args[3]) else {
    FileHandle.standardError.write("用法: render <pdf> <outDir> <width>\n".data(using: .utf8)!)
    exit(1)
}
let outDir = URL(fileURLWithPath: args[2])
try? FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let box = page.bounds(for: .mediaBox)
    let scale = targetW / Double(box.width)
    let w = Int((Double(box.width) * scale).rounded())
    let h = Int((Double(box.height) * scale).rounded())

    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
                              bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(),
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { continue }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: CGFloat(scale), y: CGFloat(scale))
    ctx.translateBy(x: -box.minX, y: -box.minY)
    ctx.interpolationQuality = .high
    ctx.setRenderingIntent(.defaultIntent)
    page.draw(with: .mediaBox, to: ctx)

    guard let img = ctx.makeImage() else { continue }
    let name = String(format: "p%02d.png", i + 1)
    let url = outDir.appendingPathComponent(name)
    guard let dest = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil)
    else { continue }
    CGImageDestinationAddImage(dest, img, nil)
    CGImageDestinationFinalize(dest)
}
print("✓ \(doc.pageCount) 页 → \(outDir.path)")

// 用法：
//   swiftc -O scripts/render_pdf_pages.swift -o /tmp/render
//   /tmp/render 课件.pdf 输出目录 1200
//
// 只依赖 macOS 自带的 PDFKit / CoreGraphics / ImageIO，不需要安装
// poppler、PyMuPDF 之类的外部工具。输出 pNN.png，正文最宽约 544px，
// 取 1200 即二倍图足够清晰。
