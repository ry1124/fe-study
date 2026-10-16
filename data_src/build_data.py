# -*- coding: utf-8 -*-
"""テキスト(fe.md)・科目Aの問題(kamoku_a.txt)・科目Bの問題(kamoku_b.py)・計画(plan.json)から js/data.js を作る。
問題やテキストを直したらこのスクリプトを実行し、js/version.js を上げて公開する。
検算: 科目Aの V: 行を計算して正解の選択肢と照合し、科目Bは check 関数でプログラムを実際に動かして正解を確かめる。"""
import html
import ipaddress  # noqa: F401  V: 式の中で使う
import json
import math  # noqa: F401  V: 式の中で使う
import re
import sqlite3
from pathlib import Path

from kamoku_b import ALGO, SEC

HERE = Path(__file__).parent
APP = HERE.parent
PLAN_JSON = HERE / "plan.json"   # make_plan.py が作る
KANA = "アイウエオカキク"
B_CH = {"algo": 3, "sec": 12}     # 科目Bの問題を置く章
TECH, MGMT, STRAT = [1, 2, 4, 5, 6, 7, 8, 9], [10], [11]
MOCK_A = {"tech": 41, "mgmt": 7, "strat": 12}   # 本番の科目Aの分野別の出題数
MOCK_B = {"algo": 16, "sec": 4}


# ===== テキスト =====
def inline(text):
    t = html.escape(text, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)


def md_to_html(md):
    """このテキストで使っている書式(見出し・段落・箇条書き・番号付き・入れ子・表・太字・コード)だけを変換する"""
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("```"):
            i += 1
            code = []
            while not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append(f"<pre class='code'>{html.escape(chr(10).join(code), quote=False)}</pre>")
        elif ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:])}</h3>")
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r"-+", c) for c in r)]
            t = "<div class='table-wrap'><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(t + "</tbody></table></div>")
        elif re.match(r"^(- |\d+\. )", ln):
            items = []
            while i < len(lines) and re.match(r"^( {2,4})?(- |\d+\. )", lines[i]):
                sub = lines[i].startswith("  ")
                m = re.match(r"^(?: {2,4})?(- |\d+\. )(.*)$", lines[i])
                kind = "ul" if m.group(1) == "- " else "ol"
                if sub and items:
                    items[-1]["sub"].append((kind, m.group(2)))
                else:
                    items.append({"kind": kind, "text": m.group(2), "sub": []})
                i += 1
            tag = items[0]["kind"]
            s = f"<{tag}>"
            for it in items:
                s += f"<li>{inline(it['text'])}"
                if it["sub"]:
                    st = it["sub"][0][0]
                    s += f"<{st}>" + "".join(f"<li>{inline(x)}</li>" for _, x in it["sub"]) + f"</{st}>"
                s += "</li>"
            out.append(s + f"</{tag}>")
        else:
            out.append(f"<p>{inline(ln)}</p>")
            i += 1
    return "\n".join(out)


# ===== 科目Aの検算に使う関数 =====
def lru(refs, frames):
    """LRUのページフォールト回数"""
    mem, faults = [], 0
    for p in refs:
        if p in mem:
            mem.remove(p)
        else:
            faults += 1
            if len(mem) == frames:
                mem.pop(0)
        mem.append(p)
    return faults


def sql(setup, query):
    """SQLを実際に実行し、結果を「と」でつないだ文字列(1行1列なら値)にする"""
    con = sqlite3.connect(":memory:")
    con.executescript(setup)
    rows = con.execute(query).fetchall()
    con.close()
    if len(rows) == 1 and len(rows[0]) == 1 and isinstance(rows[0][0], int):
        return rows[0][0]
    return "と".join(str(r[0]) for r in rows)


