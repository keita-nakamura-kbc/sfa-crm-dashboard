"""
SFA/CRM Dashboard - Main Application
メインアプリケーションファイル
"""
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
app = dash.Dash(__name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,  # Bootstrap基本スタイル
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
        "/assets/tab1-specific.css"  # Tab1専用CSS
    ],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ]
)

app.title = "SFA/CRM Analytics Dashboard"
server = app.server

# カスタムCSSを適用
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            /* アニメーション */
            {ANIMATIONS}

            /* 全体スタイル */
            html, body {{
                height: 100dvh;
                box-sizing: border-box;
            }}
            
            body {{
                background-color: {DARK_COLORS['bg_dark']} !important;
                color: {DARK_COLORS['text_primary']} !important;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                margin: 0;
                padding: 0;
                overflow-x: hidden;
                box-sizing: border-box;
            }}
            
            #react-entry-point, #_dash-app-content {{
                height: 100dvh;
                box-sizing: border-box;
            }}
            
            *, *::before, *::after {{
                box-sizing: border-box;
            }}
            
            /* グローバルテキストカラー */
            * {{
                color: {DARK_COLORS['text_primary']};
            }}
            
            /* Dash コンポーネントのデフォルトテキストカラー */
            ._dash-loading {{
                color: {DARK_COLORS['text_primary']} !important;
            }}
            
            div {{
                color: {DARK_COLORS['text_primary']};
            }}

            /* タブスタイル */
            .tab-container {{
                background-color: {DARK_COLORS['bg_card']};
                border: none;
            }}

            .tab {{
                background-color: transparent !important;
                border: none !important;
                color: {DARK_COLORS['text_secondary']} !important;
            }}

            .tab--selected {{
                background-color: {DARK_COLORS['primary_orange']} !important;
                color: {DARK_COLORS['text_primary']} !important;
            }}

            /* コントロールボタン */
            .control-button {{
                background: transparent;
                border: 1px solid {DARK_COLORS['border_light']};
                color: {DARK_COLORS['text_secondary']};
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 0.875rem;
                cursor: pointer;
                transition: all {LAYOUT['transition']};
                font-family: inherit;
            }}

            .control-button:hover {{
                background: {DARK_COLORS['bg_hover']};
                border-color: {DARK_COLORS['primary_orange']};
                color: {DARK_COLORS['text_primary']};
            }}

            .control-button.active {{
                background: {DARK_COLORS['primary_orange']};
                border-color: {DARK_COLORS['primary_orange']};
                color: {DARK_COLORS['text_primary']};
            }}

            /* ビュータグルボタン */
            .view-toggle-btn {{
                padding: 4px 12px;
                background: transparent;
                border: none;
                color: {DARK_COLORS['text_secondary']};
                font-size: 0.75rem;
                font-weight: 500;
                cursor: pointer;
                border-radius: 4px;
                transition: all {LAYOUT['transition']};
            }}

            .view-toggle-btn.active {{
                background: {DARK_COLORS['primary_orange']};
                color: {DARK_COLORS['text_primary']};
            }}

            /* ドロップダウン - 改善版 */
            .dark-dropdown {{
                background-color: {DARK_COLORS['bg_card']} !important;
                border: 1px solid {DARK_COLORS['border_color']} !important;
                color: {DARK_COLORS['text_secondary']} !important;
            }}

            .dark-dropdown-small {{
                background-color: {DARK_COLORS['bg_card']} !important;
                border: 1px solid {DARK_COLORS['border_color']} !important;
                color: {DARK_COLORS['text_secondary']} !important;
            }}

            /* ドロップダウンメニューのオプション */
            .Select-menu-outer {{
                background-color: {DARK_COLORS['bg_card']} !important;
                border: 1px solid {DARK_COLORS['border_light']} !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            }}

            .Select-menu {{
                background-color: {DARK_COLORS['bg_card']} !important;
            }}

            .Select-option {{
                background-color: {DARK_COLORS['bg_card']} !important;
                color: {DARK_COLORS['text_secondary']} !important;
                padding: 8px 12px !important;
            }}

            .Select-option:hover,
            .Select-option.is-focused {{
                background-color: {DARK_COLORS['bg_hover']} !important;
                color: {DARK_COLORS['text_primary']} !important;
            }}

            .Select-option.is-selected {{
                background-color: {DARK_COLORS['primary_orange']} !important;
                color: {DARK_COLORS['text_primary']} !important;
            }}

            /* React-Select v2+ 用の新しいクラス */
            .css-26l3qy-menu {{
                background-color: {DARK_COLORS['bg_card']} !important;
                border: 1px solid {DARK_COLORS['border_light']} !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            }}

            .css-4ljt47-MenuList {{
                background-color: {DARK_COLORS['bg_card']} !important;
            }}

            .css-9jq23d {{
                color: {DARK_COLORS['text_secondary']} !important;
            }}

            .css-1uccc91-singleValue {{
                color: {DARK_COLORS['text_secondary']} !important;
            }}

            .css-1wa3eu0-placeholder {{
                color: {DARK_COLORS['text_muted']} !important;
            }}

            /* Dash Dropdown 専用スタイル */
            .dash-dropdown .Select-control {{
                background-color: {DARK_COLORS['bg_card']} !important;
                border: 1px solid {DARK_COLORS['border_color']} !important;
            }}

            .dash-dropdown .Select-input input {{
                color: {DARK_COLORS['text_secondary']} !important;
            }}

            .dash-dropdown .Select-value-label {{
                color: {DARK_COLORS['text_secondary']} !important;
            }}

            .dash-dropdown .Select-placeholder {{
                color: {DARK_COLORS['text_muted']} !important;
            }}

            /* より具体的なDash Dropdownスタイル */
            div[class*="dash-dropdown"] .Select-menu-outer {{
                background-color: {DARK_COLORS['bg_card']} !important;
                border: 1px solid {DARK_COLORS['border_light']} !important;
                z-index: 9999 !important;
            }}

            div[class*="dash-dropdown"] .Select-option {{
                background-color: {DARK_COLORS['bg_card']} !important;
                color: {DARK_COLORS['text_secondary']} !important;
                border-bottom: 1px solid {DARK_COLORS['border_color']} !important;
            }}

            div[class*="dash-dropdown"] .Select-option:hover {{
                background-color: {DARK_COLORS['bg_hover']} !important;
                color: {DARK_COLORS['text_primary']} !important;
            }}

            div[class*="dash-dropdown"] .Select-option:last-child {{
                border-bottom: none !important;
            }}

            /* dcc.Dropdown の直接的なスタイリング */
            .dash-core-components .dropdown .Select-menu-outer {{
                background: {DARK_COLORS['bg_card']} !important;
                border: 1px solid {DARK_COLORS['border_light']} !important;
            }}

            .dash-core-components .dropdown .Select-option {{
                background: {DARK_COLORS['bg_card']} !important;
                color: {DARK_COLORS['text_secondary']} !important;
                font-size: 0.8rem !important;
            }}

            .dash-core-components .dropdown .Select-option:hover {{
                background: {DARK_COLORS['bg_hover']} !important;
                color: {DARK_COLORS['text_primary']} !important;
            }}

            /* 全ドロップダウン要素への強制適用 */
            [class*="Select-menu"] {{
                background-color: {DARK_COLORS['bg_card']} !important;
                border: 1px solid {DARK_COLORS['border_light']} !important;
            }}

            [class*="Select-option"] {{
                background-color: {DARK_COLORS['bg_card']} !important;
                color: {DARK_COLORS['text_secondary']} !important;
            }}

            [class*="Select-option"]:hover {{
                background-color: {DARK_COLORS['bg_hover']} !important;
                color: {DARK_COLORS['text_primary']} !important;
            }}

            /* グリッドレイアウト - セクション分離 */
            .grid-container {{
                display: grid;
                gap: {LAYOUT['gap']};
            }}

            .grid-section {{
                background-color: {DARK_COLORS['bg_card']};
                border: 2px solid {DARK_COLORS['border_color']};
                border-radius: {LAYOUT['card_radius']};
                padding: {LAYOUT['card_padding']};
                transition: all {LAYOUT['transition']};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }}

            .grid-section:hover {{
                border-color: {DARK_COLORS['border_light']};
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
            }}

            /* セクション間のより明確な境界 */
            .section-divider {{
                height: 2px;
                background: linear-gradient(90deg, transparent, {DARK_COLORS['border_light']}, transparent);
                margin: {LAYOUT['gap']} 0;
            }}

            /* カードコンテナのスタイル改善 */
            .card-container {{
                border: 2px solid {DARK_COLORS['border_color']};
                background: {DARK_COLORS['bg_card']};
                border-radius: {LAYOUT['card_radius']};
                transition: all {LAYOUT['transition']};
            }}

            .card-container {{
                will-change: transform, border-color;
                transition: transform 0.15s ease, border-color 0.15s ease;
            }}

            .card-container:hover {{
                border-color: {DARK_COLORS['primary_orange']};
                transform: translateY(-1px);
            }}

            /* カード共通スタイル - GPU最適化 */
            .metric-card {{
                will-change: transform;
                transition: transform 0.15s ease;
            }}

            .metric-card:hover {{
                transform: translateY(-1px);
                border-color: {DARK_COLORS['border_light']} !important;
            }}

            .performance-card {{
                position: relative;
                overflow: hidden;
            }}

            .performance-card::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 4px;
                transition: opacity {LAYOUT['transition']};
                opacity: 0;
            }}

            .performance-card {{
                will-change: transform;
                transition: transform 0.15s ease;
            }}

            .performance-card:hover {{
                transform: translateX(2px);
                border-color: {DARK_COLORS['border_light']} !important;
            }}

            .performance-card:hover::before {{
                opacity: 1;
            }}

            .performance-card.good::before {{
                background: {DARK_COLORS['success']};
            }}

            .performance-card.warning::before {{
                background: {DARK_COLORS['warning']};
            }}

            .performance-card.danger::before {{
                background: {DARK_COLORS['danger']};
            }}

            /* ファネルステージ - GPU最適化 */
            .funnel-stage {{
                will-change: transform;
                transition: transform 0.15s ease;
            }}

            .funnel-stage:hover {{
                transform: scale(1.01);
            }}

            /* チャネルヘッダー */
            .channel-header.good {{
                background: rgba(72, 187, 120, 0.1) !important;
                border-color: {DARK_COLORS['success']} !important;
            }}

            .channel-header.warning {{
                background: rgba(237, 137, 54, 0.1) !important;
                border-color: {DARK_COLORS['warning']} !important;
            }}

            .channel-header.danger {{
                background: rgba(229, 62, 62, 0.1) !important;
                border-color: {DARK_COLORS['danger']} !important;
            }}

            /* インサイトアイテム - 軽量化 */
            .insight-item {{
                will-change: transform;
                transition: transform 0.15s ease, background-color 0.15s ease;
            }}

            .insight-item:hover {{
                background: rgba(255,255,255,0.05) !important;
                transform: translateX(1px);
            }}

            /* スクロールバー */
            .scrollable-container::-webkit-scrollbar {{
                width: 4px;
            }}

            .scrollable-container::-webkit-scrollbar-track {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 2px;
            }}

            .scrollable-container::-webkit-scrollbar-thumb {{
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
            }}

            .scrollable-container::-webkit-scrollbar-thumb:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}

            /* Plotlyグラフのカスタマイズ */
            .js-plotly-plot .plotly .main-svg {{
                background: transparent !important;
            }}

            .js-plotly-plot .plotly .gtitle {{
                font-family: 'Inter', sans-serif !important;
            }}

            /* ロゴスタイル */
            .header-logo {{
                height: 28px;
                width: auto;
                object-fit: contain;
                margin-right: 8px;
                transition: opacity 0.2s ease;
            }}

            .header-logo:hover {{
                opacity: 0.8;
            }}

            /* レスポンシブ対応 */
            @media (max-width: 1366px) {{
                .metric-card {{
                    padding: 12px;
                }}
                
                .main-container {{
                    padding: 12px;
                }}
                
                .header-logo {{
                    height: 24px;  /* 小画面では少し小さく */
                }}
            }}

            @media (max-width: 768px) {{
                .header-logo {{
                    height: 20px;  /* モバイルサイズ */
                    margin-right: 6px;
                }}
            }}

            /* Tab2レイアウト修正 */
            .revenue-tab-wrapper {{
                height: calc(100dvh - var(--header-height)) !important;
                overflow: hidden !important;
            }}
            
            .section-card {{
                height: 100% !important;
                display: flex !important;
                flex-direction: column !important;
            }}

            /* ローディング状態 */
            .dash-spinner {{
                background-color: {DARK_COLORS['bg_dark']} !important;
            }}

            .dash-spinner::after {{
                border-color: {DARK_COLORS['primary_orange']} transparent {DARK_COLORS['primary_orange']} transparent !important;
            }}
            
            /* 静的ローディング表示 */
            .loading-pulse {{
                opacity: 0.6;
                transition: opacity 0.3s ease;
            }}
            
            .loading-skeleton {{
                background: linear-gradient(90deg, 
                    {DARK_COLORS['border_color']} 25%, 
                    rgba(255,255,255,0.1) 50%, 
                    {DARK_COLORS['border_color']} 75%);
                background-size: 200% 100%;
                border-radius: 4px;
            }}
            
            .chart-loading-container {{
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 200px;
                background-color: {DARK_COLORS['bg_card']};
                border: 1px dashed {DARK_COLORS['border_color']};
                border-radius: 8px;
                opacity: 0.8;
            }}
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

