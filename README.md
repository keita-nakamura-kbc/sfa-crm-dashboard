# SFA/CRM Analytics Dashboard

モダンな Dark テーマの SFA/CRM 分析ダッシュボードです。Dash（Python Web フレームワーク）を使用して構築され、Excel データを処理してセールスファネル分析と売上メトリクスを Full HD（1920x1080）に最適化されたインターフェースで可視化します。

## 📊 主な機能

### **Tab1: ファネル分析**
- **ステージ別複合グラフ**: 実績・計画・達成率を統合表示
- **ファネルメトリクスバー**: 各ステージの KPI 一覧
- **経路別 CV 率トレンド**: チャネル別転換率の推移とスパークライン
- **ステージ別 CV 率トレンド**: ステージ間転換率の分析
- **ファネルインサイト**: AI による自動分析結果

### **Tab2: 売上・獲得分析**
- **メイントレンドチャート**: 月別推移の可視化（売上/獲得切り替え対応）
- **経路別・プラン別 KPI カード**: 詳細メトリクスとスパークライン
- **構成チャート**: 経路別・プラン別の割合分析
- **継続率・客単価分析**: カード形式での表示
- **フィルタリング機能**: チャネル・プラン別での絞り込み

### **共通機能**
- **レスポンシブデザイン**: Full HD 解像度に最適化
- **ダークテーマ**: 目に優しいモダン UI
- **リアルタイム更新**: フィルター変更時の即座な反映
- **データキャッシング**: クライアントサイドでの高速処理

## 🏗️ アーキテクチャ

### **コア構造**
```
main.py                 # エントリーポイント、Dash アプリ初期化
config.py              # 設定、カラー、レイアウト、データマッピング
data_manager.py        # Excel データ処理、キャッシング、データ変換
```

### **モジュール構成**
```
components/            # 再利用可能 UI コンポーネント
├── cards.py          # KPI カード、トレンドアイテム
├── charts.py         # グラフ作成関数
└── header.py         # ヘッダーコンポーネント

layouts/              # タブ別レイアウト
├── tab1_funnel.py    # ファネル分析レイアウト
└── tab2_revenue.py   # 売上・獲得分析レイアウト

callbacks/            # タブ別インタラクティブ処理
├── tab1_callbacks.py # ファネル分析コールバック
└── tab2_callbacks.py # 売上・獲得分析コールバック

assets/               # CSS スタイル
├── style.css         # グローバルスタイル
└── tab1-specific.css # Tab1 専用スタイル
```

### **データフロー**
1. Excel ファイルをヘッダーコンポーネントでアップロード
2. DataManager が EXCEL_STRUCTURE 設定を使用してシートを処理
3. データを dcc.Store コンポーネントでクライアントサイドキャッシュ
4. タブ別コールバックがユーザーインタラクションに基づいて可視化を更新

## 🚀 セットアップ

### **開発環境**
```bash
# 仮想環境作成（初回のみ）
python -m venv venv

# 仮想環境アクティベート
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 依存関係インストール
pip install -r requirements.txt

# アプリケーション実行
python main.py

# ダッシュボードアクセス
# http://localhost:8050
```

### **本番環境構築**
```bash
# PyInstaller インストール
pip install pyinstaller

# 実行ファイル作成
pyinstaller --onefile --add-data "assets:assets" --add-data "components:components" --add-data "layouts:layouts" --add-data "callbacks:callbacks" --hidden-import dash_bootstrap_components main.py

# 実行ファイルは dist/ ディレクトリに生成
```

## 📋 依存関係

### **主要ライブラリ**
- **Dash 2.18.2**: Web フレームワーク
- **Plotly 5.24.1**: チャート・可視化
- **Pandas 2.2.0**: データ処理
- **openpyxl 3.1.2**: Excel ファイル処理
- **Dash Bootstrap Components 1.6.0**: UI コンポーネント

### **開発ツール（オプション）**
```bash
# requirements.txt でコメントアウトされた開発依存関係
pip install pytest black flake8

# リント実行
flake8 . --exclude=venv

# コードフォーマット
black . --exclude=venv

# テスト実行
pytest
```

## 📁 データソース

### **Excel ファイル仕様**
- **ファイル名**: 任意（アップロード対応）
- **シート名**: '25 年 PDCA'
- **構造**: config.py の EXCEL_STRUCTURE で定義

### **データセクション**
- **sales**: 売上データ（単月形式）
- **acquisition**: 獲得データ（累月形式）
- **unit_price**: 客単価データ
- **retention**: 継続率データ
- **indicators**: 指標データ（ファネル分析用）

### **データマッピング**
```python
STAGE_MAPPING = {
    'リード': [101, 102, 103],
    'アプローチ': [104, 105, 106],
    # ... 詳細は config.py 参照
}
```

