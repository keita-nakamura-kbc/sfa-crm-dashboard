"""
SFA/CRM Dashboard - Main Application (EXE用)
実行ファイル用に最適化されたメインアプリケーション
"""
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import logging
import webbrowser
import threading
import time
import sys
import os

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PyInstallerで実行されているかチェック
if getattr(sys, 'frozen', False):
    # EXE実行時のパス設定
    application_path = sys._MEIPASS
else:
    # 開発時のパス設定
    application_path = os.path.dirname(os.path.abspath(__file__))

# カレントディレクトリを設定
os.chdir(application_path)

# カスタムモジュールのインポート
from config import DARK_COLORS, LAYOUT, ANIMATIONS
from data_manager import data_manager, get_dataframe_from_store, get_last_data_month, clean_channel_names, clean_plan_names
from components.header import create_header
from components.loading import create_inline_loading_text
from layouts.tab1_funnel import create_funnel_analysis_layout
from layouts.tab2_revenue import create_revenue_acquisition_layout
from callbacks.tab1_callbacks import register_tab1_callbacks
from callbacks.tab2_callbacks import register_tab2_callbacks

# Dashアプリケーションの初期化
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
    ],
    suppress_callback_exceptions=True,
    title="SFA/CRM Analytics Dashboard"
)

# サーバーインスタンスを取得
server = app.server

def open_browser():
    """3秒待ってからブラウザを開く"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:8050')
        logger.info("ブラウザが開きました")
    except Exception as e:
        logger.error(f"ブラウザを開けませんでした: {e}")
        print("\n=== ダッシュボードアクセス情報 ===")
        print("ブラウザで以下のURLにアクセスしてください:")
        print("http://localhost:8050")
        print("================================\n")

# カスタムCSSとインデックスHTMLは元のmain.pyと同じ
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            /* ダークテーマのベーススタイル */
            :root {{
                --bg-dark: {DARK_COLORS['bg_dark']};
                --bg-card: {DARK_COLORS['bg_card']};
                --bg-hover: {DARK_COLORS['bg_hover']};
                --text-primary: {DARK_COLORS['text_primary']};
                --text-secondary: {DARK_COLORS['text_secondary']};
                --text-muted: {DARK_COLORS['text_muted']};
                --border-color: {DARK_COLORS['border_color']};
                --border-light: {DARK_COLORS['border_light']};
                --primary-orange: {DARK_COLORS['primary_orange']};
                --primary-dark: {DARK_COLORS['primary_dark']};
                --secondary-blue: {DARK_COLORS['secondary_blue']};
                --accent-gold: {DARK_COLORS['accent_gold']};
                --success: {DARK_COLORS['success']};
                --warning: {DARK_COLORS['warning']};
                --danger: {DARK_COLORS['danger']};
                --chart-budget: {DARK_COLORS['chart_budget']};
                --chart-actual: {DARK_COLORS['chart_actual']};
            }}
            
            body {{
                background-color: var(--bg-dark);
                color: var(--text-primary);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }}
            
            /* 他のスタイルも元のmain.pyから継承 */
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

# レイアウトとコールバックの設定は元のmain.pyと同じ
# ... (省略 - 元のmain.pyからコピー)

# サンプルデータの自動読み込み
def load_sample_data_on_startup():
    """起動時にサンプルデータを自動読み込み"""
    sample_file = os.path.join(application_path, 'pdca_2025.xlsx')
    if os.path.exists(sample_file):
        try:
            with open(sample_file, 'rb') as f:
                content = f.read()
                import base64
                content_base64 = base64.b64encode(content).decode('utf-8')
                content_string = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{content_base64}"
                
                success, message = data_manager.update_data(content_string, 'pdca_2025.xlsx')
                if success:
                    logger.info("サンプルデータを自動読み込みしました")
                else:
                    logger.error(f"サンプルデータの読み込みに失敗: {message}")
        except Exception as e:
            logger.error(f"サンプルデータ読み込みエラー: {str(e)}")

# アプリケーションレイアウト（元のmain.pyからコピー）
app.layout = html.Div([
    # データストア
    dcc.Store(id='data-store', storage_type='session'),
    dcc.Store(id='filtered-channels', storage_type='session'),
    dcc.Store(id='filtered-plans', storage_type='session'),
    dcc.Store(id='last-data-month', storage_type='session'),
    dcc.Store(id='channel-filter-tab2', storage_type='session'),
    dcc.Store(id='plan-filter-tab2', storage_type='session'),
    
    # フィルター適用フラグストア
    dcc.Store(id='filters-applied', data=False),
    
    # ビュータイプストア（初期値: actual）
    dcc.Store(id='funnel-view-type', data='actual'),
    
    # 分析タイプストア（Tab2用）
    dcc.Store(id='analysis-type-state', data='revenue'),
    
    # ヘッダー
    create_header(),
    
    # メインコンテンツ
    html.Div([
        dcc.Tabs(
            id='main-tabs',
            value='tab-1',
            children=[
                dcc.Tab(
                    label='ファネル分析',
                    value='tab-1',
                    className='custom-tab',
                    selected_className='custom-tab-selected'
                ),
                dcc.Tab(
                    label='売上・獲得分析',
                    value='tab-2',
                    className='custom-tab',
                    selected_className='custom-tab-selected'
                ),
            ],
            className='custom-tabs'
        ),
        html.Div(id='tabs-content', className='tabs-content')
    ], className='main-container')
], className='app-container')

# コールバックの登録（元のmain.pyからコピー）
# ... (省略)

if __name__ == '__main__':
    # サンプルデータの読み込み
    load_sample_data_on_startup()
    
    # コールバックの登録
    register_tab1_callbacks(app)
    register_tab2_callbacks(app)
    
    # EXE実行時の処理
    if getattr(sys, 'frozen', False):
        print("\n=== SFA/CRM Analytics Dashboard ===")
        print("サーバーを起動中...")
        print("しばらくお待ちください...\n")
        
        # ブラウザを開くスレッドを開始
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    # アプリケーションの実行
    try:
        app.run_server(
            debug=False,  # EXE実行時はデバッグモード無効
            port=8050,
            host='127.0.0.1'  # localhostのみでアクセス
        )
    except Exception as e:
        logger.error(f"サーバー起動エラー: {e}")
        print(f"\nエラー: {e}")
        print("別のアプリケーションがポート8050を使用している可能性があります。")
        input("Enterキーを押して終了...")