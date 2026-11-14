#!/usr/bin/env python3
"""sample_redact.py — keep real client samples out of session logs (used by session_log.py slice).

Real samples live in `<workspace>/01-requirement-gathering/files/samples/`. A session reads them (pandoc, pdftotext,
Read, the AI PM's own reads), so their text lands in the session log. Before a log is uploaded, every piece of sample
text in it is replaced with "[REDACTED: real sample <file name>]", and everything else is kept.

How it finds sample text, two ways at once:
  1. It extracts each sample's own text (txt/md/csv/json/eml/html/xml/yaml read directly; docx/pptx/xlsx from their XML;
     pdf with pdftotext or pypdf when available) and cuts it into overlapping runs of 6 words. Any run of 6 words in the
     log that matches one (case and punctuation ignored, so pandoc/markdown formatting does not hide it) is redacted,
     wherever it appears: tool results, file reads, Claude's own messages, helper-agent logs.
  2. Any tool call whose input names a `files/samples` path has its whole result redacted, and that result's text is
     added to the runs, so a later quote of it is caught too (this covers a sample whose text could not be extracted).
Base64 file payloads (PDF or image reads, downloads) are always replaced with a short note.

usage (for testing): sample_redact.py <project dir> <text file>   prints the text with sample text redacted
"""
import hashlib, html, json, os, re, shutil, subprocess, sys, zipfile

K = 6                       # words per run
WORD = re.compile(r"\w+", re.UNICODE)
SAMPLE_MARK = re.compile(r"files[/\\]+samples", re.I)
TEXT_EXT = {".txt", ".md", ".csv", ".tsv", ".json", ".eml", ".html", ".htm", ".xml", ".yaml", ".yml", ".log", ".rtf"}
B64 = re.compile(r"^[A-Za-z0-9+/=\s]+$")


def find_samples(root, max_depth=7):
    out = []
    root = os.path.abspath(root)
    base_depth = root.rstrip(os.sep).count(os.sep)
    for cur, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".git", "node_modules", "__pycache__", ".poc-studio")]
        if cur.count(os.sep) - base_depth > max_depth:
            dirs[:] = []
            continue
        if SAMPLE_MARK.search(cur.replace(root, "")):
            out += [os.path.join(cur, f) for f in files if not f.startswith(".")]
    return sorted(out)


def _xml_text(z, names):
    parts = []
    for n in names:
        try:
            x = z.read(n).decode("utf-8", "replace")
        except KeyError:
            continue
        x = re.sub(r"</(w:p|a:p|row|si|p)>", "\n", x)
        parts.append(html.unescape(re.sub(r"<[^>]+>", " ", x)))
    return "\n".join(parts)


def extract(path):
    """The sample's text, or None when it cannot be read here."""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in TEXT_EXT:
            t = open(path, encoding="utf-8", errors="replace").read()
            return html.unescape(re.sub(r"<[^>]+>", " ", t)) if ext in (".html", ".htm", ".xml") else t
        if ext in (".docx", ".pptx", ".xlsx", ".docm", ".xlsm"):
            z = zipfile.ZipFile(path)
            names = z.namelist()
            if ext.startswith(".doc"):
                pick = [n for n in names if re.match(r"word/(document|header\d*|footer\d*|footnotes|endnotes)\.xml$", n)]
            elif ext == ".pptx":
                pick = [n for n in names if re.match(r"ppt/(slides|notesSlides)/[^/]+\.xml$", n)]
            else:
                pick = [n for n in names if n == "xl/sharedStrings.xml" or re.match(r"xl/worksheets/[^/]+\.xml$", n)]
            return _xml_text(z, pick)
        if ext == ".pdf":
            if shutil.which("pdftotext"):
                r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, timeout=60)
                if r.returncode == 0 and r.stdout.strip():
                    return r.stdout
            for mod in ("pypdf", "PyPDF2"):
                try:
                    m = __import__(mod)
                    return "\n".join((p.extract_text() or "") for p in m.PdfReader(path).pages)
                except Exception:
                    continue
            if shutil.which("pandoc"):
                pass
            return None
        if shutil.which("pandoc") and ext in (".odt", ".epub", ".rst", ".org"):
            r = subprocess.run(["pandoc", path, "-t", "plain"], capture_output=True, text=True, timeout=60)
            return r.stdout if r.returncode == 0 else None
    except Exception:
        return None
    return None


