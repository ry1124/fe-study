# -*- coding: utf-8 -*-
"""基本情報技術者試験 1カ月合格プランを作る。
出力: data_src/plan.json(アプリ用) と 基本情報\\基本情報_1カ月の計画.xlsx(人が見る用)。
方針: 1日3時間×30日。1〜19日目でテキストを1周しながら科目Bのトレースをほぼ毎日解く / 7・14・20日目に関門 /
21〜29日目に模擬試験とIPAの過去問(科目Aと科目Bは別の日。1日3時間に収めるため) / 30日目に受験(CBT)。
日付は持たない(1日目をいつにするかはアプリで選ぶ)。"""
import json
import os
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).parent
OUT_JSON = HERE / "plan.json"
OUT_XLSX = HERE.parent.parent / "基本情報" / "基本情報_1カ月の計画.xlsx"
DRILL = "科目Aドリル20問（アプリの「今日」から。30分）"
REDO = "「間違えた問題」を、理由を説明できるまで解き直す"
A_ALL = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11]


def g(gid, label, typ, target, **kw):
    # typ: rate=問題の正答率(自動。chs=科目Aの章 / bids=科目Bの問題) / mock=模擬試験の直近の点数(自動) / score=本番の点数(入力)
    return dict({"id": gid, "label": label, "type": typ, "target": target}, **kw)


def b(*nums, s=()):
    """基礎の科目B（アルゴリズム b・セキュリティ s）"""
    return [f"b{n:02d}" for n in nums] + [f"s{n:02d}" for n in s]


def x(*nums, s=()):
    """本試験レベルの科目B（アルゴリズム x・セキュリティ y）"""
    return [f"x{n:02d}" for n in nums] + [f"y{n:02d}" for n in s]


def read(ch, t="1時間"):
    return f"第{ch}章を読み、例題を自分の手で解く（{t}）"


def quiz(ch, t="45分"):
    return f"第{ch}章の科目A問題を解き、解説を読む（{t}）"


