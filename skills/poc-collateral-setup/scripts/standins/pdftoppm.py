#!/usr/bin/env python3
# pdftoppm stand-in (poc-collateral): pdftoppm [-r DPI] [-png|-jpeg] [-f N] [-l N] <file.pdf> <prefix>
import sys, pypdfium2 as pdfium
args = sys.argv[1:]; dpi = 150; fmt = "png"; first = None; last = None; pos = []; i = 0
while i < len(args):
    x = args[i]
    if x == "-r": dpi = float(args[i + 1]); i += 2; continue
    if x in ("-png", "-jpeg"): fmt = x[1:]; i += 1; continue
    if x == "-f": first = int(args[i + 1]); i += 2; continue
    if x == "-l": last = int(args[i + 1]); i += 2; continue
    pos.append(x); i += 1
pdf = pdfium.PdfDocument(pos[0]); n = len(pdf); w = len(str(n))
for k in range((first or 1) - 1, min(last or n, n)):
    pdf[k].render(scale=dpi / 72).to_pil().save(f"{pos[1]}-{str(k + 1).zfill(w)}." + ("jpg" if fmt == "jpeg" else "png"))