def _h(words):
    return hashlib.blake2b(" ".join(words).encode("utf-8"), digest_size=8).digest()


class Redactor:
    def __init__(self):
        self.runs = {}            # hash of 6 words -> sample name
        self.counts = {}          # sample name -> pieces redacted
        self.not_extracted = []
        self.samples = []

    def add_text(self, text, name):
        w = [m.group(0).lower() for m in WORD.finditer(text or "")]
        for i in range(len(w) - K + 1):
            self.runs.setdefault(_h(w[i:i + K]), name)

    def load(self, root, cache_dir=None):
        for p in find_samples(root):
            name = os.path.basename(p)
            self.samples.append(name)
            text = None
            key = None
            if cache_dir:
                st = os.stat(p)
                key = os.path.join(cache_dir, hashlib.sha1(("%s|%s|%s" % (p, st.st_size, st.st_mtime)).encode()).hexdigest())
                if os.path.isfile(key):
                    text = open(key, encoding="utf-8").read()
            if text is None:
                text = extract(p)
                if text is not None and key:
                    os.makedirs(cache_dir, exist_ok=True)
                    open(key, "w", encoding="utf-8").write(text)
            if text and text.strip():
                self.add_text(text, name)
            else:
                self.not_extracted.append(name)
        return self

    def spans(self, s):
        ms = list(WORD.finditer(s))
        if len(ms) < K or not self.runs:
            return []
        lw = [m.group(0).lower() for m in ms]
        hits = []
        for i in range(len(ms) - K + 1):
            n = self.runs.get(_h(lw[i:i + K]))
            if n is not None:
                hits.append((ms[i].start(), ms[i + K - 1].end(), n))
        merged = []
        for a, b, n in hits:      # join overlapping or nearly touching pieces (a few characters between them)
            if merged and a <= merged[-1][1] + 12:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b, n])
        return merged

    def redact(self, s):
        sp = self.spans(s)
        if not sp:
            return s
        out, last = [], 0
        for a, b, n in sp:
            out.append(s[last:a])
            out.append("[REDACTED: real sample %s]" % n)
            self.counts[n] = self.counts.get(n, 0) + 1
            last = b
        out.append(s[last:])
        return "".join(out)

    def left(self, s):
        return bool(self.spans(s))


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for x in o:
            yield from strings(x)
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)


def drop_binary(o):
    """Replace base64 payloads (file or image reads, downloads) with a short note."""
    if isinstance(o, dict):
        if o.get("type") == "base64" and isinstance(o.get("data"), str):
            return dict(o, data="[REDACTED: base64 data, %d chars]" % len(o["data"]))
        return {k: drop_binary(v) for k, v in o.items()}
    if isinstance(o, list):
        return [drop_binary(x) for x in o]
    if isinstance(o, str) and len(o) > 4000 and " " not in o[:4000] and B64.match(o[:4000]):
        return "[REDACTED: base64 data, %d chars]" % len(o)
    return o


def sample_tool_ids(entry):
    """ids of tool calls in this entry whose input names a files/samples path."""
    m = entry.get("message") if isinstance(entry, dict) else None
    c = m.get("content") if isinstance(m, dict) else None
    out = []
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_use" and SAMPLE_MARK.search(json.dumps(b.get("input"), ensure_ascii=False)):
                out.append(b.get("id"))
    return [x for x in out if x]


def results_for(entry, ids):
    """(tool_use_id, text) of tool results in this entry that answer one of ids."""
    m = entry.get("message") if isinstance(entry, dict) else None
    c = m.get("content") if isinstance(m, dict) else None
    out = []
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in ids:
                out.append((b["tool_use_id"], "\n".join(strings(b.get("content")))))
    return out


def blank_results(entry, ids):
    """Replace the content of tool results answering ids (and the line's toolUseResult copy) with a note."""
    m = entry.get("message")
    c = m.get("content") if isinstance(m, dict) else None
    hit = False
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in ids:
                b["content"] = "[REDACTED: real sample content read by this tool call]"
                hit = True
    if hit and "toolUseResult" in entry:
        entry["toolUseResult"] = "[REDACTED: real sample content read by this tool call]"
    return hit


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    r = Redactor().load(sys.argv[1])
    print(r.redact(open(sys.argv[2], encoding="utf-8", errors="replace").read()))
    print(json.dumps({"samples": r.samples, "redacted": r.counts, "not_extracted": r.not_extracted}), file=sys.stderr)
