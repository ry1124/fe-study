# -*- coding: utf-8 -*-
"""テキスト(fe.md)・科目Aの問題(kamoku_a.txt)・科目Bの問題(基礎 kamoku_b.py / 本試験レベル kamoku_b_exam.py)・計画(plan.json)から js/data.js を作る。
問題やテキストを直したらこのスクリプトを実行し、js/version.js を上げて公開する。
検算: 科目Aの V: 行を計算して正解の選択肢と照合し、科目Bは check 関数でプログラムを実際に動かして正解を確かめる。"""
import html
import ipaddress  # noqa: F401  V: 式の中で使う
import json
import math  # noqa: F401  V: 式の中で使う
import posixpath  # noqa: F401  V: 式の中で使う
import re
import sqlite3
import statistics  # noqa: F401  V: 式の中で使う
from fractions import Fraction  # noqa: F401  V: 式の中で使う
from pathlib import Path

import kamoku_b
import kamoku_b_exam

HERE = Path(__file__).parent
APP = HERE.parent
PLAN_JSON = HERE / "plan.json"   # make_plan.py が作る
KANA = "アイウエオカキク"
# 科目Bの問題の種類と、置く章。algo/sec が本試験レベル（模試に出す）、algo0/sec0 が基礎
B_KINDS = [("algo0", kamoku_b.ALGO, 3), ("sec0", kamoku_b.SEC, 12), ("algo", kamoku_b_exam.ALGO, 3), ("sec", kamoku_b_exam.SEC, 12)]
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


# ===== 解説（初心者向け。data_src/exp/*.txt に問題id ごとに書く） =====
def load_exp():
    """「## 問題id」または「## 問題id @章番号」の次の行から、次の「## 」までを1つの解説にする。改行はそのまま残す"""
    out = {}
    for f in sorted((HERE / "exp").glob("*.txt")):
        cur = None
        for line in f.read_text(encoding="utf-8").split("\n"):
            if line.startswith("#") and not line.startswith("## "):
                continue
            m = re.match(r"^## (\S+)(?: @(\d+))?\s*$", line)
            if m:
                cur = m.group(1)
                assert cur not in out, f"{f.name}: 解説 {cur} が重複している"
                out[cur] = {"ch": int(m.group(2)) if m.group(2) else None, "lines": []}
            elif cur:
                out[cur]["lines"].append(line.rstrip())
    for k, v in out.items():
        v["text"] = "\n".join(v.pop("lines")).strip()
        assert v["text"], f"解説 {k} が空"
    return out


EXP = load_exp()


def exp_of(qid):
    """科目A・科目B（オリジナル）の解説。exp/ にない問題があればビルドを止める"""
    assert qid in EXP and EXP[qid]["ch"] is None, f"{qid}: data_src/exp/ に解説がない"
    return EXP[qid]["text"]


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


def fifo(refs, frames):
    """FIFOのページフォールト回数"""
    mem, faults = [], 0
    for p in refs:
        if p not in mem:
            faults += 1
            if len(mem) == frames:
                mem.pop(0)
            mem.append(p)
    return faults


def sql_rows(setup, query):
    con = sqlite3.connect(":memory:")
    con.executescript(setup)
    rows = [r[0] for r in con.execute(query).fetchall()]
    con.close()
    return rows


EMP = ("CREATE TABLE 社員(社員番号, 部署, 給与); INSERT INTO 社員 VALUES "
       "(1,'営業',30),(2,'営業',26),(3,'開発',40),(4,'開発',36),(5,'開発',20),(6,'総務',28);")
CUST = ("CREATE TABLE 顧客(顧客番号, 氏名); CREATE TABLE 注文(注文番号, 顧客番号); "
        "INSERT INTO 顧客 VALUES (1,'a'),(2,'b'),(3,'c'),(4,'d'); INSERT INTO 注文 VALUES (10,1),(11,1),(12,3);")


def dfa(table, start, accept, s):
    """table: 状態 -> (0のときの遷移先, 1のときの遷移先)"""
    st = start
    for ch in s:
        st = table[st][int(ch)]
    return st in accept


def rec(f, n):
    def g(k):
        return f(g, k)
    return g(n)


def qs_demo():
    """科目A 第2章のキューとスタックの問題を実際に動かす"""
    q, s, out = [1, 2, 3, 4], [], []
    s.append(q.pop(0)); s.append(q.pop(0))
    q.append(5)
    s.append(q.pop(0))
    while s:
        out.append(s.pop())
    return out