plan = [
    # ===== 1週目：基礎理論・アルゴリズム・擬似言語・コンピュータ =====
    {"n": 1, "phase": "1週目・基礎", "theme": "試験の予約・基礎理論（第1章）", "chs": [1],
     "todo": ["試験を30日目で予約する（IPAの公式サイトからCBTの申込み。会場の空きと締切りを確認。20分）",
              "「このテキストの使い方」を読み、試験の形をつかむ（10分）",
              read(1, "1.5時間"),
              quiz(1, "1時間")],
     "memo": "⚠️ 予約は今日中に。CBT試験は2026年12月28日以降に休止の予定なので、それまでに受ける。2進数・16進数の変換は、毎日ドリルで手を動かす"},
    {"n": 2, "phase": "1週目・基礎", "theme": "アルゴリズムとデータ構造（第2章）", "chs": [2],
     "todo": ["昨日の" + REDO + "（20分）",
              read(2, "1.5時間"),
              quiz(2, "1時間"),
              "スタック・キュー・2分探索の動きを、紙に図を書いて説明してみる（10分）"],
     "memo": "第2章は科目Bの土台。整列（ソート）と探索の手順は、図を書いて追えるようにする"},
    {"n": 3, "phase": "1週目・基礎", "theme": "擬似言語の読み方（第3章）", "chs": [3], "b": b(1, 2, 3, 4),
     "todo": [DRILL,
              "第3章を読み、例題のトレース表を自分で書き直す（1.5時間）",
              "科目Bの基礎問題 b01〜b04を1問15分で解く。必ずメモにトレース表を書く（1時間）"],
     "memo": "科目Bは最初は時間がかかって当たり前。今は速さより「表を書いて1行ずつ追う」ことを身につける"},
    {"n": 4, "phase": "1週目・基礎", "theme": "擬似言語のトレース練習", "chs": [], "b": b(5, 6, 7, 8, 9, 10),
     "todo": [DRILL,
              "第3章の決まり（mod・要素番号は1から・and/orの順番）を見直す（15分）",
              "科目Bの基礎問題 b05〜b10を1問15分で解く（1.5時間）",
              "×の問題を、トレース表を書いて解き直す（45分）"],
     "memo": "×の問題は、どの行で自分の表と正解がずれたかを探す。そこが弱点"},
    {"n": 5, "phase": "1週目・基礎", "theme": "コンピュータの仕組み（第4章）", "chs": [4], "b": b(11, 12, 13, 14),
     "todo": [DRILL,
              read(4),
              quiz(4),
              "科目Bの基礎問題 b11〜b14を1問12分で解く（45分）"],
     "memo": "キャッシュの実効アクセス時間・クロックとCPIの計算は、答えを見ずに解けるまでくり返す"},
    {"n": 6, "phase": "1週目・基礎", "theme": "システム構成・ソフトウェア（第5章）", "chs": [5], "b": b(15, 16, 17, 18),
     "todo": [DRILL,
              read(5),
              quiz(5),
              "科目Bの基礎問題 b15〜b18を1問12分で解く（45分）"],
     "memo": "稼働率は「直列は掛け算、並列は1−(止まる確率の積)」。図を書いてから式にする"},
    {"n": 7, "phase": "1週目・基礎", "theme": "1週目の復習・関門①", "chs": [], "b": b(19, 20, 21, 22, 23, 24),
     "todo": ["科目Bの基礎問題 b19〜b24を1問10分で解く（1時間）",
              "1週目の" + REDO + "（1時間）",
              DRILL,
              "稼働率・キャッシュ・基数変換の計算を、答えを見ずに解き直す（30分）"],
     "memo": "関門に届かなければ、8日目の最初の1時間を×の解き直しにあてる",
     "gate": [g("g1-a", "科目A 第1・2・4・5章の正答率", "rate", 70, chs=[1, 2, 4, 5]),
              g("g1-b", "科目B 基礎問題 b01〜b24の正答率", "rate", 70, bids=b(*range(1, 25)))]},
    # ===== 2週目：データベース・ネットワーク・セキュリティ・本試験レベルの科目B =====
    {"n": 8, "phase": "2週目・応用", "theme": "データベース（第6章）", "chs": [6], "b": x(1, 2),
     "todo": [DRILL,
              read(6),
              quiz(6),
              "科目B 本試験レベル x01・x02を1問15分で解く（30分）"],
     "memo": "SQLは、表を書いて「どの行が残るか」を1行ずつ確かめる。本試験レベルの科目Bは空欄の組合せ問題。選択肢を当てはめて小さい例で動かす"},
    {"n": 9, "phase": "2週目・応用", "theme": "ネットワーク（第7章）", "chs": [7], "b": x(3, 4),
     "todo": [DRILL,
              read(7),
              quiz(7),
              "科目B 本試験レベル x03・x04を1問15分で解く（30分）"],
     "memo": "サブネットの計算（ホスト部のビット数→台数）と伝送時間（バイトは×8）は毎回出ると思って練習する"},
    {"n": 10, "phase": "2週目・応用", "theme": "情報セキュリティ（第8章）", "chs": [8], "b": b(s=range(1, 9)),
     "todo": [DRILL,
              read(8),
              quiz(8),
              "科目Bの基礎問題 セキュリティ s01〜s08を1問5分で解く（40分）"],
     "memo": "公開鍵暗号は「暗号化は受け取る人の公開鍵、署名は自分の秘密鍵」。ここは必ず言えるようにする"},
    {"n": 11, "phase": "2週目・応用", "theme": "科目B セキュリティの解き方（第12章）", "chs": [12], "b": x(s=range(1, 7)),
     "todo": [DRILL,
              "第12章を読む（40分）",
              "科目B 本試験レベルのセキュリティ y01〜y06を1問8分で解き、解説を読む（1時間）",
              "第6〜8章の" + REDO + "（50分）"],
     "memo": "セキュリティの事例問題は、設問を先に読んでから本文を読む。本番は1問4分が目標"},
    {"n": 12, "phase": "2週目・応用", "theme": "科目B 本試験レベルの演習①", "chs": [], "b": x(5, 6, 7, 8),
     "todo": [DRILL,
              "科目B 本試験レベル x05〜x08を1問15分で解く（1時間）",
              "×の問題を、トレース表を書いて解き直す（45分）",
              "第6章のSQLの問題を、答えを見ずに解き直す（45分）"],
     "memo": "1問に20分以上かかったら、解説を読んで「どこから読めば早かったか」を確認する"},
    {"n": 13, "phase": "2週目・応用", "theme": "科目B 本試験レベルの演習②", "chs": [], "b": x(9, 10, 11, 12),
     "todo": [DRILL,
              "科目B 本試験レベル x09〜x12を1問12分で解く（50分）",
              "×の問題を、トレース表を書いて解き直す（45分）",
              "第7・8章の" + REDO + "（55分）"],
     "memo": "時間を計って解く。1問12分に近づけていく"},
    {"n": 14, "phase": "2週目・応用", "theme": "2週目の復習・関門②", "chs": [], "b": [],
     "todo": ["第1〜8章の" + REDO + "（1.5時間）",
              "科目B x01〜x12・y01〜y06のうち×の問題を解き直す（1時間）",
              DRILL],
     "memo": "関門に届かなければ、15日目の最初の1時間を×の解き直しにあてる。第3章の擬似言語の決まりは毎朝5分見直す",
     "gate": [g("g2-a", "科目A 第1〜8章の正答率", "rate", 70, chs=[1, 2, 4, 5, 6, 7, 8]),
              g("g2-b", "科目B 本試験レベル x01〜x12・y01〜y06の正答率", "rate", 60, bids=x(*range(1, 13), s=range(1, 7)))]},
    # ===== 3週目：開発・マネジメント・ストラテジ・科目Bの仕上げ =====
    {"n": 15, "phase": "3週目・仕上げ", "theme": "開発技術（第9章）", "chs": [9], "b": x(13, 14),
     "todo": [DRILL,
              read(9),
              quiz(9),
              "科目B 本試験レベル x13・x14を1問12分で解く（25分）"],
     "memo": "テストの種類（ブラックボックス・ホワイトボックス）と、開発の進め方（ウォーターフォール・アジャイル）は違いを言えるようにする"},
    {"n": 16, "phase": "3週目・仕上げ", "theme": "マネジメント（第10章）", "chs": [10], "b": x(15, 16),
     "todo": [DRILL,
              read(10),
              quiz(10),
              "科目B 本試験レベル x15・x16を1問12分で解く（25分）"],
     "memo": "アローダイアグラムとEVMの計算は確実に取る。用語問題は1問30秒で答えられるまで回す"},
    {"n": 17, "phase": "3週目・仕上げ", "theme": "ストラテジ（第11章）", "chs": [11], "b": x(17, 18),
     "todo": [DRILL,
              read(11),
              quiz(11),
              "科目B 本試験レベル x17・x18を1問12分で解く（25分）"],
     "memo": "損益分岐点・利益の計算と、法律（著作権・派遣と請負）は毎年出る"},
    {"n": 18, "phase": "3週目・仕上げ", "theme": "科目B 本試験レベルの演習③", "chs": [], "b": x(19, 20, 21, s=range(7, 10)),
     "todo": [DRILL,
              "科目B 本試験レベル x19〜x21を1問10分、セキュリティ y07〜y09を1問5分で解く（45分）",
              "×の問題を、トレース表を書いて解き直す（45分）",
              "第10・11章の用語問題を、1問30秒で答えられるまで回す（1時間）"],
     "memo": "科目Bの目標は1問8〜10分。本番は100分で20問"},
    {"n": 19, "phase": "3週目・仕上げ", "theme": "科目B 本試験レベルの演習④", "chs": [], "b": x(22, 23, 24, s=range(10, 13)),
     "todo": [DRILL,
              "科目B 本試験レベル x22〜x24を1問10分、セキュリティ y10〜y12を1問5分で解く（45分）",
              "×の問題を、トレース表を書いて解き直す（45分）",
              "第9〜11章の" + REDO + "（1時間）"],
     "memo": "これで科目Bの本試験レベル36問がひと通り終わる。明日の関門に向けて×を減らす"},
    {"n": 20, "phase": "3週目・仕上げ", "theme": "全範囲の総復習・関門③", "chs": [], "b": [],
     "todo": ["科目Aの" + REDO + "（1.5時間）",
              "科目B 本試験レベルの×の問題を解き直す（1時間）",
              DRILL],
     "memo": "関門に届かなければ、21・22日目の模試の後の見直しを長めにとり、×の解き直しを続ける",
     "gate": [g("g3-a", "科目A 全問の正答率", "rate", 75, chs=A_ALL),
              g("g3-b", "科目B 本試験レベル全問の正答率", "rate", 70, bids=x(*range(1, 25), s=range(1, 13)))]},
    # ===== 4週目：模擬試験・IPAの過去問・受験 =====
    {"n": 21, "phase": "4週目・模試", "theme": "模擬試験 第1回 科目A", "chs": [], "b": [],
     "todo": ["本番形式の模擬試験 第1回 科目A（アプリ。60問 90分）を時間を計って解く（1.5時間）",
              "模試で間違えた問題の解説を読み、テキストで確認する（1時間）",
              DRILL],
     "memo": "時間配分の練習。1問1分30秒、分からない問題は印を付けて先へ。空欄は作らない"},
    {"n": 22, "phase": "4週目・模試", "theme": "模擬試験 第1回 科目B", "chs": [], "b": [],
     "todo": ["本番形式の模擬試験 第1回 科目B（アプリ。20問 100分）を時間を計って解く（1時間40分）",
              "模試で間違えた問題を、トレース表を書いて解き直す（1時間20分）"],
     "memo": "最後のセキュリティ4問を先に15分で解き、残りをアルゴリズム16問に使う練習をする"},
    {"n": 23, "phase": "4週目・模試", "theme": "IPA公開問題 科目B", "chs": [], "b": [], "past": ["r05b", "r06b", "r07b", "r08b"],
     "todo": ["過去問：令和5〜8年度の公開問題 科目B（24問）を1問6分で解く（アプリの「過去問」から。2.5時間）",
              "×の問題の解説を読む（30分）"],
     "memo": "本物の問題に慣れる日。×の問題は明日以降にもう一度解く"},
    {"n": 24, "phase": "4週目・模試", "theme": "IPA公開問題 科目A", "chs": [], "b": [], "past": ["r05a", "r06a", "r07a", "r08a"],
     "todo": ["過去問：令和5〜8年度の公開問題 科目A（80問）を1問1分で解く（1時間20分）",
              "×の問題の解説を読み、テキストで確認する（1時間10分）",
              DRILL],
     "memo": "知らない用語が出たら、テキストのどの章の話かを確かめておく"},
    {"n": 25, "phase": "4週目・模試", "theme": "過去問模試 科目A（サンプル問題）", "chs": [], "b": [], "past": ["sma"],
     "todo": ["過去問模試：IPAのサンプル問題 科目A（60問 90分）を時間を計って解く（1.5時間）",
              "間違えた問題の解説を読み、テキストで確認する（1時間）",
              DRILL],
     "memo": "初めて解く本物の問題なので、本番の実力に近い。点数は関門に自動で入る",
     "gate": [g("g4-a", "過去問模試 科目A（サンプル問題・1000点換算）", "mock", 600, part="a", set="sma")]},
    {"n": 26, "phase": "4週目・模試", "theme": "過去問模試 科目B（サンプル問題）", "chs": [], "b": [], "past": ["smb"],
     "todo": ["過去問模試：IPAのサンプル問題 科目B（20問 100分）を時間を計って解く（1時間40分）",
              "間違えた問題を、トレース表を書いて解き直す（1時間20分）"],
     "memo": "600点に届かなければ、27〜29日目を×の解き直し中心にし、受験日を延ばすことも考える（変更の期限は申込みサイトで確認）",
     "gate": [g("g4-b", "過去問模試 科目B（サンプル問題・1000点換算）", "mock", 600, part="b", set="smb")]},
    {"n": 27, "phase": "4週目・模試", "theme": "弱点の総ざらい", "chs": [], "b": [],
     "todo": ["模試と過去問の×の問題を、もう一度解く（1.5時間）",
              REDO + "（1時間）",
              DRILL],
     "memo": "「間違えた問題」を0問に近づける。同じ問題を2回まちがえたら、テキストのその節を読み直す"},
    {"n": 28, "phase": "4週目・模試", "theme": "模擬試験 第2回 科目A", "chs": [], "b": [],
     "todo": ["本番形式の模擬試験 第2回 科目A（60問 90分）を解く（1.5時間）",
              "間違えた問題の解説を読み、テキストで確認する（1時間）",
              DRILL],
     "memo": "第1回と点数を比べる。時間が余ったら、見直しの手順も本番どおりに練習する"},
    {"n": 29, "phase": "4週目・模試", "theme": "模擬試験 第2回 科目B・直前の確認", "chs": [13], "b": [],
     "todo": ["本番形式の模擬試験 第2回 科目B（20問 100分）を解く（1時間40分）",
              "間違えた問題の解説を読む（40分）",
              "第13章「本番の解き方」を読み、直前の確認リストを全部言えるようにする（40分）"],
     "memo": "明日は受験日。持ち物（顔写真付きの本人確認書類）と会場までの道を確認し、早めに寝る"},
    {"n": 30, "phase": "受験日", "theme": "受験日（CBT）", "chs": [13], "b": [],
     "todo": ["第13章の「直前の確認リスト」を読む（20分）",
              "科目Aドリル20問を解き、×を確認する（30分）",
              "科目Bの「間違えた問題」を2〜3問トレースし直して、手を慣らす（40分）",
              "受験（科目A 90分・科目B 100分）。持ち物：顔写真付きの本人確認書類、申込みの確認メール"],
     "memo": "科目Bは最後のセキュリティ4問を先に15分で解き、残り85分をアルゴリズム16問に使う。1問8分を超えたら印を付けて先へ",
     "gate": [g("g5-a", "本番 科目A（1000点満点）", "score", 600), g("g5-b", "本番 科目B（1000点満点）", "score", 600)]},
]
for p in plan:
    p.setdefault("gate", None)
    p.setdefault("past", [])
    p.setdefault("memo", "")
    p.setdefault("b", [])
    assert len(p["todo"]) <= 5, p["n"]
    p["todo"] = "\n".join(f"{'①②③④⑤'[i]}{t}" for i, t in enumerate(p["todo"]))
