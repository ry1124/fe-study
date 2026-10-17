// 基本情報技術者 1週間合格プラン: 今日やること・テキスト・問題(科目A/科目B)・本番形式の模擬試験・計画・記録
const D = FE_DATA;
const PLAN = D.plan;          // 1日目〜7日目
const SUBJ = D.subjects[0];
const CHAPTERS = {};          // 章id -> 章
const QUESTIONS = {};         // 問題id -> 問題(+章id)
SUBJ.chapters.forEach((c) => {
  CHAPTERS[c.id] = c;
  c.quiz.forEach((q) => { QUESTIONS[q.id] = Object.assign({ ch: c.id }, q); });
});
// IPAの過去問(問題は原文の画像。出典つき)
const PAST_SETS = {};         // セットid -> { title, part, mock, ids }
D.past.forEach((q) => { QUESTIONS[q.id] = q; });
D.pastSets.forEach((s) => { PAST_SETS[s.id] = s; });
const PAST_IDS = D.past.map((q) => q.id);
const A_IDS = Object.keys(QUESTIONS).filter((id) => QUESTIONS[id].t === 'a');
const B_IDS = Object.keys(QUESTIONS).filter((id) => QUESTIONS[id].t === 'b');
const KANA = ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ'];

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const WD = ['日', '月', '火', '水', '木', '金', '土'];
const PART_LABEL = { a: '科目A', b: '科目B' };
// 科目Bの問題の種類。algo・sec が本試験レベル(模試に出す)、algo0・sec0 が基礎
const B_KIND_LABEL = { algo: 'アルゴリズム（本試験レベル）', sec: '情報セキュリティ（本試験レベル）', algo0: 'アルゴリズム（基礎）', sec0: '情報セキュリティ（基礎）' };

// ===== 日付 =====
function ymd(n) {
  return `${n.getFullYear()}-${String(n.getMonth() + 1).padStart(2, '0')}-${String(n.getDate()).padStart(2, '0')}`;
}
function todayStr() { return ymd(new Date()); }
function parseDay(s) { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); }
function addDays(s, n) { const d = parseDay(s); d.setDate(d.getDate() + n); return ymd(d); }
function daysBetween(a, b) { return Math.round((parseDay(b) - parseDay(a)) / 86400000); }
function fmtDay(s, withYear) {
  const d = parseDay(s);
  return `${withYear ? d.getFullYear() + '年' : ''}${d.getMonth() + 1}月${d.getDate()}日（${WD[d.getDay()]}）`;
}

// n日目の日付(1日目を決めていなければ null)
function dayDate(n) { return state.start ? addDays(state.start, n - 1) : null; }
// 今日が何日目か(1日目より前は0以下、7日目より後は8以上。未設定は null)
function todayN() { return state.start ? daysBetween(state.start, todayStr()) + 1 : null; }
const LAST = PLAN.length;
const CBT_LAST = '2026-12-27'; // CBT方式の休止前の最終受験日の見込み(IPA発表: 2026年12月28日以降は休止予定)

// ===== 共通 =====
function showToast(msg) {
  const t = $('toast');
  t.textContent = msg;
  t.classList.remove('hidden');
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => t.classList.add('hidden'), 2200);
}

let currentTab = 'today';
const backTo = { chapter: 'text', quiz: 'quizmenu', exam: 'quizmenu' };

function showView(name) {
  document.querySelectorAll('.view').forEach((v) => v.classList.toggle('active', v.id === 'view-' + name));
  $('view-' + name).scrollTop = 0;
}

function switchTab(tab) {
  stopTimer();
  currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach((b) => b.classList.toggle('active', b.dataset.tab === tab));
  RENDER[tab]();
  showView(tab);
  if (pendingReload) location.reload(); // 問題を解いている間に見つけた更新を、解き終わってから反映する
}

function chapterTitle(id) {
  const c = CHAPTERS[id];
  return `第${c.no}章 ${c.title}`;
}

function todoHtml(todo) {
  return todo.split('\n').map((l) => `<li>${esc(l.replace(/^[①②③④⑤]/, ''))}</li>`).join('');
}

// 章ごとの問題の成績
function chapterStats(id) {
  const qs = CHAPTERS[id].quiz;
  const tried = qs.filter((q) => state.quiz[q.id]);
  const okNow = tried.filter((q) => state.quiz[q.id].last).length;
  return { total: qs.length, tried: tried.length, okNow };
}

// 「間違えた問題」: 一度でも間違えて、まだ3回続けて正解していない問題
function wrongIds() {
  return Object.keys(QUESTIONS).filter((id) => isWeak(state.quiz[id]));
}

// 問題の集まりのうち、直近で正解している割合(解いていない問題は×として数える)
function rateOf(ids) {
  if (!ids.length) return 0;
  const ok = ids.filter((id) => state.quiz[id] && state.quiz[id].last).length;
  return Math.round(ok / ids.length * 100);
}

// ===== 毎日の科目Aドリル =====
const DRILL_SIZE = 20;
// 章を最初に読む日目。その日を過ぎた章だけをドリルに出す
const CH_FIRST_N = {};
PLAN.forEach((p) => p.ch.forEach((id) => { if (!CH_FIRST_N[id]) CH_FIRST_N[id] = p.n; }));

function reachedA() {
  const k = Math.max(1, Math.min(LAST, todayN() || 1));
  const chs = Object.keys(CHAPTERS).filter((id) => CH_FIRST_N[id] && CH_FIRST_N[id] <= k);
  return A_IDS.filter((id) => chs.includes(QUESTIONS[id].ch));
}

// 間違えた問題 → まだ解いていない問題 → 最後に解いたのが古い問題、の順
function prioritized(pool, size) {
  const rank = (id) => {
    const r = state.quiz[id];
    if (isWeak(r)) return [0, r.at];
    if (!r) return [1, ''];
    return [2, r.at];
  };
  return shuffle(pool.slice())
    .sort((a, b) => { const x = rank(a); const y = rank(b); return x[0] - y[0] || String(x[1]).localeCompare(String(y[1])); })
    .slice(0, size);
}

// ===== 関門 =====
// 模擬試験の記録。set を渡すと過去問模試(そのセット)だけ、渡さなければアプリの模試だけ
function examResults(part, set) {
  return state.exams.filter((r) => r.part === part && (set ? r.set === set : !r.set));
}

// 関門の1項目の結果: { pass(null=未入力), text }
function gateResult(item) {
  if (item.type === 'rate') { const v = rateOf(item.ids); return { pass: v >= item.target, text: `今 ${v}%` }; }
  if (item.type === 'mock') {
    const rs = examResults(item.part, item.set);
    if (!rs.length) return { pass: null, text: 'まだ受けていない' };
    const v = rs[rs.length - 1].score;
    return { pass: v >= item.target, text: `直近 ${v}点` };
  }
  const v = state.gates[item.id];
  if (v === undefined || v === '') return { pass: null, text: '未入力' };
  return { pass: Number(v) >= item.target, text: `${v}点` };
}
const unit = (it) => (it.type === 'rate' ? '%' : '点');

// 過ぎた関門の日で、届いていない(または未入力の)もの
function failedGateNow() {
  const k = todayN();
  if (!k || k > LAST) return null;
  return PLAN.find((p) => p.gate && p.n < k && p.gate.some((it) => gateResult(it).pass !== true));
}

