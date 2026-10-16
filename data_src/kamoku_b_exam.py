# -*- coding: utf-8 -*-
"""科目Bの本試験レベルの問題（擬似言語のアルゴリズム24問・情報セキュリティ12問）。build_data.py が読む。
本試験と同じく、空欄は〔 a 〕〔 b 〕で表し、選択肢は空欄の字句の組合せ（6択前後）にする。
アルゴリズムの問題の check は、全ての選択肢を Python で実際に動かし、仕様どおりに動く選択肢がちょうど1つであることを確かめて、その番号を返す。
問題はすべてオリジナル（IPAのサンプル問題・公開問題の転載ではない）。"""
import itertools
import random

from kamoku_b import only, pick

ALGO = []
SEC = []
DIV = "÷ は整数の除算で、商の小数点以下を切り捨てる。"


def algo(id, title, lead, code, ask, opts, ans, exp, check, code_opts=True):
    ALGO.append({"id": id, "title": title, "lead": lead, "code": code.strip("\n"), "ask": ask, "opts": opts,
                 "ans": ans, "exp": exp, "check": check, "codeOpts": code_opts})


def sec(id, title, lead, ask, opts, ans, exp):
    SEC.append({"id": id, "title": title, "lead": lead, "code": "", "ask": ask, "opts": opts,
                "ans": ans, "exp": exp, "check": None, "codeOpts": False})


def combo(a_list, b_list):
    return [f"a：{a}　b：{b}" for a in a_list for b in b_list]


class Stop(Exception):
    """誤った選択肢で無限ループ・範囲外アクセスになったときに投げる"""


def guard(n, limit=10000):
    if n > limit:
        raise Stop


# ===== x01・x02 エラトステネスのふるい =====
SIEVE = """
○整数型の配列: prime(整数型: n)
  整数型の配列: pnList ← {}             /* 要素数0の配列 */
  論理型の配列: divisible ← {n 個の false}
  整数型: i, j
  for (i を 2 から n まで 1 ずつ増やす)
    if (〔 a 〕)
      pnList の末尾に i の値を追加する
      j ← i × i
      while (j ≦ n)
        divisible[j] ← true             /* β */
        j ← 〔 b 〕
      endwhile
    endif
  endfor
  return pnList
"""
SIEVE_LEAD = ("関数 prime は、2以上の整数 n を受け取り、n 以下の素数を小さい順に格納した配列を返す。"
              "divisible[k] が true であることは、k がそれまでに見つかった素数の倍数であることを表す。"
              "配列の要素番号は1から始まる。")


def sieve(n, a_false, step):
    div = [None] + [False] * n
    out, cnt = [], 0
    for i in range(2, n + 1):
        if (div[i] is False) == a_false:
            out.append(i)
            j = i * i
            while j <= n:
                div[j] = True
                cnt += 1
                j = {"j ＋ 1": j + 1, "j ＋ i": j + i, "j × i": j * i}[step]
    return out, cnt


def _x01():
    def primes(n):
        return [k for k in range(2, n + 1) if all(k % d for d in range(2, k))]
    res = []
    for a in (True, False):
        for b in ("j ＋ 1", "j ＋ i", "j × i"):
            res.append(all(sieve(n, a, b)[0] == primes(n) for n in range(2, 80)))
    return only(res)

algo("x01", "エラトステネスのふるい（空欄）", SIEVE_LEAD, SIEVE,
     "プログラム中の〔 a 〕と〔 b 〕に入れる正しい答えの組合せはどれか。",
     combo(["divisible[i] ＝ false", "divisible[i] ＝ true"], ["j ＋ 1", "j ＋ i", "j × i"]), 1,
     "まだどの素数の倍数でもない（divisible[i] が false の）i が素数。見つけた素数 i の倍数を、i×i から i ずつ増やしながら印を付ける（i×i より小さい倍数は、より小さい素数の倍数として印が付いている）。j × i にすると i²、i³… しか印が付かず、例えば 6 が素数と判定される。j ＋ 1 にすると i² 以降の全部に印が付く。",
     _x01)

def _x02():
    _, cnt = sieve(20, True, "j ＋ i")
    return pick(["8", "11", "13", "15", "17", "19"], cnt)

algo("x02", "エラトステネスのふるい（実行回数）", SIEVE_LEAD + "空欄〔 a 〕〔 b 〕には正しい字句が入っているものとする。", SIEVE,
     "prime(20) を実行したとき、β の行が実行される回数はどれか。",
     ["8", "11", "13", "15", "17", "19"], 2,
     "i＝2 のとき j＝4, 6, 8, …, 20 の9回。i＝3 のとき j＝9, 12, 15, 18 の4回（18 は2回目の印だが実行はされる）。i＝5 は 25 ＞ 20 なので0回。それ以降の素数も0回。計13回。",
     _x02, code_opts=False)

# ===== x03 偶数パリティ =====
def _x03():
    res = []
    for a in ("<<", ">>"):
        for b in ("or80", "and80", "or01"):
            ok = True
            for data in range(128):
                mask, cnt = 1, 0
                for _ in range(7):
                    if data & mask:
                        cnt += 1
                    mask = (mask << 1) & 0xFF if a == "<<" else mask >> 1
                r = data
                if cnt % 2 == 1:
                    r = {"or80": data | 0x80, "and80": data & 0x80, "or01": data | 0x01}[b]
                if bin(r).count("1") % 2 or (r & 0x7F) != data:
                    ok = False
                    break
            res.append(ok)
    return only(res)

algo("x03", "偶数パリティの付加",
     "関数 addParity は、下位7ビットにデータが入り最上位ビットが0である8ビット型の値 data を受け取り、"
     "8ビット全体で1の個数が偶数になるように最上位ビットを設定した値を返す（偶数パリティ）。"
     "∧ はビットごとの論理積、∨ はビットごとの論理和、<< は論理左シフト、>> は論理右シフトを表す。"
     "例えば data が 00000111 のとき、1 の個数が3（奇数）なので 10000111 を返す。",
     """
○8ビット型: addParity(8ビット型: data)
  8ビット型: mask ← 00000001
  整数型: cnt ← 0
  整数型: i
  for (i を 1 から 7 まで 1 ずつ増やす)
    if ((data ∧ mask) ≠ 00000000)
      cnt ← cnt ＋ 1
    endif
    mask ← 〔 a 〕
  endfor
  if (cnt mod 2 ＝ 1)
    return 〔 b 〕
  endif
  return data
""",
     "プログラム中の〔 a 〕と〔 b 〕に入れる正しい答えの組合せはどれか。",
     ["a：mask << 1　b：data ∨ 10000000", "a：mask << 1　b：data ∧ 10000000", "a：mask << 1　b：data ∨ 00000001",
      "a：mask >> 1　b：data ∨ 10000000", "a：mask >> 1　b：data ∧ 10000000", "a：mask >> 1　b：data ∨ 00000001"], 0,
     "mask は 00000001 から始めて、1ビットずつ上の桁へずらしながら各ビットを調べる（<< 1）。>> 1 だと2回目以降 mask が 00000000 になり、最下位ビットしか数えない。1 の個数が奇数なら最上位ビットだけを1にする（∨ 10000000）。∧ 10000000 だとデータが全部消え、∨ 00000001 だとデータの最下位ビットが変わってしまう。",
     _x03)

# ===== x04 ランレングス圧縮 =====
def _x04():
    words = ["AAABCC", "A", "AB", "ABBBBA", "ZZZZ", "ABCABC", "AABBAA"]

    def want(w):
        return "".join(f"{k}{len(list(g))}" for k, g in itertools.groupby(w))

    variants = [lambda i, c: i + c, lambda i, c: i + 1, lambda i, c: i + c - 1,
                lambda i, c: i + c + 1, lambda i, c: c, lambda i, c: c + 1]

    def run(f, w):
        s = [None] + list(w)
        n, i, out, steps = len(w), 1, "", 0
        while i <= n:
            steps += 1
            guard(steps, 100)
            cnt = 1
            while i + cnt <= n and s[i + cnt] == s[i]:
                cnt += 1
            out += s[i] + str(cnt)
            i = f(i, cnt)
        return out
    res = []
    for f in variants:
        try:
            res.append(all(run(f, w) == want(w) for w in words))
        except Stop:
            res.append(False)
    return only(res)