assert [p["n"] for p in plan] == list(range(1, 31))
OUT_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=0), encoding="utf-8")


def gate_text(x):
    unit = "%" if x["type"] == "rate" else "点"
    return f"{x['label']}：{x['target']}{unit}以上"


# ===== Excel(人が見る用) =====
wb = Workbook()
ws = wb.active
ws.title = "1カ月の計画"
thin = Side(style="thin", color="BBBBBB")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
base = Font(name="メイリオ", size=10)
wrap = Alignment(wrap_text=True, vertical="center")
ws["A1"] = "基本情報技術者試験 1カ月合格プラン（1日3時間×30日）"
ws["A1"].font = Font(name="メイリオ", size=16, bold=True, color="12805F")
ws["A2"], ws["C2"] = "1日目の日付", "←ここに1日目の日付を入れると、日付の列が埋まります"
ws["A2"].font = Font(name="メイリオ", bold=True)
ws["B2"].number_format = "yyyy/mm/dd"
ws["B2"].fill = PatternFill("solid", fgColor="FFF2CC")
headers = ["日目", "日付", "時期", "テーマ", "やること", "完了", "メモ", "関門"]
widths = [6, 13, 12, 36, 72, 6, 38, 36]
for c, (h, w) in enumerate(zip(headers, widths), 1):
    cell = ws.cell(row=4, column=c, value=h)
    cell.fill, cell.font = PatternFill("solid", fgColor="12805F"), Font(bold=True, color="FFFFFF", name="メイリオ")
    cell.alignment, cell.border = Alignment(horizontal="center", vertical="center"), border
    ws.column_dimensions[cell.column_letter].width = w
