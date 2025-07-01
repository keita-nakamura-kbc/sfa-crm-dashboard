@echo off
REM SFA/CRM Dashboard Windows EXE Builder
REM Windows環境で実行してください

echo ================================
echo SFA/CRM Dashboard EXE Builder
echo ================================
echo.

REM Pythonのバージョン確認
echo Pythonバージョン確認中...
python --version
if %errorlevel% neq 0 (
    echo エラー: Pythonがインストールされていません
    echo Python 3.8以上をインストールしてください
    pause
    exit /b 1
)
echo.

REM 仮想環境のアクティベーション確認
echo 仮想環境確認中...
if exist "venv\Scripts\activate.bat" (
    echo 仮想環境が見つかりました。アクティベート中...
    call venv\Scripts\activate.bat
) else (
    echo 仮想環境が見つかりません。作成中...
    python -m venv venv
    call venv\Scripts\activate.bat
)
echo.

REM 依存関係のインストール
echo 依存関係インストール中...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo エラー: 依存関係のインストールに失敗しました
    pause
    exit /b 1
)
echo.

REM PyInstallerとPillowのインストール
echo PyInstallerとPillowインストール中...
pip install pyinstaller pillow
if %errorlevel% neq 0 (
    echo エラー: PyInstallerのインストールに失敗しました
    pause
    exit /b 1
)
echo.

REM 既存のビルドファイルを削除
echo 既存のビルドファイル削除中...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del *.spec
echo.

REM EXEファイルの作成
echo EXEファイル作成中...
echo この処理には数分かかる場合があります。お待ちください...
echo.

pyinstaller ^
  --onefile ^
  --console ^
  --add-data "assets;assets" ^
  --add-data "components;components" ^
  --add-data "layouts;layouts" ^
  --add-data "callbacks;callbacks" ^
  --add-data "images;images" ^
  --add-data "pdca_2025.xlsx;." ^
  --hidden-import dash ^
  --hidden-import dash_bootstrap_components ^
  --hidden-import plotly ^
  --hidden-import plotly.graph_objects ^
  --hidden-import plotly.express ^
  --hidden-import pandas ^
  --hidden-import openpyxl ^
  --hidden-import numpy ^
  --hidden-import werkzeug ^
  --hidden-import flask ^
  --hidden-import jinja2 ^
  --exclude-module matplotlib ^
  --exclude-module tkinter ^
  --exclude-module PyQt5 ^
  --exclude-module PyQt6 ^
  --exclude-module PySide2 ^
  --exclude-module PySide6 ^
  --name "SFA-CRM-Dashboard" ^
  main.py

if %errorlevel% neq 0 (
    echo.
    echo エラー: EXEファイルの作成に失敗しました
    echo エラーログを確認してください
    pause
    exit /b 1
)

echo.
echo ================================
echo ビルド完了！
echo ================================
echo.
echo 実行ファイルの場所: dist\SFA-CRM-Dashboard.exe
echo.

REM ファイルサイズ確認
if exist "dist\SFA-CRM-Dashboard.exe" (
    echo ファイル情報:
    dir "dist\SFA-CRM-Dashboard.exe"
    echo.
    echo 実行ファイルのテスト起動を行いますか？ ^(Y/N^)
    set /p test_run=
    if /i "%test_run%"=="Y" (
        echo テスト起動中...
        start "" "dist\SFA-CRM-Dashboard.exe"
        echo ブラウザでhttp://localhost:8050にアクセスしてダッシュボードを確認してください
    )
) else (
    echo エラー: 実行ファイルが見つかりません
)

echo.
echo 処理が完了しました。何かキーを押してください...
pause > nul