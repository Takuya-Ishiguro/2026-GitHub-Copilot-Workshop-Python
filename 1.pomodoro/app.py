"""
Pomodoro Timer App

Flaskを使用したポモドーロタイマーWebアプリケーション
"""

from flask import Flask, render_template


def create_app(config=None):
    """アプリケーションファクトリ
    
    Args:
        config: アプリケーション設定（辞書）
    
    Returns:
        Flask: Flaskアプリケーションインスタンス
    """
    app = Flask(__name__)
    
    # デフォルト設定
    app.config.update({
        'TESTING': False,
    })
    
    # カスタム設定を適用
    if config:
        app.config.update(config)
    
    # ルーティング
    @app.route('/')
    def index():
        """メイン画面を表示"""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """ヘルスチェックエンドポイント"""
        return {'status': 'ok'}, 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