// ===== 今日 =====
function renderToday() {
  const t = todayStr();
  const k = todayN();
  let html = `<div class="hero"><div class="hero-date">${fmtDay(t, true)}</div>`;
  if (k) {
    const left = daysBetween(t, dayDate(LAST));
    html += `<div class="hero-count">${left > 0 ? `受験日まで <b>${left}</b> 日` : left === 0 ? '<b>今日</b> が受験日' : '7日間の計画は終わりました'}</div>`;
  }
  html += `</div>`;

  if (!k) {
    html += `<div class="card main">
      <div class="card-label">はじめに</div>
      <h2 class="theme">1日目をいつにしますか？</h2>
      <p class="muted">1日8時間 × 7日間の計画です。7日目にCBT試験（科目A 90分・科目B 100分）を受けます。1日目に試験の予約をするので、7日目に受けられる日を選んでください。CBT試験は2026年12月28日以降に休止の予定です。</p>
      <div class="btn-row">
        <button class="btn primary" data-set-start="${t}">今日から</button>
        <button class="btn ghost" data-set-start="${addDays(t, 1)}">明日から</button>
      </div>
      <label class="score-row" for="start-input">日付を選ぶ<input id="start-input" class="date-input" type="date" data-start-input="1"></label>
    </div>`;
    $('today-body').innerHTML = html;
    return;
  }

  if (dayDate(LAST) > CBT_LAST) {
    html += `<div class="card alert"><div class="card-label">受験日がCBTの休止期間に入っています</div>
      <p class="muted">7日目（${fmtDay(dayDate(LAST))}）は、IPAが発表しているCBT試験の休止（2026年12月28日以降）に入る見込みです。「記録」タブで1日目を早めてください。</p></div>`;
  }

  const failed = failedGateNow();
  if (failed) {
    const miss = failed.gate.filter((it) => gateResult(it).pass !== true);
    html += `<div class="card alert">
      <div class="card-label">関門に届いていません（${failed.n}日目）</div>
      <p class="alert-text">${miss.map((it) => `${esc(it.label)}：${esc(gateResult(it).text)}（目標 ${it.target}${unit(it)}）`).join('<br>')}</p>
      <p class="muted">${esc(failed.memo)}</p>
      <button class="btn ghost" data-quiz-mode="wrong">間違えた問題を解き直す（${wrongIds().length}問）</button>
    </div>`;
  }

  let day = null;
  let label = '今日やること';
  if (k < 1) { day = PLAN[0]; label = `${fmtDay(state.start)}から始まります`; }
  else if (k <= LAST) day = PLAN[k - 1];
  if (day) html += dayCard(day, label);
  else {
    html += `<div class="card main"><div class="card-label">7日間の計画は終わりました</div>
      <p class="muted">本番の点数がわかったら入れておきましょう。まだ受けていない場合は、科目Aドリル・間違えた問題・模擬試験を続けてください。</p>
      ${gateBox(PLAN[LAST - 1])}</div>`;
  }

  // 毎日の科目Aドリル
  if (k >= 1) {
    const n = state.drill[t] || 0;
    const fin = n >= DRILL_SIZE;
    html += `<div class="card ${fin ? 'soft' : 'main'}">
      <div class="card-label">毎日の科目Aドリル<span class="pill">四肢択一</span></div>
      <p class="muted">読んだ章の科目A問題から、間違えた問題を優先して${DRILL_SIZE}問出します。3回続けて正解するまで何度でも出ます。</p>
      <button class="btn ${fin ? 'done' : 'primary'}" data-quiz-mode="drill">${fin ? `✓ 今日の${DRILL_SIZE}問は解きました（もう一度解く）` : `科目Aドリルを始める（今日 ${n}/${DRILL_SIZE}問）`}</button>
    </div>`;
  }

  // 遅れている日
  const behind = PLAN.filter((p) => p.n < Math.min(k, LAST + 1) && !state.done[p.n]);
  if (behind.length) {
    html += `<div class="card warn">
      <div class="card-label">まだ終わっていない日が ${behind.length} 日あります</div>
      <p class="muted">いちばん古いのは ${behind[0].n}日目「${esc(behind[0].theme)}」です。今日の分と合わせて取り戻してください。</p>
      <button class="btn ghost" data-plan-detail="${behind[0].n}">${behind[0].n}日目を開く</button>
    </div>`;
  }

  const next = PLAN.find((p) => p.n > Math.max(k, 0));
  if (next && day) {
    html += `<div class="card soft"><div class="card-label">次の予定 ${next.n}日目・${fmtDay(dayDate(next.n))}</div>
      <div class="next-theme">${esc(next.theme)}</div></div>`;
  }
  $('today-body').innerHTML = html;
}

function bRange(ids) {
  const algo = ids.filter((id) => id.startsWith('b'));
  const sec = ids.filter((id) => id.startsWith('s'));
  return [algo.length ? `${algo[0]}〜${algo[algo.length - 1]}` : '', sec.length ? `${sec[0]}〜${sec[sec.length - 1]}` : ''].filter(Boolean).join('・');
}

function dayCard(day, label) {
  const done = !!state.done[day.n];
  let h = `<div class="card main ${done ? 'is-done' : ''}">
    <div class="card-label">${esc(label)}<span class="pill">${day.n}日目・${esc(day.phase)}</span></div>
    <h2 class="theme">${esc(day.theme)}</h2>
    <ol class="todo">${todoHtml(day.todo)}</ol>`;
  if (day.memo) h += `<p class="memo">${esc(day.memo)}</p>`;
  const links = [];
  day.ch.forEach((id) => {
    const s = chapterStats(id);
    links.push(`<div class="link-row">
      <button class="btn ghost" data-open-ch="${id}">📖 ${esc(chapterTitle(id))}</button>
      ${s.total ? `<button class="btn ghost small" data-quiz-ch="${id}">問題 ${s.okNow}/${s.total}</button>` : ''}
    </div>`);
  });
  if (day.b.length) {
    const ok = day.b.filter((id) => state.quiz[id] && state.quiz[id].last).length;
    links.push(`<button class="btn ghost" data-quiz-b="${day.n}">🧩 科目B 演習 ${esc(bRange(day.b))}（${ok}/${day.b.length}）</button>`);
  }
  (day.past || []).forEach((id) => {
    const ps = PAST_SETS[id];
    if (ps.mock) {
      const rs = examResults(ps.part, id);
      links.push(`<button class="btn ghost" data-open-exam="past:${id}">📝 過去問模試 ${PART_LABEL[ps.part]}（${ps.ids.length}問・${D.mock[ps.part].min}分）${rs.length ? `　直近 ${rs[rs.length - 1].score}点` : ''}</button>`);
    } else {
      const ok = ps.ids.filter((x) => state.quiz[x] && state.quiz[x].last).length;
      links.push(`<button class="btn ghost" data-quiz-past="${id}">📜 過去問 ${esc(ps.title)}（${ok}/${ps.ids.length}）</button>`);
    }
  });
  if (day.todo.includes('模擬試験')) {
    ['a', 'b'].forEach((p) => {
      const rs = examResults(p);
      links.push(`<button class="btn ghost" data-open-exam="${p}">📝 模擬試験 ${PART_LABEL[p]}（${D.mock[p].min}分）${rs.length ? `　直近 ${rs[rs.length - 1].score}点` : ''}</button>`);
    });
  }
  if (links.length) h += `<div class="links">${links.join('')}</div>`;
  if (day.gate) h += gateBox(day);
  h += `<button class="btn ${done ? 'done' : 'primary'}" data-toggle-day="${day.n}">${done ? '✓ 完了しました（取り消す）' : 'この日の分を完了にする'}</button>`;
  return h + `</div>`;
}