# メインレイアウト
app.layout = html.Div([
    # ヘッダー（タブ含む）
    create_header(),
    
    # メインコンテンツエリア
    html.Main([
        # タブコンテンツ
        html.Div(id='tab-content', **{
            'role': 'tabpanel',
            'aria-live': 'polite'
        }),
    ], **{
        'role': 'main'
    }),
    
    # Hidden stores for data
    dcc.Store(id='data-type-state', data='plan_ratio'),
    dcc.Store(id='period-type-state', data='cumulative'),
    dcc.Store(id='active-tab', data='tab-1'),
    dcc.Store(id='stage-cv-filter', data=None),
    dcc.Store(id='analysis-type-state', data='acquisition'),  # 獲得/売上の状態管理
    
    # 初期化トリガー用のhidden div
    html.Div(id='app-initialization', children='initialized', style={'display': 'none'})
], style={
    'minHeight': '100vh',
    'backgroundColor': DARK_COLORS['bg_dark']
})

# グローバルコールバック: タブ切り替え
@app.callback(
    [Output('tab-content', 'children'),
     Output('tab-1-button', 'style'),
     Output('tab-2-button', 'style'),
     Output('active-tab', 'data'),
     Output('channel-filter-tab1-container', 'style'),
     Output('channel-filter-tab2-container', 'style'),
     Output('plan-filter-tab2-container', 'style'),
     Output('acquisition-revenue-toggle-container', 'style')],
    [Input('tab-1-button', 'n_clicks'),
     Input('tab-2-button', 'n_clicks')],
    [State('active-tab', 'data')]
)
def render_tab_content(tab1_clicks, tab2_clicks, active_tab):
    ctx = dash.callback_context
    
    # 共通タブスタイル
    def get_tab_style(is_active=False, margin_right=None):
        style = {
            'background': DARK_COLORS['primary_orange'] if is_active else 'transparent',
            'border': 'none',
            'color': DARK_COLORS['text_primary'] if is_active else DARK_COLORS['text_secondary'],
            'padding': '8px 16px',
            'borderRadius': '6px 6px 0 0',
            'fontSize': '0.875rem',
            'fontWeight': '500',
            'cursor': 'pointer'
        }
        if margin_right:
            style['marginRight'] = margin_right
        return style
    
    # どのボタンがクリックされたか判定
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'tab-1-button':
            active_tab = 'tab-1'
        elif button_id == 'tab-2-button':
            active_tab = 'tab-2'
    
    # アクティブなタブに応じてスタイルを設定
    if active_tab == 'tab-1':
        tab1_style = get_tab_style(is_active=True, margin_right='8px')
        tab2_style = get_tab_style(is_active=False)
        content = create_funnel_analysis_layout()
        # タブ1では経路フィルタを表示、タブ2のフィルターと獲得/売上切り替えは非表示
        tab1_filter_style = {'marginRight': '24px', 'display': 'block'}
        tab2_channel_filter_style = {'marginRight': '12px', 'display': 'none'}
        tab2_plan_filter_style = {'marginRight': '24px', 'display': 'none'}
        acquisition_revenue_toggle_style = {'marginRight': '12px', 'display': 'none'}
    else:
        tab1_style = get_tab_style(is_active=False, margin_right='8px')
        tab2_style = get_tab_style(is_active=True)
        content = create_revenue_acquisition_layout()
        # タブ2では全てのフィルタと獲得/売上切り替えを表示、タブ1は非表示
        tab1_filter_style = {'marginRight': '24px', 'display': 'none'}
        tab2_channel_filter_style = {'marginRight': '12px', 'display': 'block'}
        tab2_plan_filter_style = {'marginRight': '24px', 'display': 'block'}
        acquisition_revenue_toggle_style = {'marginRight': '12px', 'display': 'block'}
    
    return content, tab1_style, tab2_style, active_tab, tab1_filter_style, tab2_channel_filter_style, tab2_plan_filter_style, acquisition_revenue_toggle_style

