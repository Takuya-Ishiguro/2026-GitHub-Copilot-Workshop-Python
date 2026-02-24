"""
ゲーミフィケーション要素を持つポモドーロタイマーアプリケーション
"""
from flask import Flask, render_template, jsonify, request
from models import PomodoroDatabase
import os

app = Flask(__name__)

# データベースの初期化
db_path = os.path.join(os.path.dirname(__file__), 'pomodoro.db')
db = PomodoroDatabase(db_path)


@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')


@app.route('/api/stats')
def get_stats():
    """統計情報を取得"""
    stats = db.get_user_stats()
    badges = db.get_badges()
    weekly = db.get_weekly_stats()
    monthly = db.get_monthly_stats()
    
    return jsonify({
        'user_stats': stats,
        'badges': badges,
        'weekly_stats': weekly,
        'monthly_stats': monthly
    })


@app.route('/api/complete_pomodoro', methods=['POST'])
def complete_pomodoro():
    """ポモドーロ完了を記録"""
    data = request.get_json() or {}
    duration = data.get('duration', 25)
    
    # ポモドーロを記録
    result = db.add_pomodoro(duration)
    
    # バッジチェック
    new_badges = db.check_and_award_badges()
    result['new_badges'] = new_badges
    
    return jsonify(result)


if __name__ == '__main__':
    # デバッグモードは環境変数で制御（デフォルトはFalse）
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