def bst_path(keys, x):
    root = None
    for k in keys:
        if root is None:
            root = [k, None, None]
            continue
        n = root
        while True:
            i = 1 if k < n[0] else 2
            if n[i] is None:
                n[i] = [k, None, None]
                break
            n = n[i]
    path, n = [], root
    while n is not None:
        path.append(n[0])
        if x == n[0]:
            break
        n = n[1] if x < n[0] else n[2]
    return path


def heap_push(h, x):
    h = [None] + list(h) + [x]
    k = len(h) - 1
    while k > 1 and h[k // 2] < h[k]:
        h[k // 2], h[k] = h[k], h[k // 2]
        k //= 2
    return h[1:]


def probe(keys, size):
    table, pos = [None] * size, {}
    for k in keys:
        h = k % size
        while table[h] is not None:
            h = (h + 1) % size
        table[h] = k
        pos[k] = h
    return pos


def insertion_compares(a):
    a, c = list(a), 0
    for i in range(1, len(a)):
        x, j = a[i], i - 1
        while j >= 0:
            c += 1
            if a[j] > x:
                a[j + 1] = a[j]
                j -= 1
            else:
                break
        a[j + 1] = x
    return c


def bubble_pass(a):
    a = list(a)
    for j in range(len(a) - 1):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
    return a


def rpn(expr):
    st = []
    for t in expr.split():
        if t in "＋−×÷":
            b, a = st.pop(), st.pop()
            st.append({"＋": a + b, "−": a - b, "×": a * b, "÷": a // b}[t])
        else:
            st.append(int(t))
    return st[0]


def cpm(tasks):
    """tasks: 作業名 -> (日数, [先行作業]) のクリティカルパスの日数"""
    end = {}

    def f(t):
        if t not in end:
            d, pre = tasks[t]
            end[t] = d + max((f(p) for p in pre), default=0)
        return end[t]
    return max(f(t) for t in tasks)


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
        qid = f"p{ch:02d}-{len(bank.get(ch, [])) + 1:02d}"
        assert all(q["opts"]) and "ans" in q and q.get("exp"), f"{qid}: 選択肢・正解・解説のどれかがない「{q.get('q', '')[:20]}」"
        assert len(set(q["opts"])) == 4, f"{qid}: 同じ選択肢がある"
        if "v" in q:
            verify(qid, q.pop("v"), q["opts"], q["ans"])
            n_checked += 1
        bank.setdefault(ch, []).append({"id": qid, "t": "a", "q": q["q"], "opts": q["opts"], "ans": q["ans"], "exp": exp_of(qid)})
    return bank, n_checked


def build_b():
    out, seen = {k: [] for k, _, _ in B_KINDS}, set()
    for kind, src, _ in B_KINDS:
        for p in src:
            assert p["id"] not in seen, f"{p['id']}: 問題の id が重複している"
            seen.add(p["id"])
            assert 0 <= p["ans"] < len(p["opts"]) and len(set(p["opts"])) == len(p["opts"]), f"{p['id']}: 選択肢か正解の番号がおかしい"
            if p["check"]:
                got = p["check"]()
                assert got == p["ans"], f"{p['id']}: プログラムを動かした正解は「{p['opts'][got]}」なのに、ans は「{p['opts'][p['ans']]}」"
            elif kind.startswith("algo"):
                raise AssertionError(f"{p['id']}: アルゴリズムの問題に check がない")
            out[kind].append({"id": p["id"], "t": "b", "kind": kind, "title": p["title"], "q": p["lead"], "code": p["code"],
                              "ask": p["ask"], "opts": p["opts"], "ans": p["ans"], "exp": exp_of(p["id"]), "codeOpts": p["codeOpts"]})
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
        quiz = bank_a.get(no, []) + [q for k, _, c in B_KINDS if c == no for q in bank_b[k]]
        lead = body.strip().split("\n", 1)[0]
        chapters.append({"id": f"fe-{no:02d}", "no": no, "title": m.group(2), "lead": lead, "html": md_to_html(body), "quiz": quiz})
    return {"id": "fe", "name": "基本情報技術者", "intro": intro, "chapters": chapters}


# ===== IPAの過去問（past_build.py が作る past.json ＋ 解説 exp/past_*.txt） =====
PAST_SETS = {   # セットid -> (表示名, 本番形式の模試にするか)
    "r05a": ("令和5年度 公開問題 科目A", False), "r06a": ("令和6年度 公開問題 科目A", False),
    "r07a": ("令和7年度 公開問題 科目A", False), "r08a": ("令和8年度 公開問題 科目A", False),
    "r05b": ("令和5年度 公開問題 科目B", False), "r06b": ("令和6年度 公開問題 科目B", False),
    "r07b": ("令和7年度 公開問題 科目B", False), "r08b": ("令和8年度 公開問題 科目B", False),
    "sma": ("サンプル問題セット 科目A（60問）", True), "smb": ("サンプル問題セット 科目B（20問）", True),
    "smb0": ("サンプル問題 科目B（2022年公表）", False),
}


def build_past():
    items = json.loads((HERE / "past.json").read_text(encoding="utf-8"))
    exp = {k: v for k, v in EXP.items() if v["ch"] is not None}   # 過去問の解説は「## id @章」で書く
    ids = {x["id"] for x in items}
    assert set(exp) == ids, f"解説がない過去問 {sorted(ids - set(exp))} / 過去問にない解説 {sorted(set(exp) - ids)}"
    out = []
    for x in items:
        e = exp[x["id"]]
        assert e["text"], f"{x['id']}: 解説が空"
        assert x["set"] in PAST_SETS, f"{x['set']}: PAST_SETS にない"
        if x["part"] == "b":
            assert e["ch"] in (3, 12), f"{x['id']}: 科目Bの章は3か12"
        for im in x["imgs"]:
            assert (APP / im["src"]).exists(), f"{im['src']} がない"
        out.append({"id": x["id"], "t": "past", "part": x["part"], "set": x["set"], "no": x["no"], "src": x["src"],
                    "imgs": x["imgs"], "n": x["n"], "ans": x["ans"], "exp": e["text"],
                    "ch": f"fe-{e['ch']:02d}", "kind": ("algo" if e["ch"] == 3 else "sec") if x["part"] == "b" else None})
    sets = [{"id": k, "title": v[0], "mock": v[1], "part": next(x["part"] for x in out if x["set"] == k),
             "ids": [x["id"] for x in out if x["set"] == k]} for k, v in PAST_SETS.items()]
    return out, sets


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
                g["ids"] = [i for n in g.pop("chs", []) for i in ids_of[n]] + g.pop("bids", []) + g.pop("pids", [])
                assert g["ids"], f"{g['id']}: 対象の問題がない"
    return days


bank_a, n_checked = parse_a()
bank_b = build_b()
print("正解の位置（ア〜エ）: 科目A", rebalance([q for v in bank_a.values() for q in v])[:4],
      "/ 科目B（本試験レベル）", rebalance(bank_b["algo"] + bank_b["sec"])[:4])
subject = build_subject(bank_a, bank_b)
assert set(bank_a) <= {c["no"] for c in subject["chapters"]}, "kamoku_a.txt に存在しない章がある"
for name, chs in (("tech", TECH), ("mgmt", MGMT), ("strat", STRAT)):
    have = sum(len(bank_a.get(c, [])) for c in chs)
    assert have >= MOCK_A[name], f"模擬試験の{name}に{MOCK_A[name]}問必要だが{have}問しかない"
for k, n in MOCK_B.items():
    assert len(bank_b[k]) >= n, f"模擬試験の科目B {k} に{n}問必要"
past, past_sets = build_past()
plan = build_plan(subject)
for p_ in plan:
    assert set(p_.get("past", [])) <= set(PAST_SETS), f"{p_['n']}日目: 存在しない過去問のセット"
mock = {"a": {"tech": TECH, "mgmt": MGMT, "strat": STRAT, "n": MOCK_A, "min": 90},
        "b": {"n": MOCK_B, "min": 100}}
data = {"subjects": [subject], "plan": plan, "mock": mock, "past": past, "pastSets": past_sets}
(APP / "js" / "data.js").write_text(
    "// build_data.py が作るデータ(手で編集しない)\nconst FE_DATA = " + json.dumps(data, ensure_ascii=False) + ";\n",
    encoding="utf-8")
na = sum(len(v) for v in bank_a.values())
print(f"過去問 {len(past)}問（科目A {sum(x['part'] == 'a' for x in past)}・科目B {sum(x['part'] == 'b' for x in past)}、全問に解説）")
print(f"章 {len(subject['chapters'])} / 科目A {na}問（うち検算 {n_checked}問） / 科目B 本試験レベル：アルゴリズム {len(bank_b['algo'])}問・セキュリティ {len(bank_b['sec'])}問、"
      f"基礎：アルゴリズム {len(bank_b['algo0'])}問・セキュリティ {len(bank_b['sec0'])}問（アルゴリズムは全問を実行して検算） / 計画 {len(plan)}日")