# データアップロード処理（ローディング表示対応）
@app.callback(
    [Output('month-selector', 'options'),
     Output('month-selector', 'value'),
     Output('channel-filter', 'options'),
     Output('plan-filter', 'options'),
     Output('channel-filter-tab1', 'options'),
     Output('channel-filter-tab2', 'options'),
     Output('plan-filter-tab2', 'options'),
     Output('last-update-container', 'children')],
    [Input('upload-data', 'contents'),
     Input('app-initialization', 'children')],  # 初期化トリガーを追加
    [State('upload-data', 'filename')]
)
def handle_file_upload(contents, initialization_trigger, filename):
    # ローディング表示を返す関数
    def get_loading_state():
        return ([], None, [], [], [], [], [], create_inline_loading_text("データを処理中..."))
    
    # アップロードファイルがある場合の処理
    if contents is not None:
        success, message = data_manager.update_data(contents, filename)
    else:
        # 初期化時：既存のデータがあるかチェック
        existing_data = data_manager.get_data()
        success = existing_data is not None
        message = "サンプルデータ読み込み済み" if success else "データなし"
    
    if success:
        data = data_manager.get_data()
        
        # 月選択オプションを生成
        month_options = []
        if 'sales' in data and 'budget' in data['sales']:
            budget_df = get_dataframe_from_store(data, 'sales', 'budget')
            if budget_df is not None and not budget_df.empty:
                month_cols = [col for col in budget_df.columns if col.endswith('月')]
                month_options = [{'label': month, 'value': month} for month in month_cols]
        
        # チャネルオプションを生成
        channel_options = []
        if 'sales' in data and 'actual' in data['sales']:
            actual_data = get_dataframe_from_store(data, 'sales', 'actual')
            if actual_data is not None and not actual_data.empty:
                raw_channels = actual_data['channel'].dropna().unique()
                cleaned_channels = clean_channel_names(raw_channels)
                channel_options = [{'label': ch, 'value': ch} for ch in sorted(cleaned_channels)]
        
        # プランオプションを生成
        plan_options = []
        if 'sales' in data and 'actual' in data['sales']:
            actual_data = get_dataframe_from_store(data, 'sales', 'actual')
            if actual_data is not None and not actual_data.empty:
                raw_plans = actual_data['plan'].dropna().unique()
                cleaned_plans = clean_plan_names(raw_plans)
                plan_options = [{'label': plan, 'value': plan} for plan in sorted(cleaned_plans)]
        
        # デフォルト月を設定
        default_month = None
        if month_options and 'sales' in data and 'actual' in data['sales']:
            actual_data = get_dataframe_from_store(data, 'sales', 'actual')
            if actual_data is not None and not actual_data.empty:
                month_cols = [col for col in actual_data.columns if col.endswith('月')]
                default_month = get_last_data_month(actual_data, month_cols)
        
        if default_month is None and month_options:
            default_month = month_options[-1]['value']
        
        # 成功時の更新表示
        last_update_display = html.Span(
            f"最終更新: {data_manager.get_last_update()}",
            style={
                'color': DARK_COLORS['text_muted'],
                'fontSize': '0.75rem'
            }
        )
        
        return (
            month_options, 
            default_month, 
            channel_options, 
            plan_options, 
            channel_options,  # Tab1の経路フィルタにも同じチャネルオプションを設定
            channel_options,  # Tab2の経路フィルタにも同じチャネルオプションを設定
            plan_options,     # Tab2のプランフィルタにも同じプランオプションを設定
            last_update_display
        )
    else:
        # エラー時の表示
        error_display = html.Span(
            f"最終更新: エラー - {message}",
            style={
                'color': DARK_COLORS['danger'],
                'fontSize': '0.75rem'
            }
        )
        return [], None, [], [], [], [], [], error_display