for i, p in enumerate(plan, 5):
    gate = "\n".join(gate_text(x) for x in (p["gate"] or []))
    vals = [f"{p['n']}日目", f'=IF($B$2="","",$B$2+{p["n"] - 1})', p["phase"], p["theme"], p["todo"], "", p["memo"], gate]
    for c, v in enumerate(vals, 1):
        cell = ws.cell(row=i, column=c, value=v)
        cell.font, cell.alignment, cell.border = base, wrap, border
    ws.cell(row=i, column=2).number_format = "m/d(aaa)"
    for c in (1, 2, 6):
        ws.cell(row=i, column=c).alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[i].height = 17 * (p["todo"].count("\n") + 1) + 14
dv = DataValidation(type="list", formula1='"✓"', allow_blank=True)
ws.add_data_validation(dv)
dv.add(f"F5:F{4 + len(plan)}")
ws.freeze_panes = "A5"
ws.cell(row=6 + len(plan), column=1, value="ふだんはアプリを使う：https://ry1124.github.io/fe-study/").font = Font(name="メイリオ", color="12805F")
os.makedirs(OUT_XLSX.parent, exist_ok=True)
wb.save(OUT_XLSX)
print(f"{len(plan)}日分 → {OUT_JSON.name} / {OUT_XLSX}")