// 関門の判定と、点数の入力欄
function gateBox(day) {
  let h = `<div class="gate">`;
  day.gate.forEach((it) => {
    const r = gateResult(it);
    const badge = r.pass === null ? '' : r.pass ? '<span class="badge ok">合格ライン</span>' : '<span class="badge ng">届いていない</span>';
    const goal = `目標 ${it.target}${unit(it)}以上`;
    if (it.type === 'score') {
      h += `<label class="gate-item" for="gate-${it.id}"><div class="gate-head">${esc(it.label)}${badge}</div>
        <div class="gate-row"><span class="gate-sub">${esc(goal)}</span>
        <span><input id="gate-${it.id}" class="score-input" type="number" min="0" max="1000" inputmode="numeric"
          value="${esc(state.gates[it.id] ?? '')}" data-gate-id="${it.id}"> 点</span></div></label>`;
    } else {
      const how = it.type === 'rate' ? `対象${it.ids.length}問・未回答は×` : '模擬試験の結果から自動で記録';
      h += `<div class="gate-item"><div class="gate-head">${esc(it.label)}${badge}</div>
        <div class="gate-sub">${esc(goal)}・${esc(r.text)}（${esc(how)}）</div></div>`;
    }
  });
  return h + `</div>`;
}

// ===== テキスト =====
function renderText() {
  let html = `<ul class="list"><li class="list-row" data-open-intro="1">
      <span class="row-no">★</span>
      <span class="row-main"><span class="row-title">このテキストの使い方・試験の形式</span></span></li></ul>`;
  html += `<ul class="list">` + SUBJ.chapters.map((c) => {
    const st = chapterStats(c.id);
    const read = state.read[c.id];
    return `<li class="list-row" data-open-ch="${c.id}">
      <span class="row-no">${c.no}</span>
      <span class="row-main"><span class="row-title">${esc(c.title)}</span>
        <span class="row-sub">${CH_FIRST_N[c.id] ? CH_FIRST_N[c.id] + '日目・' : ''}${read ? '読んだ' : '未読'}${st.total ? `・問題 ${st.okNow}/${st.total}` : ''}</span></span>
      <span class="row-mark">${read ? '✓' : ''}</span>
    </li>`;
  }).join('') + `</ul>`;
  $('text-body').innerHTML = html;
}

function openIntro() {
  $('chapter-crumb').textContent = 'テキスト';
  $('chapter-body').innerHTML = `<h1 class="ch-title">このテキストの使い方</h1>${SUBJ.intro}`;
  backTo.chapter = currentTab;
  showView('chapter');
}

function openChapter(id) {
  const c = CHAPTERS[id];
  $('chapter-crumb').textContent = '基本情報技術者';
  const read = !!state.read[id];
  const ids = SUBJ.chapters.map((x) => x.id);
  const i = ids.indexOf(id);
  const na = c.quiz.filter((q) => q.t === 'a').length;
  const nb = c.quiz.length - na;
  const counts = [na ? `科目A ${na}問` : '', nb ? `科目B ${nb}問` : ''].filter(Boolean).join('・');
  $('chapter-body').innerHTML = `<h1 class="ch-title">第${c.no}章<br>${esc(c.title)}</h1>
    ${c.html}
    <div class="ch-actions">
      ${c.quiz.length ? `<button class="btn primary" data-quiz-ch="${id}">この章の問題を解く（${counts}）</button>` : ''}
      <button class="btn ${read ? 'done' : 'ghost'}" data-toggle-read="${id}">${read ? '✓ 読みました（取り消す）' : '読み終えた'}</button>
      <div class="pager">
        ${i > 0 ? `<button class="btn ghost small" data-open-ch="${ids[i - 1]}">‹ 第${c.no - 1}章</button>` : '<span></span>'}
        ${i < ids.length - 1 ? `<button class="btn ghost small" data-open-ch="${ids[i + 1]}">第${CHAPTERS[ids[i + 1]].no}章 ›</button>` : '<span></span>'}
      </div>
    </div>`;
  if (!$('view-chapter').classList.contains('active')) backTo.chapter = currentTab;
  showView('chapter');
}

// ===== 問題メニュー =====
function renderQuizMenu() {
  const wrong = wrongIds();
  const all = Object.keys(QUESTIONS);
  const unanswered = all.filter((id) => !state.quiz[id]).length;
  let html = `<div class="quick">
    <button class="quick-btn" data-quiz-mode="drill"><b>科目Aドリル</b><span>読んだ章から${DRILL_SIZE}問</span></button>
    <button class="quick-btn" data-quiz-mode="bmix"><b>科目Bトレース</b><span>本試験レベルのアルゴリズムを5問（間違えた問題を優先）</span></button>
    <button class="quick-btn" data-quiz-mode="wrong" ${wrong.length ? '' : 'disabled'}><b>間違えた問題</b><span>${wrong.length}問（3回続けて正解で外れる）</span></button>
    <button class="quick-btn" data-quiz-mode="new" ${unanswered ? '' : 'disabled'}><b>まだ解いていない問題</b><span>${unanswered}問</span></button>
  </div>
  <p class="muted">科目Aの正答率 ${rateOf(A_IDS)}%（全${A_IDS.length}問）・科目Bの正答率 ${rateOf(B_IDS)}%（全${B_IDS.length}問）。直近で正解している割合で、まだ解いていない問題は×として数えます。</p>`;

  html += `<h2 class="section-title">本番形式の模擬試験<span class="section-sub">1000点換算・600点で合格</span></h2><ul class="list">` + ['a', 'b'].map((p) => {
    const rs = examResults(p);
    const m = D.mock[p];
    const sub = p === 'a' ? `60問・${m.min}分（テクノロジ${m.n.tech}・マネジメント${m.n.mgmt}・ストラテジ${m.n.strat}）` : `20問・${m.min}分（アルゴリズム${m.n.algo}・セキュリティ${m.n.sec}）`;
    return `<li class="list-row" data-open-exam="${p}">
      <span class="row-no">${p.toUpperCase()}</span>
      <span class="row-main"><span class="row-title">模擬試験 ${PART_LABEL[p]}</span>
        <span class="row-sub">${sub}${rs.length ? `・最高 ${Math.max(...rs.map((r) => r.score))}点` : ''}</span></span>
      ${examChip(p)}</li>`;
  }).join('') + `</ul>`;

  html += `<h2 class="section-title">科目B<span class="section-sub">1問5〜10分・トレース表を書いて解く</span></h2><ul class="list">` +
    Object.entries(B_KIND_LABEL).map(([k, label]) => {
      const ids = B_IDS.filter((id) => QUESTIONS[id].kind === k);
      return `<li class="list-row" data-quiz-kind="${k}"><span class="row-no">${k.startsWith('algo') ? '🧩' : '🔒'}</span><span class="row-main"><span class="row-title">${label}</span>
        <span class="row-sub">全${ids.length}問・正答率 ${rateOf(ids)}%${k.endsWith('0') ? '・1日目の練習用（模試には出ない）' : '・模試に出る'}</span></span></li>`;
    }).join('') + `</ul>`;

  html += `<h2 class="section-title">過去問（IPA）<span class="section-sub">原文の画像・出典と解説つき</span></h2><ul class="list">` + D.pastSets.map((ps) => {
    const ok = ps.ids.filter((id) => state.quiz[id] && state.quiz[id].last).length;
    const tried = ps.ids.filter((id) => state.quiz[id]).length;
    let row = `<li class="list-row" data-quiz-past="${ps.id}"><span class="row-no">${ps.part.toUpperCase()}</span>
      <span class="row-main"><span class="row-title">${esc(ps.title)}</span>
        <span class="row-sub">${ps.ids.length}問・1問ずつ解いて解説を読む</span></span>
      <span class="score-chip ${!tried ? '' : ok === ps.ids.length ? 'good' : 'bad'}">${tried ? `${ok}/${ps.ids.length}` : '未'}</span></li>`;
    if (ps.mock) {
      row += `<li class="list-row" data-open-exam="past:${ps.id}"><span class="row-no">📝</span>
        <span class="row-main"><span class="row-title">過去問模試 ${PART_LABEL[ps.part]}（本番と同じ ${D.mock[ps.part].min}分）</span>
          <span class="row-sub">${esc(ps.title)}を時間を計って解く・6日目の関門</span></span>${examChip(ps.part, ps.id)}</li>`;
    }
    return row;
  }).join('') + `</ul>`;

  html += `<h2 class="section-title">章ごと</h2><ul class="list">` + SUBJ.chapters.filter((c) => c.quiz.length).map((c) => {
    const st = chapterStats(c.id);
    const cls = st.tried === 0 ? '' : st.okNow === st.total ? 'good' : 'bad';
    return `<li class="list-row" data-quiz-ch="${c.id}">
      <span class="row-no">${c.no}</span>
      <span class="row-main"><span class="row-title">${esc(c.title)}</span></span>
      <span class="score-chip ${cls}">${st.tried ? `${st.okNow}/${st.total}` : '未'}</span>
    </li>`;
  }).join('') + `</ul>`;
  $('quizmenu-body').innerHTML = html;
}