# ボタン状態管理: 計画比/計画差
@app.callback(
    [Output('btn-plan-ratio', 'className'),
     Output('btn-plan-diff', 'className'),
     Output('data-type-state', 'data')],
    [Input('btn-plan-ratio', 'n_clicks'),
     Input('btn-plan-diff', 'n_clicks')],
    [State('data-type-state', 'data')]
)
def update_data_type_buttons(ratio_clicks, diff_clicks, current_state):
    import dash
    if not dash.callback_context.triggered:
        return 'control-button active', 'control-button', 'plan_ratio'
    
    button_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-plan-ratio':
        return 'control-button active', 'control-button', 'plan_ratio'
    elif button_id == 'btn-plan-diff':
        return 'control-button', 'control-button active', 'plan_diff'
    
    return 'control-button active', 'control-button', current_state

# ボタン状態管理: 累月/単月
@app.callback(
    [Output('btn-cumulative', 'className'),
     Output('btn-single', 'className'),
     Output('period-type-state', 'data')],
    [Input('btn-cumulative', 'n_clicks'),
     Input('btn-single', 'n_clicks')],
    [State('period-type-state', 'data')]
)
def update_period_type_buttons(cumulative_clicks, single_clicks, current_state):
    import dash
    if not dash.callback_context.triggered:
        return 'control-button active', 'control-button', 'cumulative'
    
    button_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-cumulative':
        return 'control-button active', 'control-button', 'cumulative'
    elif button_id == 'btn-single':
        return 'control-button', 'control-button active', 'single'
    
    return 'control-button active', 'control-button', current_state

