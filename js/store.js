// 学習の記録(1日目の日付・完了した日・読んだ章・問題の正誤・模擬試験の点数)をこの端末に保存する
const STORE_KEY = 'fe-study-v1';

function emptyState() {
  // start: 1日目の日付 / done: 日目 -> 完了日時 / quiz: 問題id -> { n:解いた回数, ok:正解数, last:直近の正誤, streak:連続正解数, miss:間違えた回数, at }
  // gates: 関門の項目id -> 入力した点数 / drill: 日付 -> その日に解いた科目Aドリルの数
  // exams: 本番形式の模擬試験の記録 [{ at, part:'a'|'b', score(1000点換算), ok, n, sec }]
  return { start: null, done: {}, read: {}, quiz: {}, gates: {}, drill: {}, exams: [] };
}

let state = loadState();

function loadState() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (!raw) return emptyState();
    return Object.assign(emptyState(), JSON.parse(raw));
  } catch (e) {
    return emptyState();
  }
}

// 「間違えた問題」に残っているか: 一度でも間違えて、まだ3回続けて正解していない
const GRADUATE = 3;
function isWeak(r) {
  return !!r && r.miss > 0 && r.streak < GRADUATE;
}

function saveState() {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(state));
  } catch (e) {
    showToast('保存できませんでした。記録タブからバックアップを取ってください');
  }
}

// 1問ぶんの結果を記録する。last = 直近で正解したか
function recordAnswer(qid, ok) {
  const r = state.quiz[qid] || { n: 0, ok: 0, last: null, streak: 0, miss: 0 };
  r.n += 1;
  if (ok) { r.ok += 1; r.streak += 1; } else { r.streak = 0; r.miss += 1; }
  r.last = ok;
  r.at = new Date().toISOString();
  state.quiz[qid] = r;
  saveState();
}

// 正解したが勘で当てた場合は、間違えた扱いに直す(全部の理由を説明できて初めて正解、のルール)
function markGuess(qid) {
  const r = state.quiz[qid];
  if (!r || !r.last) return;
  r.ok -= 1;
  r.streak = 0;
  r.miss += 1;
  r.last = false;
  saveState();
}

function exportBackup() {
  return JSON.stringify({ app: 'fe-study', version: APP_VERSION, savedAt: new Date().toISOString(), state }, null, 1);
}

function importBackup(text) {
  const obj = JSON.parse(text);
  if (!obj || obj.app !== 'fe-study' || !obj.state) throw new Error('このアプリのバックアップではありません');
  state = Object.assign(emptyState(), obj.state);
  saveState();
}