// ===== 問題を解く =====
let quiz = null; // { ids, i, results, title, mode, answered }

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

function startQuiz(ids, title, mode) {
  if (!ids.length) { showToast('出題できる問題がありません'); return; }
  quiz = { ids, i: 0, results: [], title, answered: false, mode: mode || '' };
  backTo.quiz = currentTab;
  showView('quiz');
  renderQuestion();
}

function startQuizMode(mode) {
  const all = Object.keys(QUESTIONS);
  if (mode === 'drill') startQuiz(prioritized(reachedA(), DRILL_SIZE), '科目Aドリル', 'drill');
  else if (mode === 'bmix') startQuiz(prioritized(B_IDS.filter((id) => QUESTIONS[id].kind === 'algo'), 5), '科目Bトレース');
  else if (mode === 'wrong') startQuiz(shuffle(wrongIds()), '間違えた問題');
  else if (mode === 'new') startQuiz(all.filter((id) => !state.quiz[id]).slice(0, 20), 'まだ解いていない問題');
}

// 問題文(科目Bはリード文・プログラム・設問)
function questionHtml(q, label) {
  if (q.t === 'past') {
    return `<div class="q-chapter">${esc(label)}</div>
      <div class="past-imgs">${q.imgs.map((im) => `<img src="${im.src}" width="${im.w}" height="${im.h}" loading="lazy" alt="${esc(q.src)}">`).join('')}</div>
      <p class="past-src">${esc(q.src)}（画像をタップすると拡大・縮小）</p>`;
  }
  if (q.t === 'a') return `<div class="q-chapter">${esc(label)}</div><p class="q-text">${esc(q.q)}</p>`;
  return `<div class="q-chapter">${esc(label)}・${esc(q.title)}</div>
    <p class="q-text b">${esc(q.q)}</p>
    ${q.code ? `<pre class="code">${esc(q.code)}</pre>` : ''}
    <p class="q-after"><b>${esc(q.ask)}</b></p>`;
}

function choicesHtml(q, attr) {
  if (q.t === 'past') {   // 選択肢の文は画像の中にあるので、記号だけのボタンにする
    return `<div class="choices past-choices">${KANA.slice(0, q.n).map((k, i) => `<button class="choice" ${attr}="${i}" aria-label="${k}"><span class="ck">${k}</span></button>`).join('')}</div>`;
  }
  return `<div class="choices">${q.opts.map((o, i) => `<button class="choice ${q.codeOpts ? 'code' : ''}" ${attr}="${i}">
      <span class="ck">${KANA[i]}</span><span class="ct">${esc(o)}</span></button>`).join('')}</div>`;
}

function renderQuestion() {
  const id = quiz.ids[quiz.i];
  const q = QUESTIONS[id];
  $('quiz-progress').textContent = `${quiz.title}　${quiz.i + 1} / ${quiz.ids.length}`;
  quiz.answered = false;
  const label = q.t === 'past' ? `過去問・${PART_LABEL[q.part]}` : q.t === 'a' ? `${chapterTitle(q.ch)}・科目A` : `科目B ${q.kind.endsWith('0') ? '基礎' : '本試験レベル'} ${q.id}`;
  $('quiz-body').innerHTML = questionHtml(q, label) + choicesHtml(q, 'data-answer') + `<div id="q-result"></div>`;
}

function markChoices(root, q, picked) {
  root.querySelectorAll('.choice').forEach((b, i) => {
    b.disabled = true;
    if (i === q.ans) b.classList.add('is-answer');
    else if (i === picked) b.classList.add('is-wrong');
  });
  const box = root.querySelector('.choices');
  if (box) box.classList.add('done');
}

function submitAnswer(choice) {
  if (quiz.answered) return;
  const id = quiz.ids[quiz.i];
  const q = QUESTIONS[id];
  const ok = choice === q.ans;
  quiz.answered = true;
  recordAnswer(id, ok);
  quiz.results.push(ok);
  if (quiz.mode === 'drill') {
    const t = todayStr();
    state.drill[t] = (state.drill[t] || 0) + 1;
    saveState();
  }
  markChoices($('quiz-body'), q, choice);
  const last = quiz.i === quiz.ids.length - 1;
  $('q-result').innerHTML = `<div class="result ${ok ? 'ok' : 'ng'}">
      <div class="result-head">${ok ? '正解' : '不正解'}　答えは ${KANA[q.ans]}</div>
      ${expHtml(q.exp)}
      ${ok ? `<button class="guess-btn" id="btn-guess">理由を説明できない（勘で当たった）→ ×にする</button>` : ''}
    </div>
    <div class="q-actions">
      <button class="btn ghost small" data-open-ch="${q.ch}">テキストで確認</button>
      <button class="btn primary" id="btn-next-q">${last ? '結果を見る' : '次の問題'}</button>
    </div>`;
  $('q-result').scrollIntoView({ block: 'nearest' });
}

