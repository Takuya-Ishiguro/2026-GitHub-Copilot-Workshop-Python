# ポモドーロタイマーWebアプリ

Flask（Python）＋HTML/CSS/JavaScriptで構築するポモドーロタイマーWebアプリケーションです。

## プロジェクト構成

```
1.pomodoro/
├── app.py                # Flaskアプリ本体
├── logic.py              # ビジネスロジック
├── templates/            # HTMLテンプレート
│   └── index.html
├── static/               # 静的ファイル
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── timer.js
├── data/                 # データ保存
│   └── progress.json
├── tests/                # テスト
│   ├── test_logic.py
│   └── test_app.py
├── requirements.txt      # Python依存関係
├── architecture.md       # アーキテクチャ設計
├── features.md           # 機能一覧
└── plan.md              # 実装計画
```

## セットアップ

```bash
# 依存関係のインストール
pip install -r requirements.txt

# アプリケーションの起動
python app.py
```

## テスト実行

```bash
pytest tests/
```

## 開発ドキュメント

- [アーキテクチャ設計](architecture.md)
- [実装機能一覧](features.md)
- [段階的実装計画](plan.md)