algo("x04", "ランレングス圧縮",
     "関数 encode は、英大文字が格納された文字型の配列 s を受け取り、同じ文字が連続する部分を「その文字」と「連続する個数」の組に置き換えた文字列を返す。"
     "例えば s が {\"A\", \"A\", \"A\", \"B\", \"C\", \"C\"} のとき、\"A3B1C2\" を返す。"
     "関数 intToStr(x) は整数 x を文字列に変換した値を返し、文字列どうしの ＋ は連結を表す。配列の要素番号は1から始まる。"
     "なお、and は左側が false のとき右側を評価しない。",
     """
○文字列型: encode(文字型の配列: s)
  文字列型: out ← ""
  整数型: i ← 1
  整数型: cnt
  while (i ≦ sの要素数)
    cnt ← 1
    while ((i ＋ cnt ≦ sの要素数) and (s[i ＋ cnt] ＝ s[i]))
      cnt ← cnt ＋ 1
    endwhile
    out ← out ＋ s[i] ＋ intToStr(cnt)
    i ← 〔 a 〕
  endwhile
  return out
""",
     "プログラム中の〔 a 〕に入れる正しい答えはどれか。",
     ["i ＋ cnt", "i ＋ 1", "i ＋ cnt − 1", "i ＋ cnt ＋ 1", "cnt", "cnt ＋ 1"], 0,
     "s[i] から cnt 個が同じ文字なので、次に調べるのは i ＋ cnt 番目。具体例 \"AAABCC\" で i＝1 のとき cnt＝3、次は4番目の B から。i ＋ 1 だと \"A3A2A1…\" と重複して数え、i ＋ cnt − 1 だと cnt＝1 のとき i が進まず止まらない。",
     _x04)

# ===== x05 2分木のなぞり =====
def _x05():
    val = [None, 40, 20, 60, 10, 30, 70, 65]
    left = [None, 2, 4, 0, 0, 0, 7, 0]
    right = [None, 3, 5, 6, 0, 0, 0, 0]
    out = []

    def order(n):
        if left[n]:
            order(left[n])
        if right[n]:
            order(right[n])
        out.append(str(val[n]))
    order(1)
    return pick(OPTS_X05, " ".join(out))

OPTS_X05 = ["10 30 20 65 70 60 40", "40 20 10 30 60 70 65", "10 20 30 40 60 65 70",
            "40 20 60 10 30 70 65", "10 30 20 40 65 70 60", "65 70 60 10 30 20 40"]
algo("x05", "2分木のなぞり",
     "2分木の各節を、要素番号を節の番号とする3つの配列で表す。val[n] は節 n の値、left[n] と right[n] は節 n の左の子と右の子の番号で、子がないときは 0 である。"
     "節1が根であり、配列の内容は次のとおりである。\n"
     "val ← {40, 20, 60, 10, 30, 70, 65}\nleft ← {2, 4, 0, 0, 0, 7, 0}\nright ← {3, 5, 6, 0, 0, 0, 0}\n"
     "出力は、値を空白で区切って続けて表示する。",
     """
大域: 整数型の配列: val, left, right   /* 内容は問題文のとおり */

○order(整数型: n)
  if (left[n] ≠ 0)
    order(left[n])
  endif
  if (right[n] ≠ 0)
    order(right[n])
  endif
  val[n] を出力する
""",
     "order(1) を呼び出したときの出力はどれか。",
     OPTS_X05, 0,
     "左の部分木、右の部分木を全て出力してから自分の値を出力する（後行順）。節2（20）の部分木は 10 30 20。節3（60）は左の子がなく、右の子の節6（70）の部分木が 65 70 なので 65 70 60。最後に根の 40。イは先行順、ウは中間順（2分探索木なので昇順になる）、エは幅優先の順。",
     _x05, code_opts=False)

# ===== x06 2分探索木への挿入 =====
class _Node:
    def __init__(self, v):
        self.val, self.left, self.right = v, None, None


def _x06():
    combos = [("left", "right"), ("left", "left"), ("right", "right"), ("right", "left"), ("node", "right"), ("left", "node")]

    def run(c, keys):
        root = _Node(keys[0])

        def insert(node, x, depth=0):
            guard(depth, 50)
            if x < node.val:
                if node.left is None:
                    node.left = _Node(x)
                else:
                    nxt = {"left": node.left, "right": node.right, "node": node}[c[0]]
                    if nxt is None:
                        raise Stop
                    insert(nxt, x, depth + 1)
            else:
                if node.right is None:
                    if c[1] == "right": node.right = _Node(x)
                    elif c[1] == "left": node.left = _Node(x)
                    # "node" は仮引数を書き換えるだけで木は変わらない
                else:
                    insert(node.right, x, depth + 1)
        for k in keys[1:]:
            insert(root, k)
        out = []

        def walk(n):
            if n:
                walk(n.left); out.append(n.val); walk(n.right)
        walk(root)
        return out
    tests = [[50, 30, 70, 20, 40, 60, 80, 35], [5, 3, 8, 1, 4, 7, 9], [10, 20, 30, 5, 15]]
    res = []
    for c in combos:
        try:
            res.append(all(run(c, t) == sorted(t) for t in tests))
        except Stop:
            res.append(False)
    return only(res)

algo("x06", "2分探索木への挿入",
     "クラス Node は2分探索木の節を表し、属性 val に値、属性 left と right に左右の子の節への参照を持つ。子がないときは 未定義 である。"
     "Node(x) は val が x で、left と right が未定義の節を生成して返す。"
     "手続 insert は、2分探索木の節 node と値 x を受け取り、「どの節でも、左の子孫の値は節の値より小さく、右の子孫の値は節の値以上」という条件を保ったまま x を持つ節を追加する。node は未定義ではない。",
     """
○insert(Node: node, 整数型: x)
  if (x ＜ node.val)
    if (node.left が 未定義)
      node.left ← Node(x)
    else
      insert(〔 a 〕, x)
    endif
  else
    if (node.right が 未定義)
      〔 b 〕
    else
      insert(node.right, x)
    endif
  endif
""",
     "プログラム中の〔 a 〕と〔 b 〕に入れる正しい答えの組合せはどれか。",
     ["a：node.left　b：node.right ← Node(x)", "a：node.left　b：node.left ← Node(x)", "a：node.right　b：node.right ← Node(x)",
      "a：node.right　b：node.left ← Node(x)", "a：node　b：node.right ← Node(x)", "a：node.left　b：node ← Node(x)"], 0,
     "x が節の値より小さければ左の部分木に進む（node.left）。x が節の値以上で右の子がなければ、新しい節を右の子にする。a に node を入れると同じ節で呼出しを繰り返して終わらない。b を node ← Node(x) にすると仮引数を書き換えるだけで、木に節が追加されない。",
     _x06)

# ===== x07 下限の位置（二分探索） =====
def _x07():
    import bisect
    res = []
    for a in ("mid ＋ 1", "mid"):
        for b in ("mid", "mid − 1", "mid ＋ 1"):
            ok = True
            try:
                for arr in ([1, 3, 3, 5, 8], [2, 4, 6, 8], [7], [1, 1, 1], [1, 2, 3, 4, 5, 6, 7]):
                    for x in range(0, 10):
                        lo, hi, steps = 1, len(arr) + 1, 0
                        a1 = [None] + arr
                        while lo < hi:
                            steps += 1
                            guard(steps, 100)
                            mid = (lo + hi) // 2
                            if mid > len(arr):
                                raise Stop
                            if a1[mid] < x:
                                lo = mid + 1 if a == "mid ＋ 1" else mid
                            else:
                                hi = {"mid": mid, "mid − 1": mid - 1, "mid ＋ 1": mid + 1}[b]
                        if lo != bisect.bisect_left(arr, x) + 1:
                            ok = False
            except Stop:
                ok = False
            res.append(ok)
    return only(res)

algo("x07", "値以上の最初の位置を求める二分探索",
     "関数 lowerBound は、昇順に整列された整数型の配列 a と整数 x を受け取り、x 以上の値を持つ最初の要素の要素番号を返す。"
     "a の全ての要素が x より小さいときは、aの要素数 ＋ 1 を返す。配列の要素番号は1から始まる。" + DIV +
     "例えば a が {1, 3, 3, 5, 8}、x が 3 のとき 2 を返す。",
     """
○整数型: lowerBound(整数型の配列: a, 整数型: x)
  整数型: lo ← 1
  整数型: hi ← aの要素数 ＋ 1
  整数型: mid
  while (lo ＜ hi)
    mid ← (lo ＋ hi) ÷ 2
    if (a[mid] ＜ x)
      lo ← 〔 a 〕
    else
      hi ← 〔 b 〕
    endif
  endwhile
  return lo
""",
     "プログラム中の〔 a 〕と〔 b 〕に入れる正しい答えの組合せはどれか。",
     combo(["mid ＋ 1", "mid"], ["mid", "mid − 1", "mid ＋ 1"]), 0,
     "a[mid] ＜ x なら、mid 以前に答えはないので lo ← mid ＋ 1。a[mid] ≧ x なら mid 自身が答えの候補なので、mid を範囲に残したまま hi ← mid とする（hi は「答えの候補の終わりの1つ後」を表す）。mid − 1 にすると答えを範囲から外してしまう。lo ← mid だと lo ＋ 1 ＝ hi のとき範囲が縮まず止まらない。",
     _x07)

