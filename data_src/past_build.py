# -*- coding: utf-8 -*-
"""IPAが公開している基本情報技術者試験の過去問(公開問題・サンプル問題)のPDFから、問題ごとの画像と正解を取り出す。
出力: past/img/*.webp (問題の画像) と data_src/past.json (出典・正解・選択肢の数・ページ)。
PDFは IPA の公式サイトから past_src/ にダウンロードしておく(リポジトリには含めない)。
IPAの過去問は、出典を明記すれば許諾・使用料なしで教育目的に使える(IPA「試験に関するよくある質問」)。"""
import io
import json
import re
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageOps

HERE = Path(__file__).parent
APP = HERE.parent
SRC = APP / "past_src"
IMG = APP / "past" / "img"
KANA = "アイウエオカキクケコ"
DPI = 150

# (セットid, 問題PDF, 解答PDF, 科目, 出典の表記)
SETS = [
    ("r05a", "2023r05_fe_kamoku_a", "a", "令和5年度 基本情報技術者試験 公開問題 科目A"),
    ("r05b", "2023r05_fe_kamoku_b", "b", "令和5年度 基本情報技術者試験 公開問題 科目B"),
    ("r06a", "2024r06_fe_kamoku_a", "a", "令和6年度 基本情報技術者試験 公開問題 科目A"),
    ("r06b", "2024r06_fe_kamoku_b", "b", "令和6年度 基本情報技術者試験 公開問題 科目B"),
    ("r07a", "2025r07_fe_kamoku_a", "a", "令和7年度 基本情報技術者試験 公開問題 科目A"),
    ("r07b", "2025r07_fe_kamoku_b", "b", "令和7年度 基本情報技術者試験 公開問題 科目B"),
    ("r08a", "2026r08_fe_kamoku_a", "a", "令和8年度 基本情報技術者試験 公開問題 科目A"),
    ("r08b", "2026r08_fe_kamoku_b", "b", "令和8年度 基本情報技術者試験 公開問題 科目B"),
    ("sma", "fe_kamoku_a_set_sample", "a", "基本情報技術者試験 科目A サンプル問題セット"),
    ("smb", "fe_kamoku_b_set_sample", "b", "基本情報技術者試験 科目B サンプル問題セット"),
]
# 旧サンプル問題(科目B 6問)は、解答例が問題と同じPDFの末尾にある
OLD_B = ("smb0", "fe_kamoku_b_sample", "b", "基本情報技術者試験 科目B サンプル問題（2022年4月公表）")


def heads(doc):
    out = []
    for i, page in enumerate(doc):
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                t = "".join(s["text"] for s in l["spans"]).strip()
                m = re.match(r"^問\s*(\d+)", t)
                if m and l["bbox"][0] < 120:
                    out.append((int(m.group(1)), i, l["bbox"][1]))
    return out


def has_content(page, y0, y1):
    """ページ番号以外の文字や図が y0〜y1 にあるか"""
    for b in page.get_text("blocks"):
        if b[1] < y1 and b[3] > y0 and not re.fullmatch(r"[\s－\-–—\d]*", b[4]) and "余白" not in b[4]:
            return True
    if "メモ用紙" in re.sub(r"\s", "", page.get_text()):   # 問題の間に挟まる「〔 メ モ 用 紙 〕」のページ
        return False
    return any(d["rect"].y0 < y1 and d["rect"].y1 > y0 for d in page.get_drawings())


def render(page, y0, y1):
    r = page.rect
    clip = pymupdf.Rect(30, y0, r.width - 30, y1)
    pix = page.get_pixmap(dpi=DPI, clip=clip, colorspace=pymupdf.csGRAY)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    box = ImageOps.invert(im).point(lambda v: 255 if v > 24 else 0).getbbox()
    if not box:
        return None
    return im.crop((0, max(0, box[1] - 8), im.width, min(im.height, box[3] + 10)))


def answers(text):
    """解答例のテキストから {問番号: 正解} を作る"""
    toks = [t.strip() for t in text.split("\n") if t.strip()]
    out = {}
    for i, t in enumerate(toks):
        m = re.fullmatch(r"問\s*(\d+)(?:\s+(\S+))?", t)
        if not m:
            continue
        a = m.group(2) or (toks[i + 1] if i + 1 < len(toks) else "")
        if a and a[0] in KANA and int(m.group(1)) not in out:
            out[int(m.group(1))] = a
    return out