# ボタン状態管理: 獲得/売上
@app.callback(
    [Output('btn-acquisition', 'className'),
     Output('btn-revenue', 'className'),
     Output('analysis-type-state', 'data')],
    [Input('btn-acquisition', 'n_clicks'),
     Input('btn-revenue', 'n_clicks')],
    [State('analysis-type-state', 'data')]
)
def update_analysis_type_buttons(acquisition_clicks, revenue_clicks, current_state):
    import dash
    if not dash.callback_context.triggered:
        return 'control-button active', 'control-button', 'acquisition'
    
    button_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-acquisition':
        return 'control-button active', 'control-button', 'acquisition'
    elif button_id == 'btn-revenue':
        return 'control-button', 'control-button active', 'revenue'
    
    return 'control-button active', 'control-button', current_state

# タブ別コールバックの登録
register_tab1_callbacks(app)
register_tab2_callbacks(app)

# 起動時のサンプルデータ自動読み込み
def load_sample_data_on_startup():
    """起動時にサンプルデータを自動読み込み"""
    import os
    sample_file = 'pdca_2025.xlsx'
    
    if os.path.exists(sample_file):
        try:
            # サンプルファイルを読み込み
            with open(sample_file, 'rb') as f:
                file_content = f.read()
            
            # Base64エンコード（Dashのfile upload形式に合わせる）
            import base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            file_data = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{encoded_content}"
            
            # データマネージャーにデータを読み込み
            success, message = data_manager.update_data(file_data, sample_file)
            if success:
                logger.info(f"✅ サンプルデータを自動読み込みしました: {sample_file}")
                return True
            else:
                logger.warning(f"⚠️ サンプルデータの読み込みに失敗: {message}")
        except Exception as e:
            logger.error(f"❌ サンプルデータ読み込みエラー: {str(e)}")
    else:
        logger.info(f"ℹ️ サンプルファイルが見つかりません: {sample_file}")
    
    return False

# 起動時にサンプルデータを自動読み込み（コールバック登録後に実行）
load_sample_data_on_startup()

# アプリケーション実行
if __name__ == '__main__':
    app.run_server(
        debug=True, 
        port=8050,
        host='0.0.0.0'  # ネットワーク内の他のデバイスからもアクセス可能
    )