# ===== x08 括弧の対応 =====
def _x08():
    A = [lambda c, t: (c == ")" and t != "(") or (c == "]" and t != "["),
         lambda c, t: (c == ")" and t == "(") or (c == "]" and t == "["),
         lambda c, t: (c == ")" and t != "[") or (c == "]" and t != "(")]

    def ref(s):
        st = []
        for c in s:
            if c in "([":
                st.append(c)
            else:
                if not st or st.pop() != {")": "(", "]": "["}[c]:
                    return False
        return not st

    def run(fa, b_empty, s):
        st = []
        for c in s:
            if c in "([":
                st.append(c)
            else:
                if not st:
                    return False
                t = st.pop()
                if fa(c, t):
                    return False
        return len(st) == 0 if b_empty else True
    strs = ["".join(p) for n in range(0, 7) for p in itertools.product("()[]", repeat=n)]
    return only([all(run(fa, b, s) == ref(s) for s in strs) for fa in A for b in (True, False)])

algo("x08", "括弧の対応の検査",
     "関数 balanced は、文字 \"(\"、\")\"、\"[\"、\"]\" だけからなる文字型の配列 s を受け取り、括弧の対応が正しければ true を、正しくなければ false を返す。"
     "例えば \"([])\" や \"()[]\" は正しく、\"(]\" や \"((\" や \"())\" は正しくない。"
     "配列 st はスタックとして使い、末尾に追加し、末尾から取り出す。",
     """
○論理型: balanced(文字型の配列: s)
  文字型の配列: st ← {}
  文字型: c, top
  整数型: i
  for (i を 1 から sの要素数 まで 1 ずつ増やす)
    c ← s[i]
    if ((c ＝ "(") or (c ＝ "["))
      st の末尾に c を追加する
    else
      if (stの要素数 ＝ 0)
        return false
      endif
      top ← st の末尾の要素
      st の末尾の要素を削除する
      if (〔 a 〕)
        return false
      endif
    endif
  endfor
  return 〔 b 〕
""",
     "プログラム中の〔 a 〕と〔 b 〕に入れる正しい答えの組合せはどれか。",
     ["a：((c ＝ \")\") and (top ≠ \"(\")) or ((c ＝ \"]\") and (top ≠ \"[\"))　b：stの要素数 ＝ 0",
      "a：((c ＝ \")\") and (top ≠ \"(\")) or ((c ＝ \"]\") and (top ≠ \"[\"))　b：true",
      "a：((c ＝ \")\") and (top ＝ \"(\")) or ((c ＝ \"]\") and (top ＝ \"[\"))　b：stの要素数 ＝ 0",
      "a：((c ＝ \")\") and (top ＝ \"(\")) or ((c ＝ \"]\") and (top ＝ \"[\"))　b：true",
      "a：((c ＝ \")\") and (top ≠ \"[\")) or ((c ＝ \"]\") and (top ≠ \"(\"))　b：stの要素数 ＝ 0",
      "a：((c ＝ \")\") and (top ≠ \"[\")) or ((c ＝ \"]\") and (top ≠ \"(\"))　b：true"], 0,
     "閉じ括弧と、スタックから取り出した開き括弧の種類が合わなければ false（a）。最後まで読んだとき、閉じられていない開き括弧がスタックに残っていれば正しくないので、スタックが空かどうかを返す（b）。b を true にすると \"((\" を正しいと判定してしまう。",
     _x08)

# ===== x09 逆ポーランド記法の計算 =====
def _x09():
    st = []
    for t in ["5", "1", "2", "＋", "4", "×", "＋", "3", "−"]:
        if t in "＋−×":
            b, a = st.pop(), st.pop()
            st.append({"＋": a + b, "−": a - b, "×": a * b}[t])
        else:
            st.append(int(t))
    return pick(["2", "8", "12", "14", "18", "20"], st[0])

algo("x09", "逆ポーランド記法の式の計算",
     "関数 calc は、逆ポーランド記法で表された式を、字句ごとに文字列型の配列 tokens に格納したものを受け取り、式の値を返す。"
     "字句は0〜9の数字1文字か、演算子 \"＋\"、\"−\"、\"×\" のいずれかである。関数 strToInt(t) は数字の文字列 t を整数に変換した値を返す。"
     "配列 st はスタックとして使う。",
     """
○整数型: calc(文字列型の配列: tokens)
  整数型の配列: st ← {}
  整数型: i, x, y
  for (i を 1 から tokensの要素数 まで 1 ずつ増やす)
    if (tokens[i] が "＋"、"−"、"×" のいずれか)
      y ← st の末尾の要素
      st の末尾の要素を削除する
      x ← st の末尾の要素
      st の末尾の要素を削除する
      x と y に tokens[i] の演算を行った結果（x 演算子 y）を st の末尾に追加する
    else
      st の末尾に strToInt(tokens[i]) を追加する
    endif
  endfor
  return st[1]
""",
     "tokens が {\"5\", \"1\", \"2\", \"＋\", \"4\", \"×\", \"＋\", \"3\", \"−\"} のとき、calc の戻り値はどれか。",
     ["2", "8", "12", "14", "18", "20"], 3,
     "1＋2＝3、3×4＝12、5＋12＝17、17−3＝14。中置記法では 5＋(1＋2)×4−3。演算子の直前の2つの値で計算し、先に積まれた方が左側（x）になる。",
     _x09, code_opts=False)

# ===== x10 ハノイの塔 =====
def _x10():
    out = []

    def hanoi(n, f, t, v):
        if n == 0:
            return
        hanoi(n - 1, f, v, t)
        out.append(f"{f}→{t}")
        hanoi(n - 1, v, t, f)
    hanoi(3, "A", "C", "B")
    return pick(OPTS_X10, out[4])

OPTS_X10 = ["A→B", "A→C", "B→A", "B→C", "C→A", "C→B"]
algo("x10", "ハノイの塔（再帰）",
     "手続 hanoi は、棒 from に積まれた n 枚の円盤を、棒 via を使って棒 to に移す手順を出力する。円盤を1枚動かすごとに、動かす元と先の棒の名前を「元→先」の形で1行出力する。",
     """
○hanoi(整数型: n, 文字型: from, 文字型: to, 文字型: via)
  if (n ＝ 0)
    return
  endif
  hanoi(n − 1, from, via, to)
  from と to を "→" でつないで出力する
  hanoi(n − 1, via, to, from)
""",
     "hanoi(3, \"A\", \"C\", \"B\") を呼び出したとき、5番目に出力されるものはどれか。",
     OPTS_X10, 2,
     "出力は順に A→C、A→B、C→B、A→C、B→A、B→C、A→C の7行。前半3行で上の2枚を B に移し、4行目で一番下の円盤を C に移し、5行目以降で B の2枚を C に移す。その最初の動きが B→A。",
     _x10, code_opts=False)

# ===== x11 クイックソートの分割 =====
def _x11():
    a = [None, 7, 2, 9, 4, 3, 8, 5]
    p, i = a[7], 0
    for j in range(1, 7):
        if a[j] <= p:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[7] = a[7], a[i + 1]
    return pick(OPTS_X11, "{" + ", ".join(map(str, a[1:])) + "}")

OPTS_X11 = ["{2, 4, 3, 5, 9, 8, 7}", "{2, 4, 3, 5, 7, 9, 8}", "{2, 3, 4, 5, 7, 8, 9}",
            "{5, 2, 4, 3, 9, 8, 7}", "{2, 4, 3, 7, 9, 8, 5}", "{3, 2, 4, 5, 8, 9, 7}"]
algo("x11", "クイックソートの分割",
     "関数 partition は、整数型の配列 a の要素番号 lo から hi までを、a[hi] の値（基準値）以下の要素と、基準値より大きい要素に分け、基準値を両者の間に置いて、その要素番号を返す。"
     "クイックソートの1回分の分割を行う処理である。配列の要素番号は1から始まる。",
     """
○整数型: partition(整数型の配列: a, 整数型: lo, 整数型: hi)
  整数型: p ← a[hi]
  整数型: i ← lo − 1
  整数型: j, tmp
  for (j を lo から hi − 1 まで 1 ずつ増やす)
    if (a[j] ≦ p)
      i ← i ＋ 1
      tmp ← a[i]
      a[i] ← a[j]
      a[j] ← tmp
    endif
  endfor
  tmp ← a[i ＋ 1]
  a[i ＋ 1] ← a[hi]
  a[hi] ← tmp
  return i ＋ 1
""",
     "配列 a が {7, 2, 9, 4, 3, 8, 5} のとき、partition(a, 1, 7) を実行した後の a の内容はどれか。",
     OPTS_X11, 0,
     "基準値は5。j＝2 で 2 を a[1] と交換 → {2,7,9,4,3,8,5}、j＝4 で 4 を a[2] と交換 → {2,4,9,7,3,8,5}、j＝5 で 3 を a[3] と交換 → {2,4,3,7,9,8,5}。最後に a[4] と a[7] を交換して {2,4,3,5,9,8,7}。5より左は5以下、右は5より大きいが、それぞれの中はまだ整列されていない。",
     _x11, code_opts=False)