// 解説: 改行をそのまま表示し、【ポイント】などの見出しを太字にする
function expHtml(text) {
  return `<div class="exp">${esc(text).replace(/【([^】]+)】/g, '<b class="exp-h">【$1】</b>')}</div>`;
}

function shortQ(q) {
  if (q.t === 'past') return q.src.replace('出典：', '');
  return q.t === 'a' ? q.q.split('\n')[0] : `${q.id} ${q.title}`;
}

function nextQuestion() {
  if (quiz.i < quiz.ids.length - 1) {
    quiz.i += 1;
    renderQuestion();
    $('view-quiz').scrollTop = 0;
    return;
  }
  const ok = quiz.results.filter(Boolean).length;
  const n = quiz.results.length;
  const wrongHere = quiz.ids.filter((id, k) => !quiz.results[k]);
  $('quiz-progress').textContent = quiz.title;
  $('quiz-body').innerHTML = `<div class="finish">
      <div class="finish-score"><b>${ok}</b> / ${n}</div>
      <p class="muted">${ok === n ? '全問正解です。' : `間違えた ${n - ok} 問は、3回続けて正解するまで「間違えた問題」に残ります。`}</p>
    </div>
    ${wrongHere.length ? `<h2 class="section-title">間違えた問題</h2><ul class="list">` + wrongHere.map((id) => {
      const q = QUESTIONS[id];
      return `<li class="list-row static"><span class="row-main"><span class="row-title">${esc(shortQ(q))}</span>
        <span class="row-sub">答え ${KANA[q.ans]}：${esc(q.opts[q.ans])}</span></span></li>`;
    }).join('') + `</ul>` : ''}
    <div class="q-actions">
      ${wrongHere.length ? `<button class="btn ghost" id="btn-retry-wrong">間違えた問題をもう一度</button>` : ''}
      <button class="btn primary" id="btn-finish-quiz">終わる</button>
    </div>`;
  quiz.retry = wrongHere;
}

// ===== タイマー =====
let timer = null;
function startTimer(text) {
  stopTimer();
  const tick = () => { const el = $(text.el); if (el) el.textContent = text(); };
  tick();
  timer = setInterval(tick, 1000);
}
function stopTimer() { if (timer) { clearInterval(timer); timer = null; } }
function mmss(ms) { const s = Math.floor(ms / 1000); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; }

// ===== 本番形式の模擬試験(科目A 60問90分 / 科目B 20問100分。1000点換算) =====
let exam = null; // { part, ids, picked: {i: 選択肢}, startAt, done, i }

function pickFrom(ids, n) {
  return prioritized(ids, ids.length).slice(0, n);
}

// 科目Aは分野ごとの本番の出題数、科目Bはアルゴリズム16問のあとにセキュリティ4問
function pickExam(part) {
  const m = D.mock[part];
  if (part === 'a') {
    const of = (nos) => A_IDS.filter((id) => nos.includes(CHAPTERS[QUESTIONS[id].ch].no));
    const ids = [...pickFrom(of(m.tech), m.n.tech), ...pickFrom(of(m.mgmt), m.n.mgmt), ...pickFrom(of(m.strat), m.n.strat)];
    return ids; // 本番と同じく テクノロジ → マネジメント → ストラテジ の順
  }
  const of = (k) => B_IDS.filter((id) => QUESTIONS[id].kind === k);
  return [...shuffle(pickFrom(of('algo'), m.n.algo)), ...shuffle(pickFrom(of('sec'), m.n.sec))];
}

function examChip(part, set) {
  const rs = examResults(part, set);
  if (!rs.length) return '<span class="score-chip">未</span>';
  const last = rs[rs.length - 1].score;
  return `<span class="score-chip ${last >= 600 ? 'good' : 'bad'}">${last}点</span>`;
}

// key は 'a'・'b'（アプリの模試）か 'past:セットid'（過去問模試）
function examTitle() {
  return exam.set ? `過去問模試 ${PART_LABEL[exam.part]}` : `模擬試験 ${PART_LABEL[exam.part]}`;
}

function startExam(key) {
  const set = key.startsWith('past:') ? key.slice(5) : null;
  const part = set ? PAST_SETS[set].part : key;
  exam = { key, part, set, ids: set ? PAST_SETS[set].ids.slice() : pickExam(part), picked: {}, startAt: Date.now(), done: false, i: 0 };
  if (!$('view-exam').classList.contains('active')) backTo.exam = currentTab;
  renderExam();
  $('btn-end-exam').classList.remove('hidden');
  showView('exam');
  const ms = D.mock[part].min * 60 * 1000;
  startTimer(Object.assign(() => {
    const left = ms - (Date.now() - exam.startAt);
    if (left <= 0 && !exam.done) { showToast('時間になりました。採点します'); setTimeout(gradeExam, 0); }
    return `${examTitle()}　残り ${mmss(Math.max(0, left))}`;
  }, { el: 'exam-timer' }));
}

function renderExam() {
  const nav = `<div class="exam-nav">${exam.ids.map((id, i) => `<button class="exam-num ${i === exam.i ? 'on' : ''}" data-exam-q="${i}">${i + 1}</button>`).join('')}</div>`;
  const qs = exam.ids.map((id, i) => {
    const q = QUESTIONS[id];
    const label = q.t === 'a' || q.t === 'past' ? `問${i + 1}` : `問${i + 1}（${q.kind === 'algo' ? 'アルゴリズム' : 'セキュリティ'}）`;
    return `<div class="exam-q ${i === exam.i ? '' : 'hidden'}" data-i="${i}">
      ${questionHtml(q, label)}${choicesHtml(q, 'data-exam-pick')}<div class="exam-q-ans"></div>
      <div class="pager"><button class="btn ghost small" data-exam-q="${i - 1}" ${i === 0 ? 'disabled' : ''}>‹ 前の問題</button>
        <button class="btn ghost small" data-exam-q="${i + 1}" ${i === exam.ids.length - 1 ? 'disabled' : ''}>次の問題 ›</button></div></div>`;
  }).join('');
  $('exam-body').innerHTML = `<div id="exam-result"></div>${nav}${qs}
    <button class="btn primary" id="btn-end-exam2">解答を終了して採点する</button>`;
}

function examQ(i) {
  exam.i = Math.max(0, Math.min(exam.ids.length - 1, i));
  document.querySelectorAll('.exam-q').forEach((el) => el.classList.toggle('hidden', Number(el.dataset.i) !== exam.i));
  document.querySelectorAll('.exam-num').forEach((b) => b.classList.toggle('on', Number(b.dataset.examQ) === exam.i));
  $('view-exam').scrollTop = 0;
}

function examPick(btn) {
  if (exam.done) return;
  const box = btn.closest('.exam-q');
  const i = Number(box.dataset.i);
  exam.picked[i] = Number(btn.dataset.examPick);
  box.querySelectorAll('.choice').forEach((b) => b.classList.toggle('picked', b === btn));
  document.querySelector(`.exam-num[data-exam-q="${i}"]`).classList.add('filled');
}

