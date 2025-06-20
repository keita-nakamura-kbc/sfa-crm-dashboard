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

# Plotly軽量化設定
PLOTLY_CONFIG = {
    'displayModeBar': False,      # ツールバー非表示
    'staticPlot': False,          # インタラクティブ維持
    'scrollZoom': False,          # ズーム無効
    'doubleClick': False,         # ダブルクリック無効  
    'showTips': False,            # チップ無効
    'responsive': True,           # レスポンシブ維持
    'toImageButtonOptions': {
        'format': 'svg',          # 軽量フォーマット
        'width': None,
        'height': None
    },
    'modeBarButtonsToRemove': [   # 不要なボタン削除
        'pan2d', 'lasso2d', 'select2d', 'autoScale2d', 
        'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian'
    ]
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

# データポイント最適化関数
def optimize_chart_data(df, max_points=50):
    """データポイント数を制限（視覚的品質維持）"""
    if df is None or df.empty:
        return df
    if len(df) > max_points:
        step = max(1, len(df) // max_points)
        return df.iloc[::step]
    return df

# CSS animations - 軽量版
ANIMATIONS = """
/* 軽量アニメーション - GPU最適化 */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.animate-fadeIn {
    animation: fadeIn 0.2s ease-out;
    will-change: opacity;
}
"""