# ===== x12 マージソートの呼出し回数 =====
def _x12():
    cnt = 0

    def ms(lo, hi):
        nonlocal cnt
        cnt += 1
        if lo < hi:
            mid = (lo + hi) // 2
            ms(lo, mid)
            ms(mid + 1, hi)
    ms(1, 8)
    return pick(["7", "8", "14", "15", "16", "31"], cnt)

algo("x12", "マージソートの再帰呼出し",
     "手続 mergeSort は、整数型の配列 a の要素番号 lo から hi までを昇順に整列する。手続 merge は、整列済みの2つの範囲を併合する（内容は省略）。" + DIV,
     """
○mergeSort(整数型の配列: a, 整数型: lo, 整数型: hi)
  整数型: mid
  if (lo ＜ hi)
    mid ← (lo ＋ hi) ÷ 2
    mergeSort(a, lo, mid)
    mergeSort(a, mid ＋ 1, hi)
    merge(a, lo, mid, hi)      /* a[lo]〜a[mid] と a[mid＋1]〜a[hi] を併合する */
  endif
""",
     "要素数8の配列 a に対して mergeSort(a, 1, 8) を呼び出したとき、mergeSort が呼び出される回数は、最初の呼出しも含めて何回か。",
     ["7", "8", "14", "15", "16", "31"], 3,
     "範囲を半分ずつに分け、要素が1個になるまで呼び出す。要素数8・4・2・1 の範囲がそれぞれ 1・2・4・8 回呼ばれるので、1＋2＋4＋8＝15回。要素数 n なら 2n−1 回。merge が呼ばれるのは要素が2個以上の範囲の7回。",
     _x12, code_opts=False)

# ===== x13 幅優先探索 =====
EDGES = [(1, 3), (1, 5), (2, 3), (2, 6), (3, 4), (4, 6), (5, 6)]
OPTS_X13 = ["1 3 5 2 4 6", "1 3 2 6 4 5", "1 2 3 4 5 6", "1 5 3 6 4 2", "1 3 5 4 2 6", "1 5 6 2 4 3"]


def _x13():
    adj = {v: sorted([b for a, b in EDGES if a == v] + [a for a, b in EDGES if b == v]) for v in range(1, 7)}
    q, seen, out = [1], {1}, []
    while q:
        v = q.pop(0)
        out.append(str(v))
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                q.append(w)
    return pick(OPTS_X13, " ".join(out))

algo("x13", "グラフの幅優先探索",
     "頂点1〜6からなる無向グラフがあり、辺は 1−3、1−5、2−3、2−6、3−4、4−6、5−6 の7本である。"
     "二次元配列 adj は隣接行列で、頂点 i と j の間に辺があれば adj[i, j] と adj[j, i] が1、なければ0である。"
     "手続 bfs は、頂点 start から幅優先探索を行い、訪問した頂点を順に出力する。出力は空白で区切って続けて表示する。",
     """
大域: 整数型の二次元配列: adj   /* 内容は問題文のとおり */

○bfs(整数型: start)
  整数型の配列: queue ← {start}
  論理型の配列: visited ← {6 個の false}
  整数型: head ← 1
  整数型: v, w
  visited[start] ← true
  while (head ≦ queueの要素数)
    v ← queue[head]
    head ← head ＋ 1
    v を出力する
    for (w を 1 から 6 まで 1 ずつ増やす)
      if ((adj[v, w] ＝ 1) and (visited[w] ＝ false))
        visited[w] ← true
        queue の末尾に w を追加する
      endif
    endfor
  endwhile
""",
     "bfs(1) を呼び出したときの出力はどれか。",
     OPTS_X13, 0,
     "1 の隣の 3、5 を番号順にキューへ入れる。3 を取り出して、隣で未訪問の 2、4 を入れる。5 を取り出して 6 を入れる。後は 2、4、6 の順に取り出す。イは深さ優先探索（1→3→2→6→4→5）の順。",
     _x13, code_opts=False)

# ===== x14 硬貨の最少枚数（動的計画法） =====
def _x14():
    conds = [lambda dp, i, c: dp[i - c] + 1 < dp[i], lambda dp, i, c: dp[i - c] + 1 > dp[i],
             lambda dp, i, c: dp[i] < dp[i - c], lambda dp, i, c: dp[c] < dp[i - c],
             lambda dp, i, c: dp[i - c] == 999]

    def ref(coins, amount):
        best = [0] + [999] * amount
        for i in range(1, amount + 1):
            for c in coins:
                if c <= i and best[i - c] + 1 < best[i]:
                    best[i] = best[i - c] + 1
        return best[amount]

    def run(f, coins, amount):
        dp = [None] + [999] * amount
        for i in range(1, amount + 1):
            for c in coins:
                if c == i:
                    dp[i] = 1
                elif c < i and f(dp, i, c):
                    dp[i] = dp[i - c] + 1
        return dp[amount]
    cases = [([1, 5, 8], a) for a in range(1, 31)] + [([2, 3], a) for a in range(1, 21)] + [([4, 3], a) for a in range(1, 21)]
    return only([all(run(f, c, a) == ref(c, a) for c, a in cases) for f in conds])

algo("x14", "硬貨の最少枚数（動的計画法）",
     "関数 minCoins は、硬貨の額面を格納した整数型の配列 coins と、正の整数 amount を受け取り、それらの硬貨（各額面は何枚でも使える）でちょうど amount 円を支払うときの、硬貨の最少枚数を返す。"
     "支払えないときは 999 を返す。dp[i] は、i 円を支払うときの最少枚数を表す。配列の要素番号は1から始まる。"
     "例えば coins が {1, 5, 8}、amount が 10 のとき、5円2枚の 2 を返す（大きい額面から使う 8＋1＋1 の3枚ではない）。",
     """
○整数型: minCoins(整数型の配列: coins, 整数型: amount)
  整数型の配列: dp ← {amount 個の 999}
  整数型: i, k, c
  for (i を 1 から amount まで 1 ずつ増やす)
    for (k を 1 から coinsの要素数 まで 1 ずつ増やす)
      c ← coins[k]
      if (c ＝ i)
        dp[i] ← 1
      elseif ((c ＜ i) and (〔 a 〕))
        dp[i] ← dp[i − c] ＋ 1
      endif
    endfor
  endfor
  return dp[amount]
""",
     "プログラム中の〔 a 〕に入れる正しい答えはどれか。なお、and は左側が false のとき右側を評価しない。",
     ["dp[i − c] ＋ 1 ＜ dp[i]", "dp[i − c] ＋ 1 ＞ dp[i]", "dp[i] ＜ dp[i − c]", "dp[c] ＜ dp[i − c]", "dp[i − c] ＝ 999"], 0,
     "i 円は「i−c 円の支払い方に硬貨 c を1枚足したもの」で作れる。その枚数 dp[i − c] ＋ 1 が、今までに見つけた dp[i] より少ないときだけ更新する。大きい問題の答えを、小さい問題の答え（表 dp）から順に求めるのが動的計画法。",
     _x14)

# ===== x15 最大の部分配列の和 =====
def _x15():
    def ref(a):
        return max(sum(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1))
    tests = [[2, -3, 4, -1, 2, -5, 3], [-3, -1, -2], [5], [1, 2, 3], [-2, 1, -3, 4, -1, 2, 1, -5, 4], [3, -4, 5]]
    res = []
    for a_ in ("a[i]", "0", "cur"):
        for b_ in ("cur", "a[i]"):
            ok = True
            for a in tests:
                best = cur = a[0]
                for x in a[1:]:
                    cur = max({"a[i]": x, "0": 0, "cur": cur}[a_], cur + x)
                    best = max(best, {"cur": cur, "a[i]": x}[b_])
                ok = ok and best == ref(a)
            res.append(ok)
    return only(res)

algo("x15", "連続する部分の和の最大値",
     "関数 maxSub は、要素数が1以上の整数型の配列 a を受け取り、a の連続する1個以上の要素の和のうち、最大のものを返す。"
     "例えば a が {2, −3, 4, −1, 2, −5, 3} のとき、4＋(−1)＋2 の 5 を返す。関数 max(x, y) は x と y の大きい方を返す。"
     "変数 cur は、a[i] で終わる連続部分の和の最大値を表す。配列の要素番号は1から始まる。",
     """
○整数型: maxSub(整数型の配列: a)
  整数型: best ← a[1]
  整数型: cur ← a[1]
  整数型: i
  for (i を 2 から aの要素数 まで 1 ずつ増やす)
    cur ← max(〔 a 〕, cur ＋ a[i])
    best ← max(best, 〔 b 〕)
  endfor
  return best
""",
     "プログラム中の〔 a 〕と〔 b 〕に入れる正しい答えの組合せはどれか。",
     combo(["a[i]", "0", "cur"], ["cur", "a[i]"]), 0,
     "a[i] で終わる連続部分は、「a[i] だけ」か「a[i−1] で終わる最良の部分に a[i] を足したもの」のどちらか。大きい方が新しい cur（a）。best はそれまでの cur の最大値（b）。a を 0 にすると、全ての要素が負の配列で 0（空の部分）を答えてしまう。",
     _x15)

