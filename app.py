"""
Deployment entry point for Render.com
本番環境用エントリーポイント
"""
from main import app, load_sample_data_on_startup

# 本番環境でもサンプルデータを自動読み込み
load_sample_data_on_startup()

# Gunicorn用のサーバーオブジェクトを公開
server = app.server

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)