function gradeExam() {
  if (!exam || exam.done) return;
  exam.done = true;
  stopTimer();
  const m = D.mock[exam.part];
  const sec = Math.round(Math.min(m.min * 60 * 1000, Date.now() - exam.startAt) / 1000);
  const root = $('exam-body');
  let ok = 0;
  const byArea = {};
  exam.ids.forEach((id, i) => {
    const q = QUESTIONS[id];
    const p = exam.picked[i];
    const right = p === q.ans;
    if (right) ok += 1;
    if (p !== undefined) recordAnswer(id, right);
    const area = q.t === 'b' || (q.t === 'past' && q.part === 'b') ? (q.kind === 'algo' ? 'アルゴリズム' : 'セキュリティ') : areaOf(q);
    byArea[area] = byArea[area] || [0, 0];
    byArea[area][0] += right ? 1 : 0;
    byArea[area][1] += 1;
    const box = root.querySelector(`.exam-q[data-i="${i}"]`);
    markChoices(box, q, p);
    box.querySelector('.exam-q-ans').innerHTML = `<div class="result ${right ? 'ok' : 'ng'}"><div class="result-head">${right ? '正解' : p === undefined ? '未解答' : '不正解'}　答えは ${KANA[q.ans]}</div>
      ${expHtml(q.exp)}</div>`;
    root.querySelector(`.exam-num[data-exam-q="${i}"]`).classList.add(right ? 'ok' : 'ng');
  });
  const n = exam.ids.length;
  const score = Math.round(ok / n * 1000);
  state.exams.push(Object.assign({ at: new Date().toISOString(), part: exam.part, score, ok, n, sec }, exam.set ? { set: exam.set } : {}));
  saveState();
  if ($('btn-end-exam2')) $('btn-end-exam2').remove();
  $('exam-timer').textContent = `${examTitle()}　採点済み`;
  $('btn-end-exam').classList.add('hidden');
  $('exam-result').innerHTML = `<div class="finish">
      <div class="finish-score"><b>${score}</b> / 1000点</div>
      <p class="pass ${score >= 600 ? 'ok' : 'ng'}">${score >= 600 ? '合格ライン（600点）に届いています' : `合格ラインまであと ${600 - score} 点`}</p>
      <p class="muted">${ok} / ${n} 問正解・かかった時間 ${mmss(sec * 1000)}（${m.min}分）</p>
    </div>
    <div class="table-wrap"><table class="tb"><thead><tr><th>分野</th><th>正解</th><th>正答率</th></tr></thead><tbody>
      ${Object.entries(byArea).map(([a, [x, y]]) => `<tr><td>${esc(a)}</td><td class="num">${x} / ${y}</td><td class="num">${Math.round(x / y * 100)}%</td></tr>`).join('')}
    </tbody></table></div>
    <p class="muted">本番はIRT方式なので点数はこのとおりにはなりません。${exam.set ? 'IPAの過去問なので、初めて解いたときの点数は本番の実力に近い目安になります（2回目以降は高く出ます）。' : 'また、この模試は練習した問題から出るので本番より高く出ます。'}下の番号を押すと、答えと解説を確認できます。間違えた問題は「間違えた問題」に入りました。</p>
    <div class="q-actions"><button class="btn ghost" data-open-exam="${exam.key}">もう一度解く</button>
      <button class="btn primary" id="btn-finish-exam">終わる</button></div>`;
  $('view-exam').scrollTop = 0;
}

function areaOf(q) {
  const no = CHAPTERS[q.ch].no;
  if (D.mock.a.mgmt.includes(no)) return 'マネジメント';
  if (D.mock.a.strat.includes(no)) return 'ストラテジ';
  return 'テクノロジ';
}

// ===== 計画 =====
function renderPlan() {
  const k = todayN();
  let html = '';
  if (!state.start) html += `<div class="card soft plan-note"><p class="muted">「今日」の画面で1日目の日付を決めると、日付が入ります。</p></div>`;
  PLAN.forEach((p) => {
    const d = dayDate(p.n);
    const done = !!state.done[p.n];
    const late = !done && k && p.n < k;
    html += `<div class="plan-row ${k === p.n ? 'today' : ''} ${done ? 'done' : ''} ${late ? 'late' : ''}">
      <div class="plan-date"><b>${p.n}</b><span>日目</span></div>
      <div class="plan-main" data-plan-detail="${p.n}">
        <div class="plan-theme">${esc(p.theme)}</div>
        <div class="plan-sub">${d ? fmtDay(d) + '・' : ''}${p.gate ? '<b class="gate-mark">関門</b>・' : ''}${esc(p.phase)}</div>
      </div>
      <button class="plan-check ${done ? 'on' : ''}" data-toggle-day="${p.n}" aria-label="${done ? '完了を取り消す' : '完了にする'}">${done ? '✓' : ''}</button>
    </div>`;
  });
  $('plan-body').innerHTML = html;
}

function showPlanDetail(n) {
  const p = PLAN[n - 1];
  if (!$('view-chapter').classList.contains('active')) backTo.chapter = currentTab;
  $('chapter-crumb').textContent = '計画';
  const d = dayDate(n);
  $('chapter-body').innerHTML = `<h1 class="ch-title">${n}日目${d ? `<br><span class="ch-sub">${fmtDay(d, true)}</span>` : ''}</h1>` + dayCard(p, 'この日にやること');
  showView('chapter');
}

// ===== 記録 =====
function renderRecord() {
  const k = todayN();
  const doneN = PLAN.filter((p) => state.done[p.n]).length;
  const readN = Object.keys(state.read).filter((id) => CHAPTERS[id]).length;
  const nCh = SUBJ.chapters.length;

  let html = `<div class="stats">
    <div class="stat"><b>${doneN}/${LAST}</b><span>完了した日${k && k >= 1 ? `<br>（今日は${Math.min(k, LAST)}日目）` : ''}</span></div>
    <div class="stat"><b>${readN}/${nCh}</b><span>読んだ章</span></div>
    <div class="stat"><b>${rateOf(A_IDS)}%</b><span>科目Aの正答率<br>（全${A_IDS.length}問・未回答は×）</span></div>
    <div class="stat"><b>${rateOf(B_IDS)}%</b><span>科目Bの正答率<br>（全${B_IDS.length}問・未回答は×）</span></div>
    <div class="stat"><b>${Object.keys(state.quiz).filter((id) => QUESTIONS[id]).length}</b><span>解いたことのある問題<br>（全${Object.keys(QUESTIONS).length}問）</span></div>
    <div class="stat"><b>${wrongIds().length}</b><span>間違えた問題<br>（3回続けて正解で外れる）</span></div>
  </div>`;

  html += `<h2 class="section-title">関門</h2><ul class="list">` + PLAN.filter((p) => p.gate).map((p) => {
    const rs = p.gate.map((it) => gateResult(it));
    let chip = '<span class="score-chip">これから</span>';
    if (rs.some((r) => r.pass === null)) chip = (k && p.n <= k) ? '<span class="score-chip bad">未入力</span>' : chip;
    else if (rs.every((r) => r.pass)) chip = '<span class="score-chip good">通過</span>';
    else if (k && p.n <= k) chip = '<span class="score-chip bad">未達</span>';
    return `<li class="list-row" data-plan-detail="${p.n}">
      <span class="row-main"><span class="row-title">${p.n}日目：${p.gate.map((it) => esc(it.label) + ' ' + it.target + unit(it)).join('／')}</span>
        <span class="row-sub">${rs.map((r) => esc(r.text)).join('／')}</span></span>
      ${chip}</li>`;
  }).join('') + `</ul>`;

  html += `<h2 class="section-title">本番形式の模擬試験（1000点換算）</h2>`;
  html += state.exams.length ? `<ul class="list">` + state.exams.slice(-10).reverse().map((r) => {
    const d = new Date(r.at);
    return `<li class="list-row static"><span class="row-main"><span class="row-title">${r.set ? '過去問模試 ' + PART_LABEL[r.part] : '模擬試験 ' + PART_LABEL[r.part]}・${fmtDay(ymd(d))} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}</span>
      <span class="row-sub">${r.ok} / ${r.n} 問正解・${mmss(r.sec * 1000)}</span></span>
      <span class="score-chip ${r.score >= 600 ? 'good' : 'bad'}">${r.score}点</span></li>`;
  }).join('') + `</ul>` : `<div class="card soft"><p class="muted">「問題」タブの「本番形式の模擬試験」を解くと、ここに並びます。6日目の関門にも自動で記録されます。</p></div>`;

  html += `<p class="foot">バージョン ${APP_VERSION}${state.start ? `・受験日 ${fmtDay(dayDate(LAST), true)}（予定）` : ''}</p>`;
  $('record-body').innerHTML = html;
}

