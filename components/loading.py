"""
Static Loading Components
軽量でRender無料プラン対応のローディング表示
"""
from dash import html, dcc
from config import DARK_COLORS

def create_loading_overlay(loading_text="データを読み込み中..."):
    """
    静的ローディングオーバーレイを作成
    軽量でCPU使用量を抑えた実装
    """
    return html.Div([
        html.Div([
            html.Div([
                # 静的ローディングアイコン
                html.Div("⏳", style={
                    'fontSize': '32px',
                    'marginBottom': '12px',
                    'textAlign': 'center'
                }),
                html.Div(loading_text, style={
                    'fontSize': '14px',
                    'color': DARK_COLORS['text_secondary'],
                    'textAlign': 'center'
                })
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'center',
                'backgroundColor': DARK_COLORS['bg_card'],
                'padding': '24px',
                'borderRadius': '8px',
                'border': f"1px solid {DARK_COLORS['border_color']}"
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'height': '100%',
            'width': '100%'
        })
    ], style={
        'position': 'absolute',
        'top': '0',
        'left': '0',
        'right': '0',
        'bottom': '0',
        'backgroundColor': 'rgba(26, 32, 44, 0.8)',
        'zIndex': '9999',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center'
    }, id='loading-overlay')

def create_skeleton_card():
    """
    カード用スケルトンローダー（静的）
    """
    return html.Div([
        # タイトル部分のスケルトン
        html.Div(style={
            'height': '20px',
            'backgroundColor': DARK_COLORS['border_color'],
            'borderRadius': '4px',
            'marginBottom': '12px',
            'width': '60%'
        }),
        # コンテンツ部分のスケルトン
        html.Div([
            html.Div(style={
                'height': '16px',
                'backgroundColor': DARK_COLORS['border_color'],
                'borderRadius': '4px',
                'marginBottom': '8px',
                'width': '100%'
            }),
            html.Div(style={
                'height': '16px',
                'backgroundColor': DARK_COLORS['border_color'],
                'borderRadius': '4px',
                'marginBottom': '8px',
                'width': '80%'
            }),
            html.Div(style={
                'height': '16px',
                'backgroundColor': DARK_COLORS['border_color'],
                'borderRadius': '4px',
                'width': '70%'
            })
        ])
    ], style={
        'padding': '16px',
        'backgroundColor': DARK_COLORS['bg_card'],
        'border': f"1px solid {DARK_COLORS['border_color']}",
        'borderRadius': '8px',
        'height': '120px'
    })

def create_chart_loading_placeholder():
    """
    チャート用ローディングプレースホルダー（静的）
    """
    return html.Div([
        html.Div([
            html.Div("📊", style={
                'fontSize': '48px',
                'textAlign': 'center',
                'marginBottom': '16px',
                'opacity': '0.6'
            }),
            html.Div("チャートを準備中...", style={
                'fontSize': '14px',
                'color': DARK_COLORS['text_secondary'],
                'textAlign': 'center'
            })
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'alignItems': 'center',
            'justifyContent': 'center',
            'height': '100%'
        })
    ], style={
        'backgroundColor': DARK_COLORS['bg_card'],
        'border': f"1px dashed {DARK_COLORS['border_color']}",
        'borderRadius': '8px',
        'minHeight': '300px',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center'
    })

def create_inline_loading_text(text="読み込み中..."):
    """
    インライン用ローディングテキスト（静的）
    """
    return html.Span([
        html.Span("●", style={
            'color': DARK_COLORS['primary_orange'],
            'marginRight': '8px',
            'fontSize': '12px'
        }),
        html.Span(text, style={
            'color': DARK_COLORS['text_secondary'],
            'fontSize': '12px'
        })
    ], style={
        'display': 'inline-flex',
        'alignItems': 'center'
    })

def create_section_loading_state():
    """
    セクション全体のローディング状態（静的）
    """
    return html.Div([
        html.Div([
            create_skeleton_card(),
            html.Div(style={'height': '12px'}),  # スペーサー
            create_skeleton_card(),
            html.Div(style={'height': '12px'}),  # スペーサー
            create_chart_loading_placeholder()
        ])
    ], style={
        'padding': '16px',
        'backgroundColor': DARK_COLORS['bg_card'],
        'border': f"1px solid {DARK_COLORS['border_color']}",
        'borderRadius': '8px',
        'opacity': '0.8'
    })