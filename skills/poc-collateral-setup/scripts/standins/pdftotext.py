#!/usr/bin/env python3
# pdftotext stand-in (poc-collateral): pdftotext [-layout] <file.pdf> [-|out.txt]
import sys
from pypdf import PdfReader
a = [x for x in sys.argv[1:] if not x.startswith("-") or x == "-"]
src = a[0]; dst = a[1] if len(a) > 1 else src[:-4] + ".txt"
t = "\n\f".join((p.extract_text(extraction_mode="layout") or "") for p in PdfReader(src).pages)
sys.stdout.write(t) if dst == "-" else open(dst, "w").write(t)
