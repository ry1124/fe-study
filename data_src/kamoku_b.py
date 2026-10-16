# -*- coding: utf-8 -*-
"""科目Bの問題（擬似言語のアルゴリズム24問・情報セキュリティ8問）。build_data.py が読む。
アルゴリズムの問題には check を付ける。check はPythonで同じ処理を動かし、正解の選択肢の番号（0始まり）を返す。
build_data.py は check の結果が ans と一致し、正解がちょうど1つであることを確かめる。"""

ALGO = []
SEC = []


def algo(id, title, lead, code, ask, opts, ans, exp, check, code_opts=True):
    ALGO.append({"id": id, "title": title, "lead": lead, "code": code.strip("\n"), "ask": ask, "opts": opts,
                 "ans": ans, "exp": exp, "check": check, "codeOpts": code_opts})


def sec(id, title, lead, ask, opts, ans, exp):
    SEC.append({"id": id, "title": title, "lead": lead, "code": "", "ask": ask, "opts": opts,
                "ans": ans, "exp": exp, "check": None, "codeOpts": False})


def only(passing):
    """条件を満たした選択肢がちょうど1つならその番号を返す"""
    idx = [i for i, ok in enumerate(passing) if ok]
    assert len(idx) == 1, f"条件を満たす選択肢が {len(idx)} 個ある: {idx}"
    return idx[0]


def pick(opts, value):
    """出力・戻り値を問う問題：計算した値と同じ文字列の選択肢の番号"""
    return only([o == str(value) for o in opts])


DIV = "ここで、÷ は整数の除算で、商の小数点以下を切り捨てる。"

# ===== 1 =====
def _c1():
    s = 0
    for i in range(1, 8):
        if i % 3 == 0:
            s += i
        elif i % 2 == 0:
            s -= 1
    return pick(["5", "6", "7", "8"], s)

algo("b01", "条件分岐とループのトレース",
     "次の関数 calc は、引数 n を受け取り、整数を返す。",
     """
○整数型: calc(整数型: n)
  整数型: s ← 0
  整数型: i
  for (i を 1 から n まで 1 ずつ増やす)
    if (i mod 3 ＝ 0)
      s ← s ＋ i
    elseif (i mod 2 ＝ 0)
      s ← s − 1
    endif
  endfor
  return s
""",
     "calc(7) の戻り値はどれか。",
     ["5", "6", "7", "8"], 2,
     "i＝2で−1、3で＋3（2）、4で−1（1）、6で＋6（7）。i＝6は3の倍数なので elseif には進まない。1・5・7は何もしない。",
     _c1, code_opts=False)

# ===== 2 =====
def _c2():
    variants = [lambda a, i, k: a[i] > a[k], lambda a, i, k: a[i] >= a[k],
                lambda a, i, k: a[i] > a[i - 1], lambda a, i, k: a[k] > a[i]]
    tests = [[3, 9, 2, 9, 5], [1, 2, 3], [5, 4, 3], [2, 7, 7, 1], [4, 1, 6, 6, 6, 2], [8]]

    def run(f, a):
        a = [None] + a
        k = 1
        for i in range(2, len(a)):
            if f(a, i, k):
                k = i
        return k

    def want(a):
        return a.index(max(a)) + 1
    return only([all(run(f, t) == want(t) for t in tests) for f in variants])

algo("b02", "最大値の要素番号",
     "関数 maxIndex は、整数型の配列 a の要素の中で最大の値を持つ要素の要素番号を返す。最大の値を持つ要素が複数あるときは、その中で最も小さい要素番号を返す。配列の要素番号は1から始まる。",
     """
○整数型: maxIndex(整数型の配列: a)
  整数型: k ← 1
  整数型: i
  for (i を 2 から aの要素数 まで 1 ずつ増やす)
    if (〔 ア 〕)
      k ← i
    endif
  endfor
  return k
""",
     "〔 ア 〕に入れる字句として、適切なものはどれか。",
     ["a[i] ＞ a[k]", "a[i] ≧ a[k]", "a[i] ＞ a[i − 1]", "a[k] ＞ a[i]"], 0,
     "k はそれまでの最大値の位置。a[i] がそれより大きいときだけ k を更新する。≧ にすると同じ値で更新されて最も大きい要素番号になる。a[i] ＞ a[i − 1] は隣と比べているだけで最大値にならない。",
     _c2)

