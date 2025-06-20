"""
Tab2: 売上・獲得分析レイアウト（新構成）
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from config import DARK_COLORS, LAYOUT
from components.cards import create_section_card, make_scroll_card

def create_revenue_acquisition_layout():
    """売上・獲得分析タブのレイアウト（新構成）"""
    return html.Div([
        # 左半分と右半分の構成
        html.Div([
            # 左半分
            html.Div([
                # 左半分-上半分: メイントレンドチャート（60%）
                html.Div([
                    html.Div([
                        html.H3(id='main-trend-title', 
                            **{
                                'role': 'heading',
                                'aria-level': '2'
                            },
                            className='text-heading',
                            style={'margin': '0', 'fontSize': '0.9rem', 'lineHeight': '1.2'}),
                        html.Div(id='main-trend-kpi-summary', 
                            className='flex-row items-center gap-m')
                    ], className='flex-row justify-between items-center',
                    style={
                        'borderBottom': f'1px solid {DARK_COLORS["border_color"]}',
                        'marginBottom': '4px',
                        'paddingBottom': '4px'
                    }),
                    
                    html.Div([
                        dcc.Graph(id='main-trend-chart', 
                                 style={'height': '100%', 'minHeight': '0'},
                                 config={'displayModeBar': False, 'responsive': True})
                    ], **{
                        'aria-label': 'メイントレンドグラフ',
                        'role': 'img'
                    }, style={'height': 'calc(100% - 35px)', 'flexGrow': 1})
                ], 
                className='plan-card section-card',
                style={
                    'backgroundColor': DARK_COLORS['bg_card'],
                    'borderRadius': LAYOUT['card_radius'],
                    'padding': LAYOUT['card_padding'],
                    'height': '60%',
                    'display': 'flex',
                    'flexDirection': 'column'
                }),
                
                # 左半分-下半分: 左右に分かれた4つの小セクション（40%）
                html.Div([
                    # 左半分: 継続率と客単価分析（横並び）
                    html.Div([
                        # 継続率
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-sync-alt", style={'marginRight': '4px'}),
                                html.H3("継続率", 
                                    **{
                                        'role': 'heading',
                                        'aria-level': '3'
                                    },
                                    className='text-subheading',
                                    style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                            ], className='flex-row items-center card-header',
                            style={
                                'backgroundColor': '#4a5568',  # タブ1と同じタイトルバー色
                                'borderBottom': '1px solid #2d3748',
                                'flexShrink': 0,
                                'padding': '4px',
                                'marginBottom': '2px'
                            }),
                            html.Div(id='retention-rate-cards',
                                    className='p-m',
                                    style={
                                        'flex': '1 1 auto',
                                        'overflowY': 'auto',
                                        'minHeight': '0'
                                    })
                        ], 
                        className='card-base',
                        style={
                            'height': '100%',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'flex': '1',
                            'overflow': 'hidden'
                        }),
                        
                        # 客単価分析
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-yen-sign", style={'marginRight': '4px'}),
                                html.H3("客単価分析", 
                                    **{
                                        'role': 'heading',
                                        'aria-level': '3'
                                    },
                                    className='text-subheading',
                                    style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                            ], className='flex-row items-center card-header',
                            style={
                                'backgroundColor': '#4a5568',  # タブ1と同じタイトルバー色
                                'borderBottom': '1px solid #2d3748',
                                'flexShrink': 0,
                                'padding': '4px',
                                'marginBottom': '2px'
                            }),
                            html.Div(id='unit-price-analysis-cards',
                                    className='p-m',
                                    style={
                                        'flex': '1 1 auto',
                                        'overflowY': 'auto',
                                        'minHeight': '0'
                                    })
                        ], 
                        className='card-base',
                        style={
                            'height': '100%',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'flex': '1',
                            'overflow': 'hidden'
                        })
                    ], style={
                        'display': 'flex',
                        'flexDirection': 'row',
                        'gap': '8px',
                        'height': '100%',
                        'flex': '2'
                    }),
                    
                    # 右半分: 構成チャート（縦並び）
                    html.Div([
                        # 構成（経路別）- 動的タイトル
                        html.Div([
                            html.Div(id='composition-channel-title', 
                                className='card-header',
                                style={
                                    'textAlign': 'center',
                                    'fontSize': '0.7rem',
                                    'fontWeight': '600',
                                    'color': DARK_COLORS['text_primary'],
                                    'padding': '2px',
                                    'margin': '0',
                                    'backgroundColor': '#4a5568',  # タブ1と同じタイトルバー色
                                    'borderBottom': '1px solid #2d3748'
                                }
                            ),
                            html.Div([
                                dcc.Graph(id='composition-channel-chart',
                                         style={'height': '100%', 'minHeight': '0'},
                                         config={'displayModeBar': False, 'responsive': True})
                            ], className='p-m', style={'flex': '1 1 auto', 'minHeight': '0'})
                        ], 
                        className='card-base',
                        style={
                            'height': '100%',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'flex': '1',
                            'overflow': 'hidden'
                        }),
                        
                        # 構成（アプリ別）- 動的タイトル
                        html.Div([
                            html.Div(id='composition-app-title', 
                                className='card-header',
                                style={
                                    'textAlign': 'center',
                                    'fontSize': '0.7rem',
                                    'fontWeight': '600',
                                    'color': DARK_COLORS['text_primary'],
                                    'padding': '2px',
                                    'margin': '0',
                                    'backgroundColor': '#4a5568',  # タブ1と同じタイトルバー色
                                    'borderBottom': '1px solid #2d3748'
                                }
                            ),
                            html.Div([
                                dcc.Graph(id='composition-app-chart',
                                         style={'height': '100%', 'minHeight': '0'},
                                         config={'displayModeBar': False, 'responsive': True})
                            ], className='p-m', style={'flex': '1 1 auto', 'minHeight': '0'})
                        ], 
                        className='card-base',
                        style={
                            'height': '100%',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'flex': '1',
                            'overflow': 'hidden'
                        })
                    ], style={
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '8px',
                        'height': '100%',
                        'flex': '2'
                    })
                ], 
                style={
                    'display': 'flex',
                    'flexDirection': 'row',
                    'gap': '16px',
                    'height': '40%'
                })
            ], 
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '16px',
                'height': '100%'
            }),
            
            # 右半分
            html.Div([
                # 右半分-左半分: 経路別カード
                make_scroll_card_with_dynamic_title("経路別カード", "channel-cards", "detail-channel-title"),
                
                # 右半分-右半分: プラン別カード
                make_scroll_card_with_dynamic_title("プラン別カード", "plan-cards", "detail-plan-title")
            ], 
            style={
                'display': 'grid',
                'gridTemplateColumns': '1fr 1fr',
                'gap': '16px',
                'height': '100%'
            })
        ], 
        style={
            'display': 'grid',
            'gridTemplateColumns': '1fr 1fr',
            'gap': '16px',
            'height': '100%',
            'padding': '16px'
        })
    ], 
    className='revenue-tab-wrapper',
    style={
        'backgroundColor': DARK_COLORS['bg_dark'],
        'height': 'calc(100dvh - var(--header-height))',
        'boxSizing': 'border-box',
        'overflow': 'hidden'
    })

def make_scroll_card_with_dynamic_title(default_title, body_id, title_id):
    """動的タイトル付きスクロールカードを作成（一体型タイトルバー）"""
    return html.Div([
        html.Div(id=title_id, children=default_title, 
                className='flex-row items-center card-header',
                style={
                    'backgroundColor': '#4a5568',  # タブ1と同じタイトルバー色
                    'borderBottom': '1px solid #2d3748',
                    'flexShrink': 0,
                    'padding': '4px',
                    'marginBottom': '2px'
                }),
        html.Div(id=body_id, 
                className='p-m',
                **{
                    'role': 'region',
                    'aria-label': f'{default_title}一覧'
                },
                style={
                    'flex': '1 1 auto',
                    'overflowY': 'auto',
                    'minHeight': '0'
                })
    ], 
    className='card-base',
    **{
        'role': 'region',
        'aria-label': f'{default_title}セクション'
    },
    style={
        'height': '100%',
        'display': 'flex',
        'flexDirection': 'column',
        'overflow': 'hidden'
    })