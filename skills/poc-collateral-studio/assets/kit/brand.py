# kit/brand.py: pull the theme out of the UnifyApps template so every collateral matches it.
# usage: python3 kit/brand.py path/to/UnifyApps_template.pptx
# writes brand/tokens.json, brand/logo.png, brand/template.pptx (a copy; the original is never touched)
import sys, json, re, zipfile, shutil, os
src = sys.argv[1]; os.makedirs("brand", exist_ok=True)
shutil.copy(src, "brand/template.pptx")
z = zipfile.ZipFile(src)
theme = z.read("ppt/theme/theme1.xml").decode()
scheme = dict(re.findall(r'<a:(dk1|lt1|dk2|lt2|accent\d|hlink)><a:srgbClr val="(\w{6})"', theme))
# Defaults below are the values of the current template; the scheme read above overrides where it says so.
tok = {
  "canvas_from": "#FFFFFF", "canvas_to": "#" + scheme.get("lt2", "F7F3ED"),
  "ink": "#0F2805", "emphasis": "#" + scheme.get("dk1", "847347"), "body": "#3D3829",
  "olive": "#" + scheme.get("dk2", "4E582D"), "olive_2": "#" + scheme.get("accent4", "828750"),
  "card": "#FCFAF5", "card_line": "#C3B9A8", "disc": "#" + scheme.get("lt1", "EDE6D7"),
  "sand": "#" + scheme.get("accent5", "C5BAA9"), "sand_2": "#" + scheme.get("accent6", "E3D8C2"),
  "alert_fill": "#F8ECE8", "alert_line": "#DDB9B2", "alert_text": "#AF4C44",
  "font": "Spectral", "tagline": "Intelligence that compounds",
  "footer": "Agentic Automation for the Enterprise   ·   Strictly Confidential",
}
# The logo is the wide image on the slide layout (the footer wordmark).
from PIL import Image; import io
best = None
for n in z.namelist():
    if re.match(r"ppt/slideLayouts/_rels/.*\.rels", n):
        for t in re.findall(r'Target="\.\./media/([^"]+)"', z.read(n).decode()):
            im = Image.open(io.BytesIO(z.read("ppt/media/" + t)))
            if im.width > 2 * im.height and (best is None or im.width > best[1].width): best = (t, im)
if best: best[1].save("brand/logo.png"); print("logo:", best[0], best[1].size)
json.dump(tok, open("brand/tokens.json", "w"), indent=2); print(json.dumps(tok, indent=2))