# ===== x16 文字列の照合の比較回数 =====
def _x16():
    t, p = "ABABCABC", "ABC"
    n, m, cmp = len(t), len(p), 0
    for i in range(1, n - m + 2):
        j = 1
        while j <= m:
            cmp += 1
            if t[i + j - 2] != p[j - 1]:
                break
            j += 1
        if j > m:
            break
    return pick(["3", "5", "6", "7", "8", "9"], cmp)

algo("x16", "文字列の照合（力まかせ法）",
     "関数 find は、文字型の配列 t の中で、文字型の配列 p と一致する部分が最初に現れる位置を返す。見つからなければ −1 を返す。"
     "配列の要素番号は1から始まる。and は左側が false のとき右側を評価しない。",
     """
○整数型: find(文字型の配列: t, 文字型の配列: p)
  整数型: n ← tの要素数
  整数型: m ← pの要素数
  整数型: i, j
  for (i を 1 から n − m ＋ 1 まで 1 ずつ増やす)
    j ← 1
    while ((j ≦ m) and (t[i ＋ j − 1] ＝ p[j]))   /* α */
      j ← j ＋ 1
    endwhile
    if (j ＞ m)
      return i
    endif
  endfor
  return −1
""",
     "t が \"ABABCABC\"、p が \"ABC\" のとき、α の条件式の中の t[i ＋ j − 1] ＝ p[j] が評価される回数はどれか。",
     ["3", "5", "6", "7", "8", "9"], 3,
     "i＝1：A＝A、B＝B、A≠C で3回。i＝2：B≠A で1回。i＝3：A＝A、B＝B、C＝C で3回、その後 j＝4 で j ≦ m が false なので右側は評価されない。計7回で、3 を返す。",
     _x16, code_opts=False)

