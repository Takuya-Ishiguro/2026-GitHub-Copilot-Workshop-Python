/**
 * ポモドーロタイマーのJavaScriptロジック
 * ステップ1: 最小限のタイマーUIとカウントダウン機能
 */

// タイマーの設定
const POMODORO_MINUTES = 25;
const POMODORO_SECONDS = POMODORO_MINUTES * 60;

// グローバル変数
let timeLeft = POMODORO_SECONDS; // 残り時間（秒）
let timerInterval = null; // タイマーのインターバルID
let isRunning = false; // タイマーが動作中かどうか

// DOM要素の取得
const timerDisplay = document.getElementById('timer');
const startBtn = document.getElementById('startBtn');
const resetBtn = document.getElementById('resetBtn');

/**
 * 時間を MM:SS 形式にフォーマット
 * @param {number} seconds - 秒数
 * @returns {string} フォーマットされた時間文字列
 */
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

/**
 * タイマー表示を更新
 */
function updateDisplay() {
    timerDisplay.textContent = formatTime(timeLeft);
}

/**
 * タイマーを開始
 */
function startTimer() {
    if (isRunning) return;
    
    isRunning = true;
    startBtn.disabled = true;
    startBtn.textContent = '実行中';
    
    timerInterval = setInterval(() => {
        timeLeft--;
        updateDisplay();
        
        // タイマー終了
        if (timeLeft <= 0) {
            stopTimer();
            alert('ポモドーロ完了！お疲れ様でした！');
            // ステップ3で進捗を更新する処理を追加予定
        }
    }, 1000);
}

/**
 * タイマーを停止
 */
function stopTimer() {
    isRunning = false;
    clearInterval(timerInterval);
    timerInterval = null;
    startBtn.disabled = false;
    startBtn.textContent = '開始';
}

/**
 * タイマーをリセット
 */
function resetTimer() {
    stopTimer();
    timeLeft = POMODORO_SECONDS;
    updateDisplay();
}

// イベントリスナーの設定
startBtn.addEventListener('click', startTimer);
resetBtn.addEventListener('click', resetTimer);

// 初期表示の更新
updateDisplay();