// ===== 設定 =====
let updateStatus = ''; // 最後に「最新バージョンか確認」した結果
function renderSettings() {
  $('settings-body').innerHTML = `
    <h2 class="section-title">アプリ情報</h2>
    <div class="card soft">
      <div class="score-row">今のバージョン<b class="ver">${APP_VERSION}</b></div>
      <button class="btn primary" id="btn-check-update">最新バージョンか確認する</button>
      <p class="muted" id="update-status">${esc(updateStatus || 'アプリを開いたときと、画面に戻ったときにも自動で確認しています。')}</p>
    </div>

    <h2 class="section-title">1日目の日付</h2>
    <div class="card soft">
      <label class="score-row" for="start-change">1日目<input id="start-change" class="date-input" type="date" value="${esc(state.start || '')}" data-start-input="1"></label>
      <p class="muted">${state.start ? `受験日（7日目）は${fmtDay(dayDate(LAST), true)}です。` : ''}受験日を変えたときは、ここで1日目をずらしてください。完了の記録は「何日目」で残ります。CBT試験は2026年12月28日以降に休止の予定です。</p>
    </div>

    <h2 class="section-title">バックアップ</h2>
    <div class="card soft">
      <p class="muted">記録はこの端末の中だけに保存されます。機種変更やブラウザのデータ削除に備えて、ときどきファイルに書き出してください。</p>
      <div class="btn-row">
        <button class="btn ghost" id="btn-export">書き出す</button>
        <button class="btn ghost" id="btn-import">読み込む</button>
      </div>
    </div>`;
}

function openSettings() {
  backTo.settings = currentTab;
  renderSettings();
  showView('settings');
}

// 確認の結果を、設定画面の表示とトーストの両方に出す
function reportUpdate(msg, manual) {
  const t = new Date();
  updateStatus = `${msg}（${t.getHours()}:${String(t.getMinutes()).padStart(2, '0')} に確認）`;
  if ($('update-status')) $('update-status').textContent = updateStatus;
  if (manual) showToast(msg);
}

const RENDER = { today: renderToday, text: renderText, quizmenu: renderQuizMenu, plan: renderPlan, record: renderRecord };

// ===== 操作 =====
function inPlanDetail() {
  return $('view-chapter').classList.contains('active') && $('chapter-crumb').textContent === '計画';
}

document.addEventListener('click', (e) => {
  const zoom = e.target.closest('.past-imgs');   // 過去問の画像はタップで拡大・縮小
  if (zoom) { zoom.classList.toggle('zoom'); return; }
  const el = e.target.closest('button, [data-open-ch], [data-quiz-ch], [data-quiz-kind], [data-quiz-past], [data-plan-detail], [data-open-intro], [data-open-exam]');
  if (!el || el.disabled) return;
  const ds = el.dataset;
  if (el.classList.contains('tab-btn')) return switchTab(ds.tab);
  if (ds.setStart) {
    state.start = ds.setStart;
    saveState();
    showToast(`1日目は${fmtDay(ds.setStart)}、受験日は${fmtDay(addDays(ds.setStart, LAST - 1))}です`);
    return renderToday();
  }
  if (ds.toggleDay) {
    const n = Number(ds.toggleDay);
    if (state.done[n]) delete state.done[n];
    else { state.done[n] = new Date().toISOString(); showToast('お疲れさまでした'); }
    saveState();
    if (inPlanDetail()) showPlanDetail(n);
    else RENDER[currentTab]();
    return;
  }
  if (ds.toggleRead) {
    if (state.read[ds.toggleRead]) delete state.read[ds.toggleRead];
    else state.read[ds.toggleRead] = new Date().toISOString();
    saveState();
    return openChapter(ds.toggleRead);
  }
  if (ds.openIntro) return openIntro();
  if (ds.openCh) return openChapter(ds.openCh);
  if (ds.quizCh) return startQuiz(CHAPTERS[ds.quizCh].quiz.map((q) => q.id), `第${CHAPTERS[ds.quizCh].no}章`);
  if (ds.quizB) return startQuiz(PLAN[Number(ds.quizB) - 1].b.slice(), `科目B ${ds.quizB}日目の演習`);
  if (ds.quizKind) return startQuiz(B_IDS.filter((id) => QUESTIONS[id].kind === ds.quizKind), '科目B ' + B_KIND_LABEL[ds.quizKind]);
  if (ds.quizPast) return startQuiz(PAST_SETS[ds.quizPast].ids.slice(), '過去問 ' + PAST_SETS[ds.quizPast].title);
  if (ds.quizMode) return startQuizMode(ds.quizMode);
  if (ds.openExam) {
    if (exam && !exam.done && $('view-exam').classList.contains('active')) return;
    return startExam(ds.openExam);
  }
  if (ds.examPick !== undefined) return examPick(el);
  if (ds.examQ !== undefined) return examQ(Number(ds.examQ));
  if (ds.answer !== undefined) return submitAnswer(Number(ds.answer));
  if (ds.planDetail) return showPlanDetail(Number(ds.planDetail));
  switch (el.id) {
    case 'btn-next-q': return nextQuestion();
    case 'btn-guess': {
      markGuess(quiz.ids[quiz.i]);
      quiz.results[quiz.i] = false;
      const box = el.closest('.result');
      box.classList.replace('ok', 'ng');
      box.querySelector('.result-head').textContent = '勘で当たった → 間違えた問題に入れました';
      el.remove();
      return;
    }
    case 'btn-retry-wrong': return startQuiz(shuffle(quiz.retry.slice()), '間違えた問題');
    case 'btn-finish-quiz':
    case 'btn-quit-quiz': return switchTab(backTo.quiz);
    case 'btn-back-chapter': return switchTab(backTo.chapter);
    case 'btn-settings': return openSettings();
    case 'btn-back-settings': return switchTab(backTo.settings || 'today');
    case 'btn-end-exam':
    case 'btn-end-exam2': {
      if (exam.done) return;
      const left = exam.ids.length - Object.keys(exam.picked).length;
      if (confirm(left ? `未解答が ${left} 問あります。解答を終了して採点しますか？` : '解答を終了して採点しますか？')) gradeExam();
      return;
    }
    case 'btn-quit-exam':
      if (!exam.done && !confirm('試験を中断しますか？ 選んだ解答は消えます')) return;
      return switchTab(backTo.exam);
    case 'btn-finish-exam': return switchTab(backTo.exam);
    case 'btn-export': return doExport();
    case 'btn-import': return $('backup-file').click();
    case 'btn-check-update': return checkForUpdate(true);
  }
});

