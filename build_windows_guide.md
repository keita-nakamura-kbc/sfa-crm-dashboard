# Windows EXE ファイル作成ガイド

## 概要
このガイドでは、SFA/CRM DashboardをWindows実行ファイル(.exe)として配布用にビルドする方法を説明します。

## 前提条件

### Windows環境での実行が必要
- PyInstallerは作成される実行ファイルのプラットフォームが実行環境と同じになるため、Windows用のexeファイルを作成するにはWindows環境が必要です
- macOS/Linux環境からWindows用exeファイルの直接作成はサポートされていません

### 必要なソフトウェア
- Python 3.8以上
- pip (Pythonパッケージマネージャー)

## セットアップ手順

### 1. Pythonランタイムのセットアップ
```bash
# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート (Windows)
venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# PyInstallerインストール
pip install pyinstaller
```

### 2. EXEファイルの作成

#### 方法1: 簡単コマンド（推奨）
```bash
pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "components;components" --add-data "layouts;layouts" --add-data "callbacks;callbacks" --add-data "images;images" --add-data "pdca_2025.xlsx;." --hidden-import dash_bootstrap_components --hidden-import plotly --hidden-import pandas --hidden-import openpyxl --name "SFA-CRM-Dashboard" main.py
```

#### 方法2: 設定ファイル使用
```bash
# 事前準備されたspec設定ファイルを使用
pyinstaller build_windows.spec
```

### 3. ビルド結果
- 実行ファイルは `dist/` フォルダに生成されます
- ファイル名: `SFA-CRM-Dashboard.exe`

## 配布方法

### 単一ファイル配布
- `dist/SFA-CRM-Dashboard.exe` ファイル1つで配布可能
- Excelサンプルファイル（pdca_2025.xlsx）は実行ファイル内に埋め込まれます
- 初回起動時に自動的にサンプルデータが読み込まれます

### フォルダ配布（オプション）
フォルダ形式での配布が必要な場合：
```bash
pyinstaller --add-data "assets;assets" --add-data "components;components" --add-data "layouts;layouts" --add-data "callbacks;callbacks" --add-data "images;images" --add-data "pdca_2025.xlsx;." --hidden-import dash_bootstrap_components --hidden-import plotly --hidden-import pandas --hidden-import openpyxl --name "SFA-CRM-Dashboard" main.py
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. モジュール不足エラー
```
ModuleNotFoundError: No module named 'xxx'
```
**解決方法**: `--hidden-import xxx` オプションを追加

#### 2. ファイルパスエラー
```
FileNotFoundError: [Errno 2] No such file or directory
```
**解決方法**: `--add-data` オプションでファイル/フォルダを追加

#### 3. 実行ファイルサイズが大きい
**原因**: 不要なライブラリが含まれている
**解決方法**: `build_windows.spec` の `excludes` リストに不要なライブラリを追加

#### 4. 起動が遅い
**原因**: ウイルス対策ソフトの影響
**解決方法**: 実行ファイルを除外リストに追加、またはデジタル署名の付与を検討

### パフォーマンス最適化

#### UPX圧縮（オプション）
実行ファイルサイズを縮小:
1. UPXをダウンロード・インストール (https://upx.github.io/)
2. `build_windows.spec` で `upx=True` を確認

#### 除外設定
不要なライブラリを除外してサイズを削減:
- matplotlib（グラフライブラリ、Plotlyを使用しているため不要）
- tkinter（GUIライブラリ、Dashを使用しているため不要）
- PyQt/PySide（GUIライブラリ、不要）
- jupyter/IPython（開発用ツール、不要）

## デジタル署名（推奨）
Windowsでの信頼性向上のため、コード署名証明書の使用を推奨:
1. コード署名証明書を取得
2. signtoolを使用して署名
```bash
signtool sign /f your_certificate.p12 /p password /t http://timestamp.comodoca.com dist/SFA-CRM-Dashboard.exe
```

## 配布パッケージ作成

### インストーラー作成（オプション）
NSIS、Inno Setup、WiXなどを使用してインストーラーを作成できます。

#### Inno Setup使用例
```inno
[Setup]
AppName=SFA/CRM Analytics Dashboard
AppVersion=1.0
DefaultDirName={pf}\SFA-CRM-Dashboard
DefaultGroupName=SFA/CRM Analytics
OutputBaseFilename=SFA-CRM-Dashboard-Setup

[Files]
Source: "dist\SFA-CRM-Dashboard.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\SFA/CRM Dashboard"; Filename: "{app}\SFA-CRM-Dashboard.exe"
Name: "{commondesktop}\SFA/CRM Dashboard"; Filename: "{app}\SFA-CRM-Dashboard.exe"
```

## システム要件

### 最小要件
- Windows 10 以上（64bit推奨）
- RAM: 4GB以上
- ディスク空き容量: 100MB以上

### 推奨環境
- Windows 11
- RAM: 8GB以上
- ディスク空き容量: 500MB以上
- フルHD解像度（1920x1080）以上

## サポートと制限事項

### サポートされる機能
- Excel ファイルアップロード・処理
- インタラクティブダッシュボード
- データフィルタリング・可視化
- ダークテーマUI

### 制限事項
- インターネット接続は不要（スタンドアロン動作）
- Excelファイル形式は指定されたもののみサポート
- 同時ユーザー: 1ユーザー（デスクトップアプリ）

## 更新とメンテナンス

### バージョン更新時の手順
1. ソースコード更新
2. 依存関係確認・更新
3. テスト実行
4. 新しいexeファイル作成
5. デジタル署名適用
6. 配布・展開

### ログファイル
実行ファイルのログは以下の場所に保存されます:
- Windows: `%TEMP%\SFA-CRM-Dashboard.log`