## 🎨 UI テーマシステム

### **カラーパレット**
```python
DARK_COLORS = {
    'bg_dark': '#1a202c',      # メイン背景
    'bg_card': '#2d3748',      # カード背景
    'text_primary': '#e2e8f0', # プライマリテキスト
    'success': '#48bb78',      # 成功色
    'warning': '#ed8936',      # 警告色
    'danger': '#f56565',       # 危険色
    # ... 詳細は config.py 参照
}
```

### **レスポンシブレイアウト**
- **Tab2 セクション比率**: 30:45:25 (Row1:Row2:Row3)
- **フレックスボックス**: `flex: 0 0 X%` で固定比率
- **CSS カスタムプロパティ**: 一貫したスペーシング・カラー

## ⚡ パフォーマンス最適化

### **データ処理**
- **統一計算関数**: `calculate_kpi_values()` による一貫性
- **フィルタリング最適化**: 事前フィルタリングで重複排除
- **キャッシング**: dcc.Store でのクライアントサイド保存

### **レンダリング**
- **スパークライン**: 幅・線太さ最適化
- **カードソート**: 0%・N/A 達成率を最下段配置
- **色分け**: パフォーマンスに応じたヒートマップカラー

## 🔧 カスタマイズ

### **テーマ変更**
```python
# config.py で色設定を変更
DARK_COLORS['success'] = '#新しい色コード'
```

### **レイアウト調整**
```python
# config.py でレスポンシブ設定を変更
LAYOUT['card_padding'] = '新しいパディング値'
```

### **データソース拡張**
```python
# config.py で Excel 構造を定義
EXCEL_STRUCTURE['sections']['新セクション'] = (開始行, 終了行)
```

## 🛠️ 開発パターン

### **新規コンポーネント追加**
1. `components/` フォルダに関数を作成
2. 関連レイアウトファイルでインポート・使用
3. ダークテーマスタイリングパターンに従う

### **新規コールバック追加**
1. 適切な `callbacks/` ファイルに追加
2. `main.py` で `register_tabX_callbacks()` 経由で登録
3. 状態管理には dcc.Store を使用

### **エラーハンドリング**
```python
try:
    # データ処理コード
    return 結果
except Exception as e:
    logger.error(f"Error in 関数名: {str(e)}")
    return 空の結果
```

## 📊 データストアコンポーネント

### **グローバルストア**
- `'data-store'`: メイン処理済みデータ
- `'last-data-month'`: 最新データ月追跡

### **フィルター状態**
- `'filtered-channels'`: チャネルフィルター状態
- `'filtered-plans'`: プランフィルター状態
- `'channel-filter-tab2'`: Tab2 専用チャネルフィルター
- `'plan-filter-tab2'`: Tab2 専用プランフィルター

## 🌐 多言語対応

### **日本語サポート**
- UI テキスト: 完全日本語対応
- 日付形式: 日本標準（例：'2025 年 1 月'）
- 通貨表示: 日本円（¥）
- ビジネス用語: 日本企業環境に最適化

## 🎯 ビジネス用語統一

### **用語標準化**
- "予算"、"計画値"、"予算値" → **"計画"** に統一
- 達成率計算: (実績 ÷ 計画) × 100
- ソート順: 低達成率優先、0%・N/A は最下段

## 🔍 トラブルシューティング

### **よくある問題**
1. **Excel シート名エラー**: '25 年 PDCA' シートが存在するか確認
2. **データ形式エラー**: 数値列に文字列が含まれていないか確認
3. **パフォーマンス問題**: ブラウザの開発者ツールでネットワーク・メモリ使用量を確認

### **デバッグ方法**
```python
# ログレベル設定
import logging
logging.basicConfig(level=logging.DEBUG)

# データ確認
print(data_manager.get_data())
```

## 📈 ロードマップ

### **将来の改善予定**
- [ ] 自動テストスイート実装
- [ ] CI/CD パイプライン構築
- [ ] API エンドポイント追加
- [ ] リアルタイムデータ同期
- [ ] ユーザー認証システム

## 🤝 貢献

### **開発ワークフロー**
1. フィーチャーブランチ作成
2. 変更実装・テスト
3. プルリクエスト作成
4. コードレビュー・マージ

### **コード品質**
- Black フォーマッター使用
- Flake8 リンター準拠
- 関数・変数名は日本語ビジネスコンテキストに合わせて命名
- 既存コードスタイル・パターンに従う

## 📄 ライセンス

このプロジェクトは独自ライセンスの下で開発されています。詳細については、プロジェクト管理者にお問い合わせください。

---

**Generated with [Claude Code](https://claude.ai/code)**