// 問題を解いている間は、キーボードの 1〜4（ア〜エ）で答え、Enter で次へ進める
document.addEventListener('keydown', (e) => {
  if (!quiz || !$('view-quiz').classList.contains('active') || e.target.matches('input')) return;
  if (!quiz.answered && /^[1-8]$/.test(e.key)) {
    const q = QUESTIONS[quiz.ids[quiz.i]];
    const n = Number(e.key) - 1;
    if (n < q.opts.length) submitAnswer(n);
  } else if (quiz.answered && e.key === 'Enter' && $('btn-next-q')) {
    e.preventDefault();
    nextQuestion();
  }
});

document.addEventListener('change', (e) => {
  const { gateId, startInput } = e.target.dataset;
  if (startInput) {
    if (!e.target.value) return;
    state.start = e.target.value;
    saveState();
    showToast(`1日目は${fmtDay(state.start)}、受験日は${fmtDay(dayDate(LAST))}です`);
    if ($('view-settings').classList.contains('active')) return renderSettings();
    return RENDER[currentTab]();
  }
  if (!gateId) return;
  const v = e.target.value.trim();
  if (v === '') delete state.gates[gateId]; else state.gates[gateId] = String(Math.max(0, Math.min(1000, Number(v) || 0)));
  saveState();
  showToast('点数を保存しました');
  if (inPlanDetail()) {
    const d = $('chapter-body').querySelector('[data-toggle-day]');
    if (d) showPlanDetail(Number(d.dataset.toggleDay));
  } else if (currentTab === 'today') renderToday();
});

$('backup-file').addEventListener('change', async (e) => {
  const f = e.target.files[0];
  e.target.value = '';
  if (!f) return;
  try {
    importBackup(await f.text());
    showToast('バックアップを読み込みました');
    renderSettings();
  } catch (err) {
    showToast('読み込めませんでした：' + err.message);
  }
});

async function doExport() {
  const name = `基本情報の記録_${todayStr()}.json`;
  const blob = new Blob([exportBackup()], { type: 'application/json' });
  // iPhoneでは共有シートから「ファイルに保存」できるようにする
  try {
    const file = new File([blob], name, { type: 'application/json' });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      await navigator.share({ files: [file], title: name });
      return;
    }
  } catch (err) {
    if (err && err.name === 'AbortError') return;
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

// 日付が変わったら(アプリを開いたまま翌日になった場合も)今の画面を描き直す
let lastDay = todayStr();
document.addEventListener('visibilitychange', () => {
  const busy = ['view-quiz', 'view-chapter', 'view-exam', 'view-settings'].some((v) => $(v).classList.contains('active'));
  if (document.visibilityState === 'visible' && todayStr() !== lastDay) {
    lastDay = todayStr();
    if (!busy) RENDER[currentTab]();
  }
  if (document.visibilityState === 'visible') checkForUpdate(false);
});

// ===== 自動アップデート =====
// サーバー上の最新の js/version.js を(キャッシュを通さず)取りに行き、今動いているバージョンと比べる
async function fetchLatestVersion() {
  const res = await fetch(`js/version.js?t=${Date.now()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('取得できませんでした');
  const m = (await res.text()).match(/APP_VERSION\s*=\s*['"]([^'"]+)['"]/);
  if (!m) throw new Error('バージョンを読み取れませんでした');
  return m[1];
}

let pendingReload = false;
let updateInFlight = false;
const RELOADED_KEY = 'fe-reloaded-for';
// 新しいバージョンがあれば、そのファイル一式を(配信キャッシュを素通りして)取り、本当に新しい版かを確かめてから
// 新しいキャッシュに入れ、画面を読み込み直す。service-worker.js 自体は中身が変わらないリリースもあるので、
// ブラウザの更新チェックだけに頼らない
async function checkForUpdate(manual) {
  if (updateInFlight) return;
  if (!('caches' in window)) { if (manual) reportUpdate('このブラウザでは確認できません', true); return; }
  updateInFlight = true;
  if (manual && $('update-status')) $('update-status').textContent = '確認しています…';
  try {
    const latest = await fetchLatestVersion();
    if (latest === APP_VERSION) {
      try { sessionStorage.removeItem(RELOADED_KEY); } catch (e) { /* なくても動く */ }
      reportUpdate(`最新のバージョン（${APP_VERSION}）です`, manual);
      return;
    }
    // 読み込み直したのにまだ古いときは、自動では繰り返さない(読み込み直しが止まらなくなるのを防ぐ)
    let reloaded = null;
    try { reloaded = sessionStorage.getItem(RELOADED_KEY); } catch (e) { /* なくても動く */ }
    if (!manual && reloaded === latest) {
      reportUpdate(`新しいバージョン（${latest}）に切り替わりませんでした。「最新バージョンか確認する」を押してください`, false);
      return;
    }

    const entries = await fetchFreshAssets(latest);   // 古いファイルしか返らなければここで止まる(次の確認でやり直す)
    const name = 'fe-cache-' + latest;
    await caches.delete(name);                         // 前に途中まで入れたものがあれば捨てる
    const cache = await caches.open(name);
    await Promise.all(entries.map(([href, res]) => cache.put(href, res)));
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== name).map((k) => caches.delete(k)));
    const reg = await navigator.serviceWorker?.getRegistration();
    if (reg) reg.update().catch(() => {});
    try { sessionStorage.setItem(RELOADED_KEY, latest); } catch (e) { /* なくても動く */ }

    if (['view-quiz', 'view-exam'].some((v) => $(v).classList.contains('active'))) {
      pendingReload = true;
      reportUpdate(`新しいバージョン（${latest}）があります。問題を終えたら更新します`, true);
    } else {
      reportUpdate(`新しいバージョン（${latest}）に更新します`, true);
      setTimeout(() => location.reload(), 900);
    }
  } catch (e) {
    const msg = String(e.message || '').includes('まだ')
      ? '新しいバージョンを公開した直後で、まだ準備中です。数分後にもう一度確認してください'
      : '確認できませんでした。通信状態を確かめてください';
    reportUpdate(msg, manual);
  } finally {
    updateInFlight = false;
  }
}

// ===== 起動 =====
$('app-version').textContent = 'v' + APP_VERSION;
switchTab('today'); // 開いたら毎回「今日」から
if ('serviceWorker' in navigator) {
  // service-worker.js が読み込むファイル(version.js など)もブラウザのキャッシュを通さずに更新を確かめる
  navigator.serviceWorker.register('service-worker.js', { updateViaCache: 'none' }).catch(() => {});
}
checkForUpdate(false); // 開いたときに、裏で新しいバージョンがないか確認する