def numbers(text):
    return [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*(?:\.\d+)?", text.replace("−", "-"))]


def verify(qid, expr, opts, ans):
    v = eval(expr)
    if isinstance(v, str):
        hit = [i for i, o in enumerate(opts) if o == v or (v in o and len(v) > 3)]
        exact = [i for i, o in enumerate(opts) if o == v]
        hit = exact or hit
    else:
        hit = [i for i, o in enumerate(opts) if any(abs(n - v) < 1e-9 * max(1, abs(v)) for n in numbers(o))]
    assert hit == [ans], f"{qid}: 検算の値 {v!r} が正解「{opts[ans]}」と合わない（一致した選択肢: {[opts[i] for i in hit]}）"
    return v


def parse_a():
    bank, ch = {}, None
    text = "\n".join(l for l in (HERE / "kamoku_a.txt").read_text(encoding="utf-8").split("\n") if not l.startswith("#"))
    n_checked = 0
    for block in re.split(r"\n\s*\n", text):
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if lines and lines[0].startswith("@"):
            ch = int(lines.pop(0)[1:])
        if not lines:
            continue
        q = {"opts": [None] * 4}
        for l in lines:
            k, v = l.split(":", 1)
            v = v.strip()
            if k == "Q": q["q"] = v.replace("\\n", "\n")
            elif k in KANA[:4]: q["opts"][KANA.index(k)] = v
            elif k == "A": q["ans"] = KANA.index(v)
            elif k == "E": q["exp"] = v
            elif k == "V": q["v"] = v
            else: raise ValueError(f"知らない行: {l}")
        qid = f"a{ch:02d}-{len(bank.get(ch, [])) + 1:02d}"
        assert all(q["opts"]) and "ans" in q and q.get("exp"), f"{qid}: 選択肢・正解・解説のどれかがない「{q.get('q', '')[:20]}」"
        assert len(set(q["opts"])) == 4, f"{qid}: 同じ選択肢がある"
        if "v" in q:
            verify(qid, q.pop("v"), q["opts"], q["ans"])
            n_checked += 1
        bank.setdefault(ch, []).append({"id": qid, "t": "a", "q": q["q"], "opts": q["opts"], "ans": q["ans"], "exp": q["exp"]})
    return bank, n_checked


def build_b():
    out = {"algo": [], "sec": []}
    for kind, src in (("algo", ALGO), ("sec", SEC)):
        for p in src:
            assert 0 <= p["ans"] < len(p["opts"]) and len(set(p["opts"])) == len(p["opts"]), f"{p['id']}: 選択肢か正解の番号がおかしい"
            if p["check"]:
                got = p["check"]()
                assert got == p["ans"], f"{p['id']}: プログラムを動かした正解は「{p['opts'][got]}」なのに、ans は「{p['opts'][p['ans']]}」"
            elif kind == "algo":
                raise AssertionError(f"{p['id']}: アルゴリズムの問題に check がない")
            out[kind].append({"id": p["id"], "t": "b", "kind": kind, "title": p["title"], "q": p["lead"], "code": p["code"],
                              "ask": p["ask"], "opts": p["opts"], "ans": p["ans"], "exp": p["exp"], "codeOpts": p["codeOpts"]})
    return out


# ===== 正解の位置をそろえる =====
# 問題ファイルは正解がア・イに偏っている（エはほとんど正解にならない）。本番は位置がほぼ均等なので、
# 選択肢を回転させて、正解の位置がア〜エに均等に散らばるようにする。数値だけの選択肢は小さい順のまま動かさない。
# 解説の中の選択肢の記号（「アは〜」「イとエは〜」）も、新しい並びに合わせて書き換える。
LABEL = re.compile(r"(?<![ァ-ヶー])[アイウエオカキク](?![ァ-ヶー])")


def is_numeric(opts):
    return all(re.fullmatch(r"[−-]?[\d,]+(\.\d+)?", o.strip()) for o in opts)


def rebalance(items):
    count = [0] * 8
    fixed = [q for q in items if is_numeric(q["opts"])]
    for q in fixed:
        count[q["ans"]] += 1
    for q in items:
        if q in fixed:
            continue
        n = len(q["opts"])
        target = min(range(n), key=lambda i: (count[i], i))
        shift = (target - q["ans"]) % n
        q["opts"] = [q["opts"][(i - shift) % n] for i in range(n)]
        q["ans"] = target
        q["exp"] = LABEL.sub(lambda m: KANA[(KANA.index(m.group()) + shift) % n] if KANA.index(m.group()) < n else m.group(), q["exp"])
        count[target] += 1
    return count


def build_subject(bank_a, bank_b):
    md = (HERE / "fe.md").read_text(encoding="utf-8")
    sections = re.split(r"^## ", md, flags=re.M)[1:]
    intro, chapters = "", []
    for sec in sections:
        title, body = sec.split("\n", 1)
        m = re.match(r"第(\d+)章 (.+)", title)
        if not m:
            intro = md_to_html(body)
            continue
        no = int(m.group(1))
        quiz = bank_a.get(no, []) + [q for k, c in B_CH.items() if c == no for q in bank_b[k]]
        lead = body.strip().split("\n", 1)[0]
        chapters.append({"id": f"fe-{no:02d}", "no": no, "title": m.group(2), "lead": lead, "html": md_to_html(body), "quiz": quiz})
    return {"id": "fe", "name": "基本情報技術者", "intro": intro, "chapters": chapters}


# ===== 計画 =====
def build_plan(subject):
    days = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    ids_of = {c["no"]: [q["id"] for q in c["quiz"] if q["t"] == "a"] for c in subject["chapters"]}
    all_b = {q["id"] for c in subject["chapters"] for q in c["quiz"] if q["t"] == "b"}
    for p in days:
        p["ch"] = [f"fe-{n:02d}" for n in p["chs"]]
        assert set(p["b"]) <= all_b, f"{p['n']}日目: 存在しない科目Bの問題 {set(p['b']) - all_b}"
        for g in p["gate"] or []:
            if g["type"] == "rate":
                g["ids"] = [i for n in g.pop("chs", []) for i in ids_of[n]] + g.pop("bids", [])
                assert g["ids"], f"{g['id']}: 対象の問題がない"
    return days


bank_a, n_checked = parse_a()
bank_b = build_b()
print("正解の位置（ア〜エ）: 科目A", rebalance([q for v in bank_a.values() for q in v])[:4],
      "/ 科目B", rebalance(bank_b["algo"] + bank_b["sec"])[:4])
subject = build_subject(bank_a, bank_b)
assert set(bank_a) <= {c["no"] for c in subject["chapters"]}, "kamoku_a.txt に存在しない章がある"
for name, chs in (("tech", TECH), ("mgmt", MGMT), ("strat", STRAT)):
    have = sum(len(bank_a.get(c, [])) for c in chs)
    assert have >= MOCK_A[name], f"模擬試験の{name}に{MOCK_A[name]}問必要だが{have}問しかない"
for k, n in MOCK_B.items():
    assert len(bank_b[k]) >= n, f"模擬試験の科目B {k} に{n}問必要"
plan = build_plan(subject)
mock = {"a": {"tech": TECH, "mgmt": MGMT, "strat": STRAT, "n": MOCK_A, "min": 90},
        "b": {"n": MOCK_B, "min": 100}}
data = {"subjects": [subject], "plan": plan, "mock": mock}
(APP / "js" / "data.js").write_text(
    "// build_data.py が作るデータ(手で編集しない)\nconst FE_DATA = " + json.dumps(data, ensure_ascii=False) + ";\n",
    encoding="utf-8")
na = sum(len(v) for v in bank_a.values())
print(f"章 {len(subject['chapters'])} / 科目A {na}問（うち検算 {n_checked}問） / 科目B アルゴリズム {len(bank_b['algo'])}問（全問を実行して検算）・セキュリティ {len(bank_b['sec'])}問 / 計画 {len(plan)}日")
