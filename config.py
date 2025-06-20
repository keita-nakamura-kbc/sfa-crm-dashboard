"""
SFA/CRM Dashboard Configuration
設定・定数定義ファイル
"""

# ダークテーマカラーパレット
DARK_COLORS = {
    # Primary colors
    'primary_orange': '#ff6b35',
    'primary_dark': '#cc5628',
    'secondary_blue': '#2c5282',
    'accent_gold': '#d69e2e',
    
    # Status colors
    'success': '#48bb78',
    'warning': '#ed8936',
    'danger': '#e53e3e',
    
    # Background colors
    'bg_dark': '#0f1419',
    'bg_card': '#1a202c',
    'bg_hover': '#2d3748',
    
    # Text colors
    'text_primary': '#ffffff',
    'text_secondary': '#cbd5e0',
    'text_muted': '#718096',
    
    # Border colors
    'border_color': '#2d3748',
    'border_light': '#4a5568',
    
    # Chart colors
    'chart_budget': '#94a3b8',  # より明るいグレーブルーに変更
    'chart_actual': '#ff6b35',
    'chart_line': '#2c5282',
    'chart_budget_opacity': 0.6,
    'chart_actual_opacity': 0.8,
    
    # Funnel stage colors (ビジネスライクなトーン - グラデーション)
    'stage_1': '#2d3748',  # ダークグレー
    'stage_2': '#4a5568',  # ミディアムダークグレー
    'stage_3': '#718096',  # ミディアムグレー
    'stage_4': '#a0aec0',  # ライトグレー
    'stage_5': '#ff6b35',  # オレンジ（最終ステージ）
}

# Performance thresholds
THRESHOLDS = {
    'critical': 80,
    'warning': 95,
    'good': 100
}

# レイアウト設定（フルHD最適化）- UIトークンと連動
LAYOUT = {
    'max_width': '1920px',
    'header_height': '48px',
    'padding': '16px',        # var(--gap-m)相当
    'card_radius': '12px',    # var(--radius-l)相当
    'card_padding': '16px',   # var(--gap-m)相当
    'gap': '16px',           # var(--gap-m)相当
    'transition': '0.2s ease',
}

# グラフ設定
CHART_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'sfa_crm_chart',
        'height': 600,
        'width': 1000,
        'scale': 1
    }
}

# Plotlyテンプレート設定
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': DARK_COLORS['bg_card'],
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {
            'family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            'color': DARK_COLORS['text_secondary']
        },
        'margin': dict(l=40, r=40, t=40, b=40),
        'xaxis': {
            'gridcolor': DARK_COLORS['border_color'],
            'showgrid': True,
            'zeroline': False
        },
        'yaxis': {
            'gridcolor': DARK_COLORS['border_color'],
            'showgrid': True,
            'zeroline': False
        }
    }
}

# データマッピング
STAGE_MAPPING = {
    "新規リード数": [102, 121],
    "アプローチ数": [129],
    "商談ステージ": [103, 110, 122, 130],
    "具体検討ステージ": [105, 113, 124, 132],
    "内諾ステージ": [106, 116, 125, 133],
    "新規アプリ獲得数（単月）": [107, 118, 126, 134]
}

INTEGRATED_STAGES = {
    "リード・アプローチ": ["新規リード数", "アプローチ数"],
    "商談": ["商談ステージ"],
    "具体検討": ["具体検討ステージ"],
    "内諾": ["内諾ステージ"],
    "獲得": ["新規アプリ獲得数（単月）"]
}

# Excelファイル構造
EXCEL_STRUCTURE = {
    'sheet_name': '25年PDCA',
    'sections': {
        'sales': (4, 34),
        'acquisition': (37, 63),
        'unit_price': (65, 91),
        'retention': (93, 98),
        'indicators': (101, 135)
    },
    'col_ranges': {
        'plan_diff': (2, 14),
        'plan_ratio': (20, 32),
        'actual': (38, 49),
        'budget': (56, 68)
    }
}

# CSS animations
ANIMATIONS = """
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { transform: translateX(-10px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.animate-fadeIn {
    animation: fadeIn 0.3s ease-out;
}

.animate-slideIn {
    animation: slideIn 0.3s ease-out;
}

.animate-pulse {
    animation: pulse 2s infinite;
}
"""