def n_options(text, part):
    if part == "a":
        return 4
    labels = set(re.findall(r"(?m)^\s*([アイウエオカキクケコ])\s", text))
    labels |= set(re.findall(r"\s([アイウエオカキクケコ])\s+(?=\S)", text))
    n = 0
    for k in KANA:
        if k in labels:
            n = KANA.index(k) + 1
        else:
            break
    return n


def build_set(sid, stem, part, label, ans_text=None, stop_page=None):
    doc = pymupdf.open(SRC / f"{stem}_qs.pdf" if (SRC / f"{stem}_qs.pdf").exists() else SRC / f"{stem}.pdf")
    if ans_text is None:
        ans_text = "\n".join(p.get_text() for p in pymupdf.open(SRC / f"{stem}_ans.pdf"))
    ans = answers(ans_text)
    hs = heads(doc)
    last_page = stop_page if stop_page is not None else doc.page_count
    foot = doc[0].rect.height - 52   # ページ番号より上
    items = []
    for k, (no, pg, y) in enumerate(hs):
        nxt = hs[k + 1] if k + 1 < len(hs) else (None, last_page, None)
        segs = []
        p = pg
        while True:
            y0 = y - 6 if p == pg else 40
            if p == nxt[1]:
                y1 = nxt[2] - 6
            else:
                y1 = foot
            if p < doc.page_count and y1 > y0 and has_content(doc[p], y0, y1):
                segs.append((p, y0, y1))
            if p >= nxt[1] or p + 1 >= last_page:
                break
            p += 1
        imgs, text = [], ""
        for j, (p, y0, y1) in enumerate(segs):
            im = render(doc[p], y0, y1)
            if im is None or im.height < 60:   # 次の問題の分野名だけ等、1行だけの切れ端は捨てる
                continue
            name = f"{sid}-{no:02d}-{j + 1}.webp"
            im.save(IMG / name, "WEBP", quality=72, method=6)
            imgs.append({"src": f"past/img/{name}", "w": im.width, "h": im.height})
            text += doc[p].get_text(clip=pymupdf.Rect(0, y0, doc[p].rect.width, y1))
        assert no in ans, f"{sid} 問{no}: 解答例に正解がない"
        n = n_options(text, part)
        a = ans[no]
        assert len(a) == 1 and KANA.index(a) < n, f"{sid} 問{no}: 正解 {a} が選択肢の数 {n} を超える"
        items.append({"id": f"{sid}-{no:02d}", "set": sid, "no": no, "part": part, "src": f"出典：{label} 問{no}",
                      "ans": KANA.index(a), "n": n, "imgs": imgs, "text": text})
    assert [x["no"] for x in items] == list(range(1, len(items) + 1)), f"{sid}: 問番号が連続していない"
    return items


IMG.mkdir(parents=True, exist_ok=True)
for f in IMG.glob("*.webp"):
    f.unlink()
out = []
for sid, stem, part, label in SETS:
    out += build_set(sid, stem, part, label)
# 旧サンプルは問題と解答例が同じPDF。解答例のページ(「解答例」の文字があるページ以降)は問題に含めない
old = pymupdf.open(SRC / f"{OLD_B[1]}.pdf")
ans_pages = [i for i, p in enumerate(old) if "解答例" in p.get_text() or "正解" in p.get_text()]
out += build_set(*OLD_B, ans_text="\n".join(old[i].get_text() for i in ans_pages), stop_page=ans_pages[0] if ans_pages else None)
(HERE / "past.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
size = sum(f.stat().st_size for f in IMG.glob("*.webp"))
sys.stdout.reconfigure(encoding="utf-8")
for sid in dict.fromkeys(x["set"] for x in out):
    xs = [x for x in out if x["set"] == sid]
    print(sid, len(xs), "問", "正解", "".join(KANA[x["ans"]] for x in xs), "選択肢数", "".join(str(x["n"]) for x in xs), "画像", sum(len(x["imgs"]) for x in xs))
print(f"計 {len(out)}問 / 画像 {size / 1e6:.1f}MB")