# ===== 3 =====
def _c3():
    variants = [(lambda n: n // 2, lambda n, i: n - i + 1), (lambda n: n, lambda n, i: n - i + 1),
                (lambda n: n // 2, lambda n, i: n - i), (lambda n: n - 1, lambda n, i: n - i)]

    def run(v, a):
        end, idx = v
        a = [None] + list(a)
        n = len(a) - 1
        for i in range(1, end(n) + 1):
            j = idx(n, i)
            if not 1 <= j <= n:
                return None
            a[i], a[j] = a[j], a[i]
        return a[1:]
    tests = [[1, 2, 3, 4], [1, 2, 3, 4, 5], [7], [3, 8]]
    return only([all(run(v, t) == t[::-1] for t in tests) for v in variants])

algo("b03", "配列を逆順に並べ替える",
     "手続 reverse は、整数型の配列 a の要素を逆の順番に並べ替える。配列の要素番号は1から始まる。" + DIV,
     """
○reverse(整数型の配列: a)
  整数型: n ← aの要素数
  整数型: i, tmp
  for (i を 1 から 〔 ア 〕 まで 1 ずつ増やす)
    tmp ← a[i]
    a[i] ← a[〔 イ 〕]
    a[〔 イ 〕] ← tmp
  endfor
""",
     "〔 ア 〕と〔 イ 〕に入れる字句の組合せとして、適切なものはどれか。",
     ["ア：n ÷ 2　イ：n − i ＋ 1", "ア：n　イ：n − i ＋ 1", "ア：n ÷ 2　イ：n − i", "ア：n − 1　イ：n − i"], 0,
     "1番目と n 番目、2番目と n−1 番目…と交換するので相手は n − i ＋ 1。最後まで（n まで）交換すると2回交換して元に戻ってしまうので、半分（n ÷ 2）で止める。要素数が奇数なら真ん中は動かさなくてよい。",
     _c3)

# ===== 4 =====
def _c4():
    x, y, c = 84, 36, 0
    while y != 0:
        x, y = y, x % y
        c += 1
    return pick(["1回、12", "2回、12", "2回、6", "3回、12"], f"{c}回、{x}")

algo("b04", "ユークリッドの互除法",
     "関数 gcd は、正の整数 x と y の最大公約数を返す。",
     """
○整数型: gcd(整数型: x, 整数型: y)
  整数型: r
  while (y ≠ 0)
    r ← x mod y
    x ← y
    y ← r
  endwhile
  return x
""",
     "gcd(84, 36) を呼び出したとき、while の中の処理が実行される回数と、戻り値の組合せとして、適切なものはどれか。",
     ["1回、12", "2回、12", "2回、6", "3回、12"], 1,
     "1回目：r＝84 mod 36＝12、x＝36、y＝12。2回目：r＝36 mod 12＝0、x＝12、y＝0。y＝0 なので終了し、12 を返す。",
     _c4, code_opts=False)

# ===== 5 =====
def _c5():
    def is_prime(n):
        return n >= 2 and all(n % d for d in range(2, n))
    variants = [lambda d, n: d * d <= n, lambda d, n: d < n // 2, lambda d, n: d <= n, lambda d, n: d * d < n]

    def run(f, n):
        d = 2
        while f(d, n):
            if n % d == 0:
                return False
            d += 1
        return True
    return only([all(run(f, n) == is_prime(n) for n in range(2, 200)) for f in variants])

algo("b05", "素数の判定",
     "関数 isPrime は、2以上の整数 n が素数なら true を、そうでなければ false を返す。" + DIV,
     """
○論理型: isPrime(整数型: n)
  整数型: d ← 2
  while (〔 ア 〕)
    if (n mod d ＝ 0)
      return false
    endif
    d ← d ＋ 1
  endwhile
  return true
""",
     "〔 ア 〕に入れる字句として、適切なものはどれか。",
     ["d × d ≦ n", "d ＜ n ÷ 2", "d ≦ n", "d × d ＜ n"], 0,
     "n が素数でないなら、√n 以下の約数が必ずある。d × d ≦ n まで調べれば十分。d ≦ n だと d＝n で必ず割り切れて false になる。d × d ＜ n だと n＝4、9 などの平方数で d＝2、3 を調べずに true を返してしまう。d ＜ n ÷ 2 は n＝4 で1回も調べない。",
     _c5)

# ===== 6 =====
def _c6():
    variants = [lambda s, n: str(n % 2) + s, lambda s, n: s + str(n % 2),
                lambda s, n: str(n // 2) + s, lambda s, n: s + str(n // 2)]

    def run(f, n):
        s = ""
        while n > 0:
            s = f(s, n)
            n //= 2
        return s
    return only([all(run(f, n) == format(n, "b") for n in range(1, 70)) for f in variants])

algo("b06", "10進数を2進数の文字列にする",
     "関数 toBinary は、正の整数 n を2進数で表した文字列を返す。例えば n が 6 のときは \"110\" を返す。関数 intToStr(x) は整数 x を文字列にしたものを返し、文字列どうしの ＋ は連結を表す。" + DIV,
     """
○文字列型: toBinary(整数型: n)
  文字列型: s ← ""
  while (n ＞ 0)
    s ← 〔 ア 〕
    n ← n ÷ 2
  endwhile
  return s
""",
     "〔 ア 〕に入れる字句として、適切なものはどれか。",
     ["intToStr(n mod 2) ＋ s", "s ＋ intToStr(n mod 2)", "intToStr(n ÷ 2) ＋ s", "s ＋ intToStr(n ÷ 2)"], 0,
     "2で割った余りが下の桁から順に求まるので、新しく求めた桁を左側（前）に連結する。s ＋ … にすると逆順の \"011\" になる。",
     _c6)

# ===== 7 =====
def _c7():
    a = [5, 3, 4, 1, 2]
    for j in range(len(a) - 1):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
    return pick(["{3, 4, 1, 2, 5}", "{3, 1, 2, 4, 5}", "{1, 2, 3, 4, 5}", "{3, 5, 4, 1, 2}"],
                "{" + ", ".join(map(str, a)) + "}")

algo("b07", "バブルソートの途中経過",
     "手続 bubble は、整数型の配列 a を昇順に整列する。配列の要素番号は1から始まる。",
     """
○bubble(整数型の配列: a)
  整数型: n ← aの要素数
  整数型: i, j, tmp
  for (i を n から 2 まで 1 ずつ減らす)
    for (j を 1 から i − 1 まで 1 ずつ増やす)
      if (a[j] ＞ a[j ＋ 1])
        tmp ← a[j]
        a[j] ← a[j ＋ 1]
        a[j ＋ 1] ← tmp
      endif
    endfor
  endfor
""",
     "配列 a が {5, 3, 4, 1, 2} のとき、外側の for の1回目（i が 5 のとき）の処理が終わった時点の配列 a の内容はどれか。",
     ["{3, 4, 1, 2, 5}", "{3, 1, 2, 4, 5}", "{1, 2, 3, 4, 5}", "{3, 5, 4, 1, 2}"], 0,
     "隣どうしを比べて大きい方を後ろへ送る。5 が順に交換されて末尾まで移動し {3, 4, 1, 2, 5}。1回目で最大値が末尾に決まる。イは2回目が終わった時点。",
     _c7)

# ===== 8 =====
def _c8():
    data = [None, 2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    low, high, c = 1, 10, 0
    while low <= high:
        c += 1
        mid = (low + high) // 2
        if data[mid] == 23:
            break
        elif data[mid] < 23:
            low = mid + 1
        else:
            high = mid - 1
    return pick(["2", "3", "4", "6"], c)

algo("b08", "2分探索の比較回数",
     "関数 search は、昇順に整列された整数型の配列 data から target を2分探索で探し、見つかった要素番号を返す。見つからなければ −1 を返す。配列の要素番号は1から始まる。" + DIV,
     """
○整数型: search(整数型の配列: data, 整数型: target)
  整数型: low ← 1
  整数型: high ← dataの要素数
  整数型: mid
  while (low ≦ high)
    mid ← (low ＋ high) ÷ 2
    if (data[mid] ＝ target)
      return mid
    elseif (data[mid] ＜ target)
      low ← mid ＋ 1
    else
      high ← mid − 1
    endif
  endwhile
  return −1
""",
     "data が {2, 5, 8, 12, 16, 23, 38, 56, 72, 91}、target が 23 のとき、while の中の処理は何回実行されるか。",
     ["2", "3", "4", "6"], 1,
     "1回目：low＝1、high＝10、mid＝5、data[5]＝16 ＜ 23 → low＝6。2回目：mid＝(6＋10)÷2＝8、data[8]＝56 ＞ 23 → high＝7。3回目：mid＝6、data[6]＝23 で見つかる。",
     _c8, code_opts=False)

# ===== 9 =====
def _c9():
    variants = [lambda i, j: j, lambda i, j: j + 1, lambda i, j: j - 1, lambda i, j: i]

    def run(f, a):
        a = [None] + list(a)
        n = len(a) - 1
        for i in range(2, n + 1):
            x = a[i]
            j = i - 1
            while j >= 1 and a[j] > x:
                a[j + 1] = a[j]
                j -= 1
            k = f(i, j)
            if not 1 <= k <= n:
                return None
            a[k] = x
        return a[1:]
    tests = [[4, 2, 5, 1, 3], [1, 2, 3], [3, 2, 1], [2, 2, 1, 3]]
    return only([all(run(f, t) == sorted(t) for t in tests) for f in variants])

algo("b09", "挿入ソート",
     "手続 insertionSort は、整数型の配列 a を昇順に整列する。配列の要素番号は1から始まる。なお、and の左側が false のときは右側を評価しない。",
     """
○insertionSort(整数型の配列: a)
  整数型: n ← aの要素数
  整数型: i, j, x
  for (i を 2 から n まで 1 ずつ増やす)
    x ← a[i]
    j ← i − 1
    while ((j ≧ 1) and (a[j] ＞ x))
      a[j ＋ 1] ← a[j]
      j ← j − 1
    endwhile
    a[〔 ア 〕] ← x
  endfor
""",
     "〔 ア 〕に入れる字句として、適切なものはどれか。",
     ["j", "j ＋ 1", "j − 1", "i"], 1,
     "while を抜けたとき、a[j] は x 以下（または j＝0）。x はその1つ後ろ、j ＋ 1 の位置に入れる。具体例 {4, 2} で i＝2：x＝2、j＝1 で 4 ＞ 2 なので a[2]←4、j＝0。a[1] に 2 を入れるので j ＋ 1。",
     _c9)

# ===== 10 =====
def _c10():
    cnt = 0

    def f(n):
        nonlocal cnt
        cnt += 1
        if n <= 1:
            return n
        return f(n - 1) + f(n - 2)
    f(5)
    return pick(["5", "8", "15", "25"], cnt)

algo("b10", "再帰呼出しの回数",
     "関数 f は、フィボナッチ数を再帰的に求める。",
     """
○整数型: f(整数型: n)
  if (n ≦ 1)
    return n
  endif
  return f(n − 1) ＋ f(n − 2)
""",
     "f(5) を呼び出したとき、関数 f が呼び出される回数は、最初の呼出しも含めて何回か。",
     ["5", "8", "15", "25"], 2,
     "呼出し回数を C(n) とすると C(0)＝C(1)＝1、C(n)＝1＋C(n−1)＋C(n−2)。C(2)＝3、C(3)＝5、C(4)＝9、C(5)＝1＋9＋5＝15。f(5) の値（5）と混同しない。",
     _c10, code_opts=False)

# ===== 11 =====
def _c11():
    out = []

    def proc(n):
        if n == 0:
            return
        proc(n // 2)
        out.append(str(n % 2))
    proc(13)
    return pick(["1011", "1101", "0111", "1100"], "".join(out))

algo("b11", "再帰で出力する順番",
     "手続 proc は、整数 n を受け取り、値を出力する。出力は区切りなしで続けて表示される。" + DIV,
     """
○proc(整数型: n)
  if (n ＝ 0)
    return
  endif
  proc(n ÷ 2)
  n mod 2 を出力する
""",
     "proc(13) を呼び出したときの出力はどれか。",
     ["1011", "1101", "0111", "1100"], 1,
     "先に proc(n ÷ 2) を呼んでから出力するので、一番深い呼出しの出力が最初に出る。13→6→3→1→0。出力は proc(1) の 1、proc(3) の 1、proc(6) の 0、proc(13) の 1 の順で \"1101\"（13 の2進数）。出力を先にすると逆順の \"1011\" になる。",
     _c11, code_opts=False)

# ===== 12 =====
class _E:
    def __init__(self, v):
        self.val, self.next = v, None


def _c12():
    variants = [("none", "curr"), ("none", "head"), ("some", "curr"), ("some", "head")]

    def run(v):
        head = None
        for x in [1, 2, 3]:
            curr = _E(x)
            cond = head is None if v[0] == "none" else head is not None
            if cond:
                head = curr
            else:
                if head is None:
                    return None
                prev, steps = head, 0
                while prev.next is not None:
                    prev, steps = prev.next, steps + 1
                    if steps > 10:   # 誤った選択肢でリストが輪になった
                        return None
                prev.next = curr if v[1] == "curr" else head
        out, p, guard = [], head, 0
        while p is not None and guard < 10:
            out.append(p.val)
            p, guard = p.next, guard + 1
        return out
    return only([run(v) == [1, 2, 3] for v in variants])

algo("b12", "連結リストの末尾に追加する",
     "ListElement は連結リストの要素を表すクラスで、属性 val に値、属性 next に次の要素への参照を持つ。次の要素がないときの next は未定義である。ListElement(x) は val が x、next が未定義の新しい要素を作って返す。大域変数 listHead はリストの先頭の要素を参照し、リストが空のときは未定義である。手続 append は、値 qVal を持つ要素をリストの末尾に追加する。",
     """
大域: ListElement: listHead ← 未定義

○append(整数型: qVal)
  ListElement: prev, curr
  curr ← ListElement(qVal)
  if (listHead が 〔 ア 〕)
    listHead ← curr
  else
    prev ← listHead
    while (prev.next が 未定義 でない)
      prev ← prev.next
    endwhile
    prev.next ← 〔 イ 〕
  endif
""",
     "〔 ア 〕と〔 イ 〕に入れる字句の組合せとして、適切なものはどれか。",
     ["ア：未定義　イ：curr", "ア：未定義　イ：listHead", "ア：未定義でない　イ：curr", "ア：未定義でない　イ：listHead"], 0,
     "リストが空（listHead が未定義）なら新しい要素が先頭になる。そうでなければ next が未定義の要素（末尾）までたどり、その next に新しい要素 curr をつなぐ。listHead をつなぐと循環してしまう。",
     _c12)

# ===== 13 =====
def _c13():
    variants = ["prev.next = curr.next", "curr.next = prev.next", "prev = curr.next", "prev.next = curr"]

    def build(xs):
        head = None
        for x in reversed(xs):
            e = _E(x)
            e.next = head
            head = e
        return head

    def to_list(head):
        out, p, g = [], head, 0
        while p is not None and g < 20:
            out.append(p.val)
            p, g = p.next, g + 1
        return out

    def run(stmt, xs, x):
        head = build(xs)
        if head.val == x:
            return to_list(head.next)
        prev, curr = head, head.next
        while curr.val != x:
            prev, curr = curr, curr.next
        if stmt == "prev.next = curr.next": prev.next = curr.next
        elif stmt == "curr.next = prev.next": curr.next = prev.next
        elif stmt == "prev = curr.next": prev = curr.next
        else: prev.next = curr
        return to_list(head)

    def want(xs, x):
        ys = list(xs)
        ys.remove(x)
        return ys
    tests = [([1, 2, 3, 4], 3), ([1, 2, 3, 4], 4), ([5, 6], 6), ([7, 8, 9], 7), ([1, 2, 2, 3], 2)]
    return only([all(run(s, xs, x) == want(xs, x) for xs, x in tests) for s in variants])

algo("b13", "連結リストから要素を削除する",
     "ListElement と大域変数 listHead は、前の問題と同じである。手続 delete は、リストを先頭からたどって最初に見つかった値 x を持つ要素を、リストから取り除く。値 x を持つ要素は必ずリストに存在する。",
     """
○delete(整数型: x)
  ListElement: prev, curr
  if (listHead.val ＝ x)
    listHead ← listHead.next
    return
  endif
  prev ← listHead
  curr ← listHead.next
  while (curr.val ≠ x)
    prev ← curr
    curr ← curr.next
  endwhile
  〔 ア 〕
""",
     "〔 ア 〕に入れる字句として、適切なものはどれか。",
     ["prev.next ← curr.next", "curr.next ← prev.next", "prev ← curr.next", "prev.next ← curr"], 0,
     "curr が削除する要素、prev がその1つ前。prev の次を、curr を飛ばして curr の次にすれば取り除ける。prev ← curr.next は変数 prev を書き換えるだけで、リストは変わらない。",
     _c13)

# ===== 14 =====
def _c14():
    m = [[1, 2, 3], [4, 5, 6], [7, 8, 10]]
    s = sum(m[i - 1][4 - i - 1] for i in range(1, 4))
    return pick(["15", "16", "18", "45"], s)

algo("b14", "2次元配列の要素の和",
     "二次元配列 m の要素 m[i, j] は、i 行目 j 列目の要素を表す。行も列も番号は1から始まる。m は {{1, 2, 3}, {4, 5, 6}, {7, 8, 10}} で、{1, 2, 3} が1行目である。",
     """
大域: 整数型の二次元配列: m ← {{1, 2, 3}, {4, 5, 6}, {7, 8, 10}}

○整数型: f()
  整数型: i
  整数型: s ← 0
  for (i を 1 から 3 まで 1 ずつ増やす)
    s ← s ＋ m[i, 4 − i]
  endfor
  return s
""",
     "f() の戻り値はどれか。",
     ["15", "16", "18", "45"], 0,
     "i＝1 で m[1, 3]＝3、i＝2 で m[2, 2]＝5、i＝3 で m[3, 1]＝7。右上から左下への対角線の和で 15。左上から右下の対角線（m[i, i]）なら 1＋5＋10＝16。",
     _c14, code_opts=False)

# ===== 15 =====
def _c15():
    variants = [lambda c, n, i: c[n - i + 1], lambda c, n, i: c[n - i], lambda c, n, i: c[i + 1],
                lambda c, n, i: c[n // 2 - i + 1]]

    def run(f, word):
        c = [None] + list(word)
        n = len(word)
        for i in range(1, n // 2 + 1):
            try:
                if c[i] != f(c, n, i):
                    return False
            except IndexError:
                return None
        return True
    words = ["level", "abba", "abca", "a", "ab", "aa", "racecar", "abcda", "xyzx"]
    return only([all(run(f, w) == (w == w[::-1]) for w in words) for f in variants])

algo("b15", "回文の判定",
     "関数 isPalindrome は、文字型の配列 c に格納された文字の並びが、前から読んでも後ろから読んでも同じ（回文）であれば true を、そうでなければ false を返す。配列の要素番号は1から始まる。" + DIV,
     """
○論理型: isPalindrome(文字型の配列: c)
  整数型: n ← cの要素数
  整数型: i
  for (i を 1 から n ÷ 2 まで 1 ずつ増やす)
    if (c[i] ≠ 〔 ア 〕)
      return false
    endif
  endfor
  return true
""",
     "〔 ア 〕に入れる字句として、適切なものはどれか。",
     ["c[n − i ＋ 1]", "c[n − i]", "c[i ＋ 1]", "c[n ÷ 2 − i ＋ 1]"], 0,
     "前から i 番目と後ろから i 番目（n − i ＋ 1 番目）を比べる。i＝1 のとき相手は n 番目になるか確かめるとよい。c[n − i] だと i＝1 で n−1 番目と比べてしまう。",
     _c15)

# ===== 16 =====
def _c16():
    # 選択肢の順に 0〜3 の処理を実行する
    def run(k, data):
        cnt = [None] + [0] * 5
        for i in range(1, len(data) + 1):
            d = data[i - 1]
            if k == 0:
                if i > 5: return None
                cnt[i] += 1
            elif k == 1: cnt[d] += 1
            elif k == 2: cnt[d] = d + 1
            else:
                if i > 5: return None
                cnt[i] = d
        return cnt[1:]
    tests = [[3, 1, 3, 5, 2, 3], [1, 1, 1], [5, 4, 3, 2, 1], [2]]
    return only([all(run(k, t) == [t.count(v) for v in range(1, 6)] for t in tests) for k in range(4)])

algo("b16", "値ごとの個数を数える",
     "関数 count は、1〜5 の整数だけが入った整数型の配列 data を受け取り、値 v（1〜5）の個数を cnt[v] に入れた配列 cnt を返す。配列の要素番号は1から始まる。",
     """
○整数型の配列: count(整数型の配列: data)
  整数型の配列: cnt ← {0, 0, 0, 0, 0}
  整数型: i
  for (i を 1 から dataの要素数 まで 1 ずつ増やす)
    〔 ア 〕
  endfor
  return cnt
""",
     "〔 ア 〕に入れる字句として、適切なものはどれか。",
     ["cnt[i] ← cnt[i] ＋ 1", "cnt[data[i]] ← cnt[data[i]] ＋ 1", "cnt[data[i]] ← data[i] ＋ 1", "cnt[i] ← data[i]"], 1,
     "data[i] の値そのものを cnt の要素番号に使い、その場所を1増やす。例えば data[i] が 3 なら cnt[3] を1増やす。",
     _c16)

# ===== 17 =====
def _c17():
    a = [4, 2, 5, 1, 3]
    n, swaps = len(a), 0
    for i in range(n - 1):
        k = i
        for j in range(i + 1, n):
            if a[j] < a[k]:
                k = j
        if k != i:
            a[i], a[k] = a[k], a[i]
            swaps += 1
    return pick(["1", "2", "3", "4"], swaps)

algo("b17", "選択ソートの交換回数",
     "手続 selectionSort は、整数型の配列 a を昇順に整列する。配列の要素番号は1から始まる。",
     """
○selectionSort(整数型の配列: a)
  整数型: n ← aの要素数
  整数型: i, j, k, tmp
  for (i を 1 から n − 1 まで 1 ずつ増やす)
    k ← i
    for (j を i ＋ 1 から n まで 1 ずつ増やす)
      if (a[j] ＜ a[k])
        k ← j
      endif
    endfor
    if (k ≠ i)
      tmp ← a[i]
      a[i] ← a[k]
      a[k] ← tmp
    endif
  endfor
""",
     "配列 a が {4, 2, 5, 1, 3} のとき、要素の交換（if (k ≠ i) の中の処理）は何回行われるか。",
     ["1", "2", "3", "4"], 1,
     "i＝1：最小値1（4番目）と交換 → {1, 2, 5, 4, 3}。i＝2：最小値は2で位置は2のまま、交換なし。i＝3：最小値3（5番目）と交換 → {1, 2, 3, 4, 5}。i＝4：交換なし。計2回。",
     _c17, code_opts=False)

# ===== 18 =====
def _c18():
    variants = [("stack[top]", -1), ("stack[top-1]", -1), ("stack[top]", +1), ("stack[1]", -1)]

    def run(v):
        stack, top, out = [None] * 12, 0, []

        def push(x):
            nonlocal top
            top += 1
            stack[top] = x

        def pop():
            nonlocal top
            x = {"stack[top]": stack[top], "stack[top-1]": stack[top - 1], "stack[1]": stack[1]}[v[0]]
            top += v[1]
            return x
        try:
            push(1); push(2); out.append(pop()); push(3); push(4); out.append(pop()); out.append(pop()); out.append(pop())
        except (IndexError, TypeError):
            return None
        return out
    return only([run(v) == [2, 4, 3, 1] for v in variants])

algo("b18", "配列でスタックを作る",
     "大域変数の配列 stack と top を使ってスタックを実現する。top は最後に積んだ要素の要素番号で、スタックが空のときは 0 である。配列の要素番号は1から始まり、要素数は十分に大きいものとする。空のスタックから pop することはない。",
     """
大域: 整数型の配列: stack ← {要素数 100 の配列}
大域: 整数型: top ← 0

○push(整数型: x)
  top ← top ＋ 1
  stack[top] ← x

○整数型: pop()
  整数型: x ← 〔 ア 〕
  〔 イ 〕
  return x
""",
     "〔 ア 〕と〔 イ 〕に入れる字句の組合せとして、適切なものはどれか。",
     ["ア：stack[top]　イ：top ← top − 1", "ア：stack[top − 1]　イ：top ← top − 1",
      "ア：stack[top]　イ：top ← top ＋ 1", "ア：stack[1]　イ：top ← top − 1"], 0,
     "最後に積んだ要素は stack[top] にある。それを取り出したら top を1減らす。stack[1] は最初に積んだ要素なので、キューのような動きになってしまう。",
     _c18)

# ===== 19 =====
def _c19():
    variants = [lambda t: t % 5 + 1, lambda t: t % 5, lambda t: (t + 1) % 5, lambda t: t + 1]

    def run(f):
        q, head, tail, out = [None] * 7, 1, 1, []

        def enq(x):
            nonlocal tail
            if not 1 <= tail <= 5:
                raise IndexError
            q[tail] = x
            tail = f(tail)

        def deq():
            nonlocal head
            x = q[head]
            head = head % 5 + 1
            return x
        try:
            for x in [1, 2, 3, 4]: enq(x)
            out += [deq(), deq(), deq()]
            for x in [5, 6, 7, 8]: enq(x)
            out += [deq() for _ in range(5)]
        except IndexError:
            return None
        return out
    return only([run(f) == [1, 2, 3, 4, 5, 6, 7, 8] for f in variants])

algo("b19", "配列を環状に使うキュー",
     "要素数5の配列 q（要素番号は1〜5）を環状に使ってキューを実現する。tail は次に値を入れる要素番号で、5 の次は 1 に戻る。キューがあふれる操作や、空のキューから取り出す操作は行わない。",
     """
大域: 整数型の配列: q ← {0, 0, 0, 0, 0}
大域: 整数型: head ← 1
大域: 整数型: tail ← 1

○enqueue(整数型: x)
  q[tail] ← x
  tail ← 〔 ア 〕

○整数型: dequeue()
  整数型: x ← q[head]
  head ← head mod 5 ＋ 1
  return x
""",
     "〔 ア 〕に入れる字句として、適切なものはどれか。",
     ["tail mod 5 ＋ 1", "tail mod 5", "(tail ＋ 1) mod 5", "tail ＋ 1"], 0,
     "1→2→3→4→5→1 と進めたい。tail mod 5 ＋ 1 なら tail＝5 で 0＋1＝1 に戻る。tail mod 5 は tail＝1 で 1 のまま進まない。(tail ＋ 1) mod 5 は tail＝4 で 0 になり範囲外。tail ＋ 1 は 6 になって範囲外。",
     _c19)

# ===== 20 =====
def _c20():
    n, cnt = 10, 0
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            cnt += 1
    return pick(["45", "55", "100", "110"], cnt)

algo("b20", "2重ループの実行回数",
     "次のプログラムで、n は正の整数である。",
     """
○整数型: loopCount(整数型: n)
  整数型: i, j
  整数型: cnt ← 0
  for (i を 1 から n まで 1 ずつ増やす)
    for (j を i から n まで 1 ずつ増やす)
      cnt ← cnt ＋ 1
    endfor
  endfor
  return cnt
""",
     "loopCount(10) の戻り値はどれか。",
     ["45", "55", "100", "110"], 1,
     "i＝1 で10回、i＝2 で9回、…、i＝10 で1回。10＋9＋…＋1＝55＝n(n＋1)/2。j が i ＋ 1 から始まるなら45。計算量は O(n²)。",
     _c20, code_opts=False)

# ===== 21 =====
def _c21():
    a, b = [1, 4, 7], [2, 3, 8, 9]
    i = j = 0
    c = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            c.append(a[i]); i += 1
        else:
            c.append(b[j]); j += 1
    return pick(["3", "4", "5", "7"], len(c))

algo("b21", "整列済みの配列を併合する",
     "関数 merge は、昇順に整列された整数型の配列 a と b を併合し、昇順に整列した配列 c を返す。配列の要素番号は1から始まる。",
     """
○整数型の配列: merge(整数型の配列: a, 整数型の配列: b)
  整数型の配列: c ← {要素数が aの要素数 ＋ bの要素数 の配列}
  整数型: i ← 1, j ← 1, k ← 1
  while ((i ≦ aの要素数) and (j ≦ bの要素数))
    if (a[i] ≦ b[j])
      c[k] ← a[i]
      i ← i ＋ 1
    else
      c[k] ← b[j]
      j ← j ＋ 1
    endif
    k ← k ＋ 1
  endwhile
  /* ここで、残った要素を c の後ろに順に移す（省略） */
  return c
""",
     "a が {1, 4, 7}、b が {2, 3, 8, 9} のとき、最初の while を抜けた時点で、c に格納されている要素の個数はどれか。",
     ["3", "4", "5", "7"], 2,
     "1(a)、2(b)、3(b)、4(a)、7(a) の順に入る。7 を入れた時点で i＝4 となり a を使い切るので while を抜ける。5個。残りの 8、9 は後の処理で移される。",
     _c21, code_opts=False)

# ===== 22 =====
def _c22():
    table = [None] + [-1] * 10
    pos = {}
    for key in [19, 29, 9]:
        h = key % 10 + 1
        while table[h] != -1:
            h = h % 10 + 1
        table[h] = key
        pos[key] = h
    return pick(["1", "2", "9", "10"], pos[9])

algo("b22", "ハッシュ表への格納（衝突の処理）",
     "要素数10の配列 table（要素番号は1〜10）をハッシュ表として使う。最初は全ての要素が −1（空き）である。手続 insert は、キー key を、key mod 10 ＋ 1 番目に格納する。そこが空いていなければ、次の要素番号（10 の次は 1）を順に調べ、最初に見つかった空きに格納する。",
     """
大域: 整数型の配列: table ← {−1, −1, −1, −1, −1, −1, −1, −1, −1, −1}

○insert(整数型: key)
  整数型: h ← key mod 10 ＋ 1
  while (table[h] ≠ −1)
    h ← h mod 10 ＋ 1
  endwhile
  table[h] ← key
""",
     "空の table に、insert(19)、insert(29)、insert(9) の順に実行したとき、9 が格納される要素番号はどれか。",
     ["1", "2", "9", "10"], 1,
     "19：19 mod 10 ＋ 1＝10 に格納。29：10 は使用中 → 10 mod 10 ＋ 1＝1 に格納。9：10 使用中 → 1 使用中 → 2 に格納。",
     _c22, code_opts=False)

# ===== 23 =====
def _c23():
    variants = [lambda s, a, i: s[i - 1] + a[i], lambda s, a, i: s[i] + a[i - 1],
                lambda s, a, i: a[i - 1] + a[i], lambda s, a, i: s[i - 1] + a[i - 1]]

    def run(f, a):
        a = [None] + a
        n = len(a) - 1
        s = [None] + [0] * n
        s[1] = a[1]
        for i in range(2, n + 1):
            s[i] = f(s, a, i)
        return s[1:]

    def want(a):
        return [sum(a[:i + 1]) for i in range(len(a))]
    tests = [[3, 1, 4, 1, 5], [2, 7], [1, 1, 1, 1], [5, -2, 8]]
    return only([all(run(f, t) == want(t) for t in tests) for f in variants])

algo("b23", "累積和",
     "関数 prefixSum は、整数型の配列 a を受け取り、a[1] から a[i] までの和を s[i] に入れた配列 s を返す。例えば a が {3, 1, 4} なら {3, 4, 8} を返す。配列の要素番号は1から始まる。",
     """
○整数型の配列: prefixSum(整数型の配列: a)
  整数型: n ← aの要素数
  整数型の配列: s ← {要素数 n の配列}
  整数型: i
  s[1] ← a[1]
  for (i を 2 から n まで 1 ずつ増やす)
    s[i] ← 〔 ア 〕
  endfor
  return s
""",
     "〔 ア 〕に入れる字句として、適切なものはどれか。",
     ["s[i − 1] ＋ a[i]", "s[i] ＋ a[i − 1]", "a[i − 1] ＋ a[i]", "s[i − 1] ＋ a[i − 1]"], 0,
     "1つ前までの和 s[i − 1] に、今の要素 a[i] を足す。例 {3, 1, 4} の i＝2：s[1]＋a[2]＝3＋1＝4。a[i − 1] ＋ a[i] は隣どうしの和にしかならない。",
     _c23)

# ===== 24 =====
def _c24():
    def judge(x, y):
        if x > 10 or y > 10 and x > y:
            return 1
        elif not (x == y):
            return 2
        return 3
    return pick(["1", "2", "3", "4"], judge(12, 15))

algo("b24", "and と or の優先順位",
     "関数 judge は、2つの整数を受け取り、1〜3 のいずれかを返す。演算子の優先順位は、not が最も高く、次に関係演算子（＞ ＝ など）、次に and、最も低いのが or である。",
     """
○整数型: judge(整数型: x, 整数型: y)
  if (x ＞ 10 or y ＞ 10 and x ＞ y)
    return 1
  elseif (not (x ＝ y))
    return 2
  endif
  return 3
""",
     "judge(12, 15) の戻り値はどれか。",
     ["1", "2", "3", "4"], 0,
     "and が or より先なので、条件は「x ＞ 10」or「(y ＞ 10 and x ＞ y)」。x＝12 で x ＞ 10 が true なので全体が true になり 1 を返す。左から順に (x ＞ 10 or y ＞ 10) and x ＞ y と計算すると false になり、誤って 2 を選んでしまう。",
     _c24, code_opts=False)


# ===== 情報セキュリティ =====
sec("s01", "マルウェア感染が疑われるときの初動",
    "A社の営業部の社員Bさんが、取引先を名乗るメールの添付ファイルを開いたところ、PCの動作が急に遅くなり、見覚えのないウィンドウが一瞬表示された。A社の規程では、マルウェア感染が疑われる場合は情報システム部に連絡することになっている。PCは有線LANで社内ネットワークに接続されており、社内のファイルサーバにもアクセスできる。",
    "Bさんが、情報システム部に連絡する前に、まず行うべきこととして最も適切なものはどれか。",
    ["PCの電源をすぐに切る", "LANケーブルを抜いて、PCをネットワークから切り離す",
     "ウイルス対策ソフトでフルスキャンを行い、結果が出るまで作業を続ける",
     "添付ファイルを削除し、ごみ箱も空にする", "同じメールを受け取った可能性のある同僚に、そのメールを転送して注意を促す"], 1,
    "感染の拡大（ファイルサーバなど他の機器への感染）を防ぐため、まずネットワークから切り離す。電源を切るとメモリ上の痕跡などの調査に必要な情報が失われるおそれがある。ファイルの削除も証拠を消すことになる。疑わしいメールを転送すると被害が広がる。")

sec("s02", "退職者のアカウント管理",
    "C社では、社員の入社時に業務システムのアカウントを情報システム部が作成している。退職時には、本人の所属部署から総務部に退職届が出されるが、情報システム部には連絡されない。先日の点検で、退職者のアカウントが30件以上残っており、そのうち1件で退職後にログインした記録が見つかった。",
    "この問題の再発を防ぐための対策として、最も適切なものはどれか。",
    ["全社員のパスワードを、毎月変更させる", "退職の手続に、情報システム部へのアカウント削除の依頼を組み込み、さらに定期的にアカウントの棚卸しを行う",
     "業務システムへのログインを、社内ネットワークからだけに制限する", "退職者が使っていたPCを初期化する",
     "ログインの記録を保存する期間を延ばす"], 1,
    "原因は「退職の情報が情報システム部に届かない」こと。手続に削除依頼を組み込み、漏れがないか定期的に棚卸し（実際の在籍者とアカウントを突き合わせる）するのが根本的な対策。ほかの選択肢は、退職者のアカウントが残る原因を解決しない。")

sec("s03", "メールの誤送信",
    "D社の社員が、複数の顧客に案内メールを送る際、全員のメールアドレスを宛先（To）に入れて送信したため、顧客どうしにお互いのメールアドレスが知られてしまった。D社では、メールの送信は各社員の判断に任されており、送信前の確認の仕組みはない。",
    "同じ事故を防ぐための対策として、最も適切なものはどれか。",
    ["メールの本文を暗号化する", "複数の社外アドレスを To や Cc に入れて送信しようとしたときに警告を出し、送信を一定時間保留して取り消せるようにする",
     "迷惑メールフィルタを導入する", "メールサーバをクラウドサービスに移行する", "メールの送信ログを1年間保存する"], 1,
    "複数の顧客に一斉に送るときは Bcc を使う、あるいは警告と送信保留で誤りに気付けるようにするのが有効。本文の暗号化や迷惑メールフィルタは、宛先を全員に見せてしまう問題を防がない。")

sec("s04", "パスワードリスト攻撃への対策",
    "E社が運営する通販サイトで、短時間に多数の異なるIPアドレスから、多数の異なる利用者IDでログインが試みられた。1つの利用者IDあたりのログイン失敗は1〜2回だけだったが、一部の利用者IDではログインに成功しており、登録情報が閲覧されていた。調査の結果、ログインに成功した利用者は、他のサービスと同じパスワードを使っていたことがわかった。E社のサイトでは、同じ利用者IDで5回続けてログインに失敗するとアカウントをロックする設定になっている。",
    "この攻撃への対策として、最も効果的なものはどれか。",
    ["アカウントをロックするまでの失敗回数を、5回から3回に減らす", "ログイン時に、パスワードに加えて、登録したスマートフォンに送る確認コードの入力を求める（多要素認証）",
     "パスワードの最低文字数を8文字から10文字に増やす", "通信をTLSで暗号化する", "ログインに失敗したIPアドレスを1つずつ手作業で遮断する"], 1,
    "他のサービスから漏れたIDとパスワードの組を使うパスワードリスト攻撃。正しいパスワードで1〜2回で成功しているので、ロックの回数を減らしても防げない。攻撃元のIPアドレスも多数で、手作業の遮断は追いつかない。パスワードが知られていても、所持の要素がなければログインできない多要素認証が効果的。")

sec("s05", "取引先を装った振込先変更の依頼",
    "F社の経理担当者に、いつも取引している G社の担当者の名前で「振込先の口座が変わったので、今月の支払からは新しい口座に振り込んでほしい」というメールが届いた。メールの署名や文面はいつもと同じだったが、送信元のメールアドレスのドメイン名が、G社の正しいドメイン名と1文字だけ違っていた。",
    "F社の対応として、最も適切なものはどれか。",
    ["メールの文面と署名がいつもと同じなので、新しい口座に振り込む", "届いたメールに返信して、振込先の変更が本当かどうかを確認する",
     "以前から把握しているG社の電話番号など、メール以外の方法でG社の担当者に確認する", "メールを削除し、今月の支払は保留して、G社から連絡が来るのを待つ",
     "新しい口座に少額を試しに振り込んでみて、G社から苦情が来なければ残りを振り込む"], 2,
    "ビジネスメール詐欺（BEC）の典型。そのメールに返信すると攻撃者が答えるだけなので、メール以外の確かな経路（以前から知っている電話番号など）で確認する。連絡を待つだけでは本物の取引にも支障が出る。")

sec("s06", "ランサムウェアとバックアップ",
    "H社では、ファイルサーバのデータを、毎晩同じ社内ネットワーク上のNAS（ネットワーク接続型の記憶装置）にバックアップしていた。ある日、社員のPCがランサムウェアに感染し、ファイルサーバのデータだけでなく、NASのバックアップデータも暗号化されて、復元できなくなった。",
    "今後の対策として、最も適切なものはどれか。",
    ["バックアップの取得を毎晩から1時間ごとに増やす", "バックアップデータを、ネットワークから切り離した媒体や、書換えのできない保管先にも保管する",
     "NASの容量を増やして、より多くの世代を保存する", "ファイルサーバのアクセス権を全員読取り専用にする", "バックアップデータを圧縮して保存する"], 1,
    "ランサムウェアは、ネットワークでつながった保存先まで暗号化する。バックアップを取る頻度や世代を増やしても、同じネットワーク上にあれば一緒に暗号化される。オフライン（切り離した場所）や変更できない保管先に置くことが有効。全員を読取り専用にすると業務ができない。")

sec("s07", "USBメモリの紛失",
    "I社の社員が、顧客の個人情報を含むファイルをUSBメモリにコピーして社外に持ち出し、移動中に紛失した。I社では、USBメモリの利用は禁止されていなかったが、使用できるUSBメモリの種類やデータの暗号化についての決まりはなかった。",
    "同じような事故が起きても情報が漏えいしないようにするための対策として、最も適切なものはどれか。",
    ["USBメモリに保存するファイルの名前を、内容がわからないものにする", "会社が支給する、暗号化機能とパスワードロック機能を持つUSBメモリだけを使用できるように、PCの設定で制限する",
     "USBメモリを紛失したときは、すぐに警察に届け出ることを規程に定める", "USBメモリにウイルス対策ソフトを入れる", "持ち出したUSBメモリは、帰社後すぐにデータを消去させる"], 1,
    "紛失しても中身を読めないようにするのが情報漏えいの対策。暗号化されたUSBメモリだけを使えるように技術的に制限する。ファイル名を変えても中身は読める。届出や帰社後の消去は、紛失した時点の漏えいを防がない。")

sec("s08", "クラウドストレージの共有設定",
    "J社では、取引先とのファイルのやり取りにクラウドストレージを利用している。ある社員が、取引先に資料を渡すために、フォルダを「リンクを知っている全員が閲覧可能」の設定で共有した。そのフォルダには、取引先に関係のない社内の人事資料も入っていた。後日、そのリンクがインターネット上の掲示板に書き込まれているのが見つかった。",
    "この事故の再発防止策として、最も適切なものはどれか。",
    ["クラウドストレージの利用を全面的に禁止する", "共有は相手のアカウントを指定する方法だけを許可し、「リンクを知っている全員」での共有は管理者の設定で使えないようにする",
     "共有リンクの文字列を長くする", "フォルダの名前に「社外秘」と付ける", "取引先に、リンクを他人に教えないよう口頭で依頼する"], 1,
    "「リンクを知っている全員」の設定では、リンクが漏れると誰でも見られる。相手を指定した共有に限定すれば、リンクが漏れてもアカウントのない人は閲覧できない。全面禁止は業務が止まるので適切ではない。名前の工夫や口頭の依頼では技術的に防げない。")