# ===== x17 ヒープへの追加 =====
def _x17():
    res = []
    for a in ("k÷2", "k−1", "2k"):
        for b in ("k÷2", "k−1"):
            ok = True
            for perm in itertools.permutations(range(1, 7)):
                heap = [None] * 20
                size = 0
                try:
                    for x in perm:
                        size += 1
                        heap[size] = x
                        k, steps = size, 0
                        while True:
                            steps += 1
                            guard(steps, 50)
                            if k <= 1:
                                break
                            idx = {"k÷2": k // 2, "k−1": k - 1, "2k": 2 * k}[a]
                            if idx > size or heap[idx] is None:
                                raise Stop
                            if not heap[idx] < heap[k]:
                                break
                            heap[k // 2], heap[k] = heap[k], heap[k // 2]
                            k = k // 2 if b == "k÷2" else k - 1
                    if sorted(heap[1:size + 1]) != sorted(perm) or any(heap[i // 2] < heap[i] for i in range(2, size + 1)):
                        ok = False
                except Stop:
                    ok = False
                if not ok:
                    break
            res.append(ok)
    return only(res)

algo("x17", "ヒープへの要素の追加",
     "大域変数の配列 heap を使って、親の値が子の値以上になる2分木（ヒープ）を表す。heap[1] が根で、heap[k] の親は heap[k ÷ 2]、子は heap[2k] と heap[2k ＋ 1] である。"
     "大域変数 size はヒープの要素数で、heap の要素数は十分に大きい。手続 push は、ヒープの条件を保ったまま値 x を追加する。" + DIV +
     "なお、and は左側が false のとき右側を評価しない。",
     """
大域: 整数型の配列: heap
大域: 整数型: size ← 0

○push(整数型: x)
  整数型: k, tmp
  size ← size ＋ 1
  heap[size] ← x
  k ← size
  while ((k ＞ 1) and (heap[〔 a 〕] ＜ heap[k]))
    tmp ← heap[k ÷ 2]
    heap[k ÷ 2] ← heap[k]
    heap[k] ← tmp
    k ← 〔 b 〕
  endwhile
""",
     "プログラム中の〔 a 〕と〔 b 〕に入れる正しい答えの組合せはどれか。",
     combo(["k ÷ 2", "k − 1", "2 × k"], ["k ÷ 2", "k − 1"]), 0,
     "追加した値を末尾に置き、親（k ÷ 2）より大きい間は親と交換して上に移動する。交換したら自分は親の位置に移るので k ← k ÷ 2。k − 1 は親ではなく隣の要素なので、ヒープの条件が崩れる。2 × k は子なので、末尾の要素には存在しない。",
     _x17)

# ===== x18 うるう年 =====
def _x18():
    fs = [lambda y: (y % 4 == 0 and y % 100 != 0) or y % 400 == 0,
          lambda y: (y % 4 == 0 or y % 100 != 0) and y % 400 == 0,
          lambda y: y % 4 == 0 and y % 100 != 0 and y % 400 == 0,
          lambda y: (y % 4 == 0 and y % 100 == 0) or y % 400 != 0,
          lambda y: y % 4 == 0 or (y % 100 != 0 and y % 400 == 0),
          lambda y: y % 400 == 0 or y % 100 != 0]
    import calendar
    return only([all(f(y) == calendar.isleap(y) for y in range(1, 3001)) for f in fs])

algo("x18", "うるう年の判定",
     "関数 isLeap は、西暦の年 y を受け取り、うるう年なら true を返す。うるう年は「4で割り切れる年。ただし100で割り切れる年は除く。ただし400で割り切れる年はうるう年とする」である。"
     "例えば 2024年と2000年はうるう年、1900年と2023年はうるう年ではない。",
     """
○論理型: isLeap(整数型: y)
  return 〔 a 〕
""",
     "プログラム中の〔 a 〕に入れる正しい答えはどれか。",
     ["((y mod 4 ＝ 0) and (y mod 100 ≠ 0)) or (y mod 400 ＝ 0)",
      "((y mod 4 ＝ 0) or (y mod 100 ≠ 0)) and (y mod 400 ＝ 0)",
      "(y mod 4 ＝ 0) and (y mod 100 ≠ 0) and (y mod 400 ＝ 0)",
      "((y mod 4 ＝ 0) and (y mod 100 ＝ 0)) or (y mod 400 ≠ 0)",
      "(y mod 4 ＝ 0) or ((y mod 100 ≠ 0) and (y mod 400 ＝ 0))",
      "(y mod 400 ＝ 0) or (y mod 100 ≠ 0)"], 0,
     "「4で割り切れて100で割り切れない」か「400で割り切れる」のどちらか。具体例で確かめる：2000年（400で割り切れる）、1900年（100で割り切れるが400で割り切れない）、2023年（4で割り切れない）。カの「400で割り切れるか100で割り切れない」だと 2023年もうるう年になってしまう。",
     _x18)

# ===== x19 連結リストの反転 =====
class _E:
    def __init__(self, v, nxt=None):
        self.val, self.next = v, nxt


def _x19():
    def build(xs):
        head = None
        for x in reversed(xs):
            head = _E(x, head)
        return head

    def to_list(h):
        out = []
        while h is not None:
            out.append(h.val)
            guard(len(out), 20)
            h = h.next
        return out
    res = []
    for a in ("curr.next ← prev", "prev.next ← curr", "curr.next ← nxt"):
        for b in ("nxt", "curr.next"):
            ok = True
            for xs in ([1, 2, 3, 4], [1], [1, 2]):
                try:
                    prev, curr, steps = None, build(xs), 0
                    while curr is not None:
                        steps += 1
                        guard(steps, 20)
                        nxt = curr.next
                        if a == "curr.next ← prev": curr.next = prev
                        elif a == "prev.next ← curr":
                            if prev is None:
                                raise Stop
                            prev.next = curr
                        else: curr.next = nxt
                        prev = curr
                        curr = nxt if b == "nxt" else curr.next
                    ok = ok and to_list(prev) == xs[::-1]
                except Stop:
                    ok = False
            res.append(ok)
    return only(res)

algo("x19", "連結リストの反転",
     "クラス ListElement は単方向の連結リストの要素を表し、属性 val に値、属性 next に次の要素への参照を持つ。最後の要素の next は未定義である。"
     "関数 reverse は、リストの先頭の要素 head を受け取り、要素の並びを逆順にしたリストの先頭の要素を返す。新しい要素は作らず、next の付け替えだけで行う。",
     """
○ListElement: reverse(ListElement: head)
  ListElement: prev ← 未定義
  ListElement: curr ← head
  ListElement: nxt
  while (curr が 未定義 でない)
    nxt ← curr.next
    〔 a 〕
    prev ← curr
    curr ← 〔 b 〕
  endwhile
  return prev
""",
     "プログラム中の〔 a 〕と〔 b 〕に入れる正しい答えの組合せはどれか。",
     combo(["curr.next ← prev", "prev.next ← curr", "curr.next ← nxt"], ["nxt", "curr.next"]), 0,
     "今の要素の次を、1つ前の要素に付け替える（a）。付け替えると元の次の要素をたどれなくなるので、先に nxt に退避しておき、そこへ進む（b）。b を curr.next にすると、付け替えた後の curr.next は1つ前の要素なので、前へ戻ってしまう。",
     _x19)

# ===== x20 画像の回転 =====
def _x20():
    maps = [lambda n, i, j: (j, n - i + 1), lambda n, i, j: (n - j + 1, i), lambda n, i, j: (j, i),
            lambda n, i, j: (n - i + 1, n - j + 1), lambda n, i, j: (i, n - j + 1), lambda n, i, j: (n - j + 1, n - i + 1)]

    def run(f, img):
        n = len(img)
        out = [[None] * n for _ in range(n)]
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                r, c = f(n, i, j)
                out[r - 1][c - 1] = img[i - 1][j - 1]
        return out

    def cw(img):
        return [list(r) for r in zip(*img[::-1])]
    imgs = [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[k + 4 * r for k in range(4)] for r in range(4)]]
    return only([all(run(f, m) == cw(m) for m in imgs) for f in maps])

algo("x20", "画像を右に90度回転する",
     "関数 rotate は、n 行 n 列の画像を表す二次元配列 img を受け取り、右に（時計回りに）90度回転した画像を表す二次元配列を返す。img[i, j] は i 行 j 列の画素で、行も列も番号は1から始まる。"
     "例えば {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}} は {{7, 4, 1}, {8, 5, 2}, {9, 6, 3}} になる。",
     """
○整数型の二次元配列: rotate(整数型の二次元配列: img, 整数型: n)
  整数型の二次元配列: out ← {n 行 n 列の 0}
  整数型: i, j
  for (i を 1 から n まで 1 ずつ増やす)
    for (j を 1 から n まで 1 ずつ増やす)
      out[〔 a 〕] ← img[i, j]
    endfor
  endfor
  return out
""",
     "プログラム中の〔 a 〕に入れる正しい答えはどれか。",
     ["j, n − i ＋ 1", "n − j ＋ 1, i", "j, i", "n − i ＋ 1, n − j ＋ 1", "i, n − j ＋ 1", "n − j ＋ 1, n − i ＋ 1"], 0,
     "例の 1 は img[1, 1] から out[1, 3] へ、7 は img[3, 1] から out[1, 1] へ移る。元の列番号 j が新しい行番号になり、元の行番号 i が大きいほど新しい列番号は小さくなる（n − i ＋ 1）。イは左回転、ウは転置、エは180度回転。",
     _x20)

# ===== x21 状態遷移表 =====
def _x21():
    trans = {1: (2, 1), 2: (2, 3), 3: (4, 1), 4: (4, 4)}

    def accept(s):
        st = 1
        for ch in s:
            st = trans[st][0 if ch == "a" else 1]
        return st == 4
    return only([accept(s) for s in OPTS_X21])

OPTS_X21 = ["abba", "baab", "aabab", "bbaa", "abbb", "bab"]
algo("x21", "状態遷移表による文字列の判定",
     "関数 accept は、文字 \"a\" と \"b\" だけからなる文字型の配列 s を受け取り、状態遷移表 trans に従って状態を変化させ、最後の状態が4なら true を返す。"
     "trans[状態, 列] が次の状態で、文字が \"a\" なら1列目、\"b\" なら2列目を使う。最初の状態は1である。\n"
     "trans ← {{2, 1}, {2, 3}, {4, 1}, {4, 4}}　（{2, 1} が状態1の行）",
     """
大域: 整数型の二次元配列: trans   /* 内容は問題文のとおり */

○論理型: accept(文字型の配列: s)
  整数型: state ← 1
  整数型: col, i
  for (i を 1 から sの要素数 まで 1 ずつ増やす)
    if (s[i] ＝ "a")
      col ← 1
    else
      col ← 2
    endif
    state ← trans[state, col]
  endfor
  return state ＝ 4
""",
     "accept が true を返す s はどれか。",
     OPTS_X21, 2,
     "状態1→(a)→2→(b)→3→(a)→4 と進み、状態4はどの文字でも4のまま。つまり「aba」を含む文字列で true になる。aabab は 1→2→2→3→4→4。他の選択肢は aba を含まない。",
     _x21)

# ===== x22 行列の積 =====
def _x22():
    rnd = random.Random(7)
    ms = [([[rnd.randint(-3, 5) for _ in range(3)] for _ in range(3)], [[rnd.randint(-3, 5) for _ in range(3)] for _ in range(3)]) for _ in range(3)]
    fs = [lambda x, y, i, j, k: x[i][k] * y[k][j], lambda x, y, i, j, k: x[i][k] * y[j][k],
          lambda x, y, i, j, k: x[k][i] * y[k][j], lambda x, y, i, j, k: x[i][j] * y[j][k],
          lambda x, y, i, j, k: x[k][j] * y[i][k], lambda x, y, i, j, k: x[i][k] * y[i][k]]

    def run(f, x, y):
        n = 3
        return [[sum(f(x, y, i, j, k) for k in range(n)) for j in range(n)] for i in range(n)]

    def ref(x, y):
        return [[sum(x[i][k] * y[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return only([all(run(f, x, y) == ref(x, y) for x, y in ms) for f in fs])

algo("x22", "行列の積",
     "関数 mul は、n 行 n 列の行列を表す二次元配列 x と y を受け取り、行列の積 x × y を返す。積の i 行 j 列の要素は、x の i 行目の各要素と、y の j 列目の各要素を順に掛けて足したものである。行も列も番号は1から始まる。",
     """
○整数型の二次元配列: mul(整数型の二次元配列: x, 整数型の二次元配列: y, 整数型: n)
  整数型の二次元配列: z ← {n 行 n 列の 0}
  整数型: i, j, k
  for (i を 1 から n まで 1 ずつ増やす)
    for (j を 1 から n まで 1 ずつ増やす)
      for (k を 1 から n まで 1 ずつ増やす)
        z[i, j] ← z[i, j] ＋ 〔 a 〕
      endfor
    endfor
  endfor
  return z
""",
     "プログラム中の〔 a 〕に入れる正しい答えはどれか。",
     ["x[i, k] × y[k, j]", "x[i, k] × y[j, k]", "x[k, i] × y[k, j]", "x[i, j] × y[j, k]", "x[k, j] × y[i, k]", "x[i, k] × y[i, k]"], 0,
     "x の i 行目は x[i, 1]〜x[i, n]、y の j 列目は y[1, j]〜y[n, j]。同じ k 番目どうしを掛けるので x[i, k] × y[k, j]。オは y × x の積になる。",
     _x22)

# ===== x23 整列済み配列の重複の除去 =====
def _x23():
    fs = ["a[i] ≠ a[i − 1]", "a[i] ＝ a[i − 1]", "a[i] ≠ a[1]", "a[i − 1] ＞ a[i]", "a[i] ≠ a[i ＋ 1]"]

    def run(k, arr):
        a = [None] + arr
        out = [a[1]]
        for i in range(2, len(arr) + 1):
            if k == 4 and i + 1 > len(arr):
                raise Stop
            cond = [a[i] != a[i - 1], a[i] == a[i - 1], a[i] != a[1], a[i - 1] > a[i], k == 4 and a[i] != a[i + 1]][k]
            if cond:
                out.append(a[i])
        return out
    tests = [[1, 1, 2, 3, 3, 3, 5], [4], [2, 2, 2], [1, 2, 3], [1, 2, 2, 3]]
    res = []
    for k in range(len(fs)):
        try:
            res.append(all(run(k, t) == sorted(set(t)) for t in tests))
        except Stop:
            res.append(False)
    return only(res)

algo("x23", "整列済みの配列から重複を取り除く",
     "関数 unique は、昇順に整列された要素数1以上の整数型の配列 a を受け取り、同じ値を1つにまとめた配列を返す。例えば {1, 1, 2, 3, 3, 3, 5} なら {1, 2, 3, 5} を返す。配列の要素番号は1から始まる。",
     """
○整数型の配列: unique(整数型の配列: a)
  整数型の配列: out ← {a[1]}
  整数型: i
  for (i を 2 から aの要素数 まで 1 ずつ増やす)
    if (〔 a 〕)
      out の末尾に a[i] を追加する
    endif
  endfor
  return out
""",
     "プログラム中の〔 a 〕に入れる正しい答えはどれか。",
     ["a[i] ≠ a[i − 1]", "a[i] ＝ a[i − 1]", "a[i] ≠ a[1]", "a[i − 1] ＞ a[i]", "a[i] ≠ a[i ＋ 1]"], 0,
     "整列済みなので、同じ値は隣どうしに並ぶ。1つ前と違う値のときだけ追加すればよい。a[i] ≠ a[1] は先頭と比べているだけなので、{1, 2, 2, 3} で 2 を2回追加してしまう。a[i ＋ 1] は最後の要素で配列の範囲を超える。",
     _x23)

# ===== x24 2つのスタックで作るキュー =====
def _x24():
    ops = [("e", 1), ("e", 2), ("d",), ("e", 3), ("e", 4), ("d",), ("d",), ("e", 5), ("d",), ("d",)]
    variants = ["inbox の末尾の要素", "inbox[1]", "outbox の末尾の要素", "inboxの要素数"]

    def run(k):
        inbox, outbox, out = [], [], []
        for op in ops:
            if op[0] == "e":
                inbox.append(op[1])
            else:
                if not outbox:
                    steps = 0
                    while inbox:
                        steps += 1
                        guard(steps, 20)
                        v = [inbox[-1] if inbox else None, inbox[0] if inbox else None, outbox[-1] if outbox else None, len(inbox)][k]
                        if v is None:
                            raise Stop
                        outbox.append(v)
                        inbox.pop()
                if not outbox:
                    raise Stop
                out.append(outbox.pop())
        return out
    res = []
    for k in range(len(variants)):
        try:
            res.append(run(k) == [1, 2, 3, 4, 5])
        except Stop:
            res.append(False)
    return only(res)

algo("x24", "2つのスタックでキューを作る",
     "配列 inbox と outbox をそれぞれスタックとして使い（末尾に追加し、末尾から取り出す）、先入れ先出しのキューを実現する。"
     "手続 enqueue は値をキューに入れ、関数 dequeue はキューから最も古い値を取り出して返す。空のキューから取り出すことはない。",
     """
大域: 整数型の配列: inbox ← {}
大域: 整数型の配列: outbox ← {}

○enqueue(整数型: x)
  inbox の末尾に x を追加する

○整数型: dequeue()
  整数型: x
  if (outboxの要素数 ＝ 0)
    while (inboxの要素数 ＞ 0)
      outbox の末尾に 〔 a 〕 を追加する
      inbox の末尾の要素を削除する
    endwhile
  endif
  x ← outbox の末尾の要素
  outbox の末尾の要素を削除する
  return x
""",
     "プログラム中の〔 a 〕に入れる正しい答えはどれか。",
     ["inbox の末尾の要素", "inbox[1]", "outbox の末尾の要素", "inboxの要素数"], 0,
     "inbox の要素を末尾から順に outbox へ移すと、順番が逆になり、最も古い値が outbox の末尾（取り出す位置）に来る。outbox が空になるまでは移し替えないので、後から入れた値が先に出ることはない。",
     _x24)


# ===== 情報セキュリティ（本試験レベル） =====
sec("y01", "ランサムウェアの初動対応",
    "A社は従業員300名の製造業で、情報システム部の中に CSIRT を置いている。ある朝、経理部のB氏から「共有フォルダのファイルが開けず、拡張子が見慣れないものに変わっている。"
    "デスクトップに身代金を要求する文書がある」と連絡があった。B氏のPCは有線LANで社内ネットワークに接続されており、経理部の共有フォルダはファイルサーバ上にある。\n"
    "CSIRT のC氏は、B氏に対して初動として次の(1)〜(5)の中から指示すべきものを検討した。\n"
    "(1) PCのLANケーブルを抜き、無線LANも無効にする\n(2) PCの電源をすぐに切る\n(3) 身代金を支払えば復旧できるか、攻撃者に連絡して確認する\n"
    "(4) 画面の表示や、気付いた時刻・操作した内容をメモし、PCはそのままの状態にしておく\n(5) 暗号化されたファイルを削除して、ごみ箱も空にする",
    "C氏が B氏に指示すべきものだけを全て挙げた組合せはどれか。",
    ["(1), (2)", "(1), (4)", "(1), (4), (5)", "(2), (3)", "(2), (4)", "(3), (5)"], 1,
    "感染の拡大を防ぐため、まずネットワークから切り離す（1）。調査に必要なメモリ上の情報や記録を残すため、電源はすぐには切らず、状況を記録してそのままにする（4）。身代金を払っても復旧の保証はなく、攻撃者との接触は避ける。ファイルの削除は証拠を失わせる。")

sec("y02", "アクセス権の設定",
    "D社では、ファイルサーバに部門ごとのフォルダを置き、アクセス権を次のように設定している。\n"
    "・人事フォルダ：人事部員は読取りと書込み、他の部員はアクセス不可\n・営業フォルダ：営業部員は読取りと書込み、経理部員は読取り\n・共通フォルダ：全社員が読取りと書込み\n"
    "先日、営業部から人事部に異動したE氏が、異動後も営業フォルダの顧客リストを読み書きできることが分かった。E氏のアカウントには、営業部のグループと人事部のグループの両方が設定されていた。"
    "D社では、異動の手続きは人事システムで行われ、ファイルサーバのグループの変更は、各部門の依頼を受けて情報システム部が手作業で行っている。",
    "この問題の再発を防ぐための対策として、最も適切なものはどれか。",
    ["営業フォルダのアクセス権を、全社員が読取りだけにする",
     "人事システムでの異動の確定をきっかけに、旧部門のグループからの削除を情報システム部に自動で依頼し、さらに定期的にグループの所属を棚卸しする",
     "E氏のパスワードを変更する",
     "ファイルサーバのアクセスログを1年間保存する",
     "顧客リストのファイル名を変更する"], 1,
    "原因は、異動の情報がアクセス権の変更に結び付いていないこと。異動を確実にグループの変更に反映し、漏れがないか定期的に棚卸しするのが根本的な対策（最小権限の原則の維持）。ログの保存は、事後の調査には役立つが再発は防げない。")

sec("y03", "ファイル送付の方法の見直し",
    "F社では、取引先に機密情報を含むファイルをメールで送るとき、ファイルをパスワード付きZIPで暗号化して添付し、続けて別のメールでパスワードを送っている。"
    "情報セキュリティ委員会では、この方法について次の問題点が指摘された。\n"
    "・宛先を誤ると、ファイルとパスワードの両方が同じ誤った相手に届く\n・メールの経路で盗聴された場合、2通とも同じ経路を通るので、両方とも盗まれる\n"
    "・暗号化されたZIPファイルは、受信側のマルウェア対策ソフトで中身を検査できない\nそこで、代替となる方法を検討した。",
    "指摘された問題点を全て改善できる方法として、最も適切なものはどれか。",
    ["ZIPのパスワードを、より長く複雑なものにする",
     "パスワードを電話で伝える",
     "ファイルを社が契約するクラウドストレージに置き、取引先の担当者だけがログインして取得できるように共有し、取得の期限を設定する",
     "ファイルを暗号化せずに添付し、本文に「機密」と記載する",
     "メールの件名に【重要】と付ける"], 2,
    "クラウドストレージで相手を指定して共有すれば、メールの誤送信でファイルが届くことはなく、通信はTLSで保護され、ファイルは暗号化されたZIPではないので受信側で検査できる。パスワードを電話で伝えると盗聴の問題は改善するが、マルウェア検査の問題は残る。")

sec("y04", "ログインの異常の分析",
    "G社の会員制Webサイトのログイン記録を調べたところ、次のことが分かった。\n"
    "・午前2時から4時の間に、約3,000件の異なる会員IDでログインが試みられた\n・送信元のIPアドレスは約800種類で、国外のものが多かった\n"
    "・1つの会員IDあたりのログイン試行は1回か2回で、そのうち約2%が成功していた\n・ログインに成功した会員の多くは、他のWebサイトと同じパスワードを使っていた\n"
    "G社のサイトでは、同じ会員IDで5回連続してログインに失敗すると、そのIDを30分間ロックする設定になっている。",
    "この攻撃の名称〔 a 〕と、最も効果的な対策〔 b 〕の組合せはどれか。",
    ["a：ブルートフォース攻撃　b：ロックするまでの失敗回数を3回に減らす",
     "a：ブルートフォース攻撃　b：多要素認証を導入する",
     "a：パスワードリスト攻撃　b：ロックするまでの失敗回数を3回に減らす",
     "a：パスワードリスト攻撃　b：多要素認証を導入する",
     "a：パスワードスプレー攻撃　b：送信元IPアドレスを1つずつ遮断する",
     "a：辞書攻撃　b：パスワードの最低文字数を増やす"], 3,
    "1つのIDあたり1〜2回で成功しており、他サイトと同じパスワードの会員が被害に遭っているので、他サイトから漏えいしたIDとパスワードの組を使ったパスワードリスト攻撃。正しいパスワードを使われているので、ロックの回数やパスワードの長さでは防げない。送信元が多数なので、IPアドレスごとの遮断も追いつかない。所持の要素を加える多要素認証が効果的。")

sec("y05", "個人情報の取扱いの委託",
    "H社は、通信販売の顧客の問合せ対応業務を、コールセンター事業者のI社に委託している。委託契約には秘密保持の条項があるが、再委託や監査についての条項はない。"
    "あるとき、I社が H社に無断で業務の一部を J社に再委託しており、J社の従業員が顧客の個人情報を持ち出していたことが分かった。",
    "H社が今後、委託先の管理として行うべきことの組合せとして、最も適切なものはどれか。",
    ["委託先の選定はやめ、全ての業務を自社で行う",
     "契約に、再委託には事前の書面による承諾を必要とすることと、委託先への監査や報告を求める権利を定め、定期的に委託先の取扱い状況を確認する",
     "委託先の従業員全員の個人のメールアドレスを報告させる",
     "顧客に、個人情報が漏えいする可能性があることを事前に通知しておく",
     "委託料を引き上げる"], 1,
    "個人情報保護法では、委託元は委託先を監督する義務がある。再委託の条件と監査の権利を契約で定め、実際に取扱い状況を確認することが必要。全てを自社で行うのは、委託の監督の問題の解決にならず、現実的でもない。")

sec("y06", "VPN装置の脆弱性",
    "K社では、テレワークのためにVPN装置を導入している。VPN装置のメーカは半年前に、認証を回避できる重大な脆弱性と、それを修正するファームウェアを公表していた。"
    "しかし K社では、VPN装置を担当する者が決まっておらず、ファームウェアは導入時のままだった。先日、攻撃者がこの脆弱性を悪用して VPN装置に侵入し、社内のサーバに不正にアクセスしていたことが分かった。",
    "今後の対策として、最も適切なものはどれか。",
    ["テレワークを全面的に禁止する",
     "ネットワーク機器を含む情報資産の一覧と担当者を定め、脆弱性情報を定期的に確認して、修正プログラムを計画的に適用する",
     "VPN の接続に使う利用者のパスワードを変更する",
     "社内のサーバのディスクを暗号化する",
     "VPN装置を別のメーカの製品に交換する"], 1,
    "原因は、機器の管理者がおらず、公表された脆弱性の修正が適用されなかったこと。資産と担当者を明確にし、脆弱性情報の収集と修正の適用を手順化する。認証を回避する脆弱性なので、パスワードを変えても防げない。製品を替えても、管理の仕組みがなければ同じことが起きる。")

sec("y07", "Webアプリケーションの脆弱性診断",
    "L社は、自社の Webアプリケーションの脆弱性診断を外部に依頼し、次の2件の指摘を受けた。\n"
    "指摘1：検索画面で、入力した文字列がそのまま結果画面に表示される。入力に <script> タグを含めると、閲覧者のブラウザでスクリプトが実行される。\n"
    "指摘2：ログイン画面で、利用者IDに ' OR '1'='1 と入力すると、パスワードを知らなくてもログインできる。",
    "指摘1と指摘2への対策〔 a 〕〔 b 〕の組合せとして、最も適切なものはどれか。",
    ["a：出力する文字列の特殊文字をエスケープする　b：SQL文の組立てにプレースホルダを使う",
     "a：出力する文字列の特殊文字をエスケープする　b：Cookie に HttpOnly 属性を付ける",
     "a：SQL文の組立てにプレースホルダを使う　b：出力する文字列の特殊文字をエスケープする",
     "a：通信を TLS で暗号化する　b：SQL文の組立てにプレースホルダを使う",
     "a：通信を TLS で暗号化する　b：パスワードを長くする",
     "a：Cookie に Secure 属性を付ける　b：WAF だけで対応し、プログラムは修正しない"], 0,
    "指摘1はクロスサイトスクリプティングで、出力時のエスケープが根本的な対策。指摘2は SQLインジェクションで、プレースホルダが根本的な対策。TLS は通信路を保護するだけで、アプリケーションの処理の欠陥は防げない。WAF は暫定的な緩和策で、プログラムの修正の代わりにはならない。")

sec("y08", "退職予定者による情報の持出し",
    "M社の営業部で退職予定の社員Nが、退職の2週間前に、顧客リストを含む大量のファイルを個人のクラウドストレージにアップロードしていたことが、退職後に分かった。"
    "M社では、社員のPCからインターネット上の任意のクラウドストレージにアクセスでき、Webアクセスのログは取得していたが、誰も確認していなかった。",
    "今後の対策として、最も適切なものはどれか。",
    ["退職者には、退職後に一切連絡しないようにする",
     "業務で許可したクラウドストレージ以外へのアップロードを制限し、大量のデータの送信を検知したら管理者に通知する仕組みを導入する",
     "顧客リストを紙で管理する",
     "全社員のPCを毎日初期化する",
     "退職者の名前を社内に公表する"], 1,
    "持出しの経路（私用のクラウドストレージ）を技術的に制限し、異常な送信を検知して早く気付けるようにする（DLP などの仕組み）。ログを取得していても、確認しなければ不正に気付けない。紙での管理は持出しを防ぐことにならず、業務の効率も落ちる。")

sec("y09", "私物スマートフォンの業務利用",
    "P社では、営業担当者が私物のスマートフォンで社内のメールとスケジュールを利用すること（BYOD）を認めている。"
    "端末の紛失時に情報を守るための対策を検討した結果、次の(1)〜(4)が候補に挙がった。\n"
    "(1) MDM を導入し、紛失時には業務用の領域のデータを遠隔で消去できるようにする\n(2) 画面ロックのパスコードの設定を利用の条件にする\n"
    "(3) 端末に保存された写真や私的なアプリを、会社が自由に閲覧できるようにする\n(4) 業務用のデータは、端末の中の、私的なデータと分離された領域に保存させる",
    "紛失時の情報漏えい対策として適切で、かつ従業員のプライバシーへの配慮も必要以上に損なわないものだけを全て挙げた組合せはどれか。",
    ["(1), (2)", "(1), (2), (3)", "(1), (2), (4)", "(2), (3)", "(3), (4)", "(1), (2), (3), (4)"], 2,
    "(1)(2)(4) は紛失時に業務データを守る対策で、業務の領域だけを対象にできる。(3) は私的なデータを会社が見ることになり、紛失対策としても不要で、プライバシーを損なう。")

sec("y10", "SMSによるフィッシング",
    "Q社の社員の私物スマートフォンに「宅配便の不在通知」を装ったSMSが届き、記載されたリンク先で、Q社のクラウドサービスのログイン画面とそっくりな偽の画面にIDとパスワード、"
    "さらにスマートフォンに届いたワンタイムパスワードまで入力してしまった。その直後に、攻撃者が Q社のクラウドサービスにログインしていた。Q社はワンタイムパスワードによる多要素認証を導入済みだった。",
    "この被害を防ぐために最も効果的な対策はどれか。",
    ["ワンタイムパスワードの桁数を増やす",
     "パスワードを定期的に変更させる",
     "正規のサイトのドメインに結び付いた認証器を使う方式（FIDO2 などのパスキー）に変更する",
     "SMSの受信を禁止する",
     "ログイン画面のデザインを変更する"], 2,
    "偽サイトで入力されたワンタイムパスワードは、攻撃者がすぐに正規サイトで使える（リアルタイムのフィッシング）。FIDO2 の認証はサイトのドメインに結び付いているので、偽のドメインでは認証が成立せず、フィッシングに強い。桁数や定期変更ではこの手口は防げない。")

sec("y11", "バックアップの運用",
    "R社では、業務サーバのデータを毎晩、同じサーバ室にある NAS にバックアップしている。バックアップは成功したかどうかだけを確認しており、実際に復元したことはない。"
    "BCP の見直しの中で、次の(1)〜(4)の改善案が出された。\n"
    "(1) バックアップの1世代を、ネットワークから切り離した媒体や遠隔地にも保管する\n(2) 定期的に、バックアップから実際にデータを復元する訓練を行い、かかる時間を測る\n"
    "(3) バックアップの頻度を毎晩から1時間ごとに増やせば、保管場所は今のままでよい\n(4) 目標復旧時点（RPO）と目標復旧時間（RTO）を業務ごとに決め、それに合わせて頻度と方法を決める",
    "改善案として適切なものだけを全て挙げた組合せはどれか。",
    ["(1), (2)", "(1), (2), (4)", "(1), (3)", "(2), (3), (4)", "(3), (4)", "(1), (2), (3), (4)"], 1,
    "同じ部屋やネットワークにあると、火災やランサムウェアで一緒に失われる（1）。復元できるか、時間内に戻せるかは実際に試さないと分からない（2）。頻度は業務の目標から決める（4）。(3) は頻度を上げても保管場所の問題は解決しない。")

sec("y12", "入退室管理",
    "S社のサーバ室は、ICカードをかざすと扉が開く入退室管理システムで管理されている。調査の結果、権限のない社員が、権限のある社員が扉を開けた直後に一緒に入室する「共連れ」が起きていたことが分かった。"
    "システムには、入室と退室の記録が残るが、記録は誰も確認していなかった。",
    "共連れを防ぐための対策として、最も適切なものはどれか。",
    ["ICカードの有効期限を短くする",
     "入室の記録がない者は退室できないようにするアンチパスバックを導入し、1回の認証で1人しか通れないセキュリティゲートを設置する",
     "扉の前に「共連れ禁止」と掲示するだけにする",
     "サーバ室の扉を常に開けておき、監視カメラを設置する",
     "ICカードを全員に配布し、全員がサーバ室に入れるようにする"], 1,
    "アンチパスバックでは、入室の記録がないと退室の認証が通らないので、共連れをした者は出られなくなり、共連れが記録に表れる。セキュリティゲートは物理的に1人ずつしか通れないようにする。掲示だけでは技術的に防げない。")
