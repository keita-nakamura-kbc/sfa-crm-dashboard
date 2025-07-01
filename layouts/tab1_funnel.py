"""
Tab1: ファネル分析レイアウト
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from config import DARK_COLORS, LAYOUT
from components.cards import create_metric_card, create_section_card

def create_funnel_analysis_layout():
    """ファネル分析タブのレイアウト"""
    return html.Div([
        # 上段：ステージ別複合グラフ（30%）
        html.Div([
            html.Div(id='funnel-metrics-bar', 
                className='funnel-metrics-grid grid grid-cols-5 gap-m',
                **{
                    'role': 'region',
                    'aria-label': 'ステージ別メトリクス'
                },
                style={
                    'height': '100%',
                    'maxHeight': '100%',
                    'overflow': 'hidden',
                    'padding': '8px 16px'
                })
        ], 
        className='funnel-top-section',
        style={
            'flex': '0 0 30%',
            'minHeight': '250px',
            'display': 'flex',
            'flexDirection': 'column',
            'boxSizing': 'border-box'
        }),
        
        # 中段・下段（70%）- グリッドレイアウト
        html.Div([
            # 左列：ファネル分析（中段・下段にまたがる）
            html.Div([
                html.Div([
                    html.I(className="fas fa-filter", style={'marginRight': '4px'}),
                    html.H3("ファネル分析", 
                        **{
                            'role': 'heading',
                            'aria-level': '2'
                        },
                        className='text-heading',
                        style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                ], className='flex-row items-center card-header',
                style={
                    'backgroundColor': '#4a5568',  # 複合グラフと同じ色
                    'borderBottom': '1px solid #2d3748',
                    'flexShrink': 0,
                    'padding': '4px',
                    'marginBottom': '2px'
                }),
                
                html.Div(id='funnel-grid', 
                    **{
                        'role': 'region',
                        'aria-label': 'チャネル別ファネル分析'
                    },
                    className='p-m',
                    style={
                        'display': 'grid',
                        'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                        'gap': 'var(--gap-l)',
                        'flex': '1 1 auto',
                        'overflowY': 'auto',
                        'overflowX': 'hidden',
                        'minHeight': '0'
                    })
            ], className='card-base', 
            style={
                'gridArea': 'funnel',
                'display': 'flex',
                'flexDirection': 'column',
                'overflow': 'hidden',
                'minHeight': '0',  # flex item内での縮小を許可
                'minWidth': '0'   # 幅の制約も解除
            }),
            
            # 右上：経路別CV率トレンド
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-chart-line", style={'marginRight': '4px'}),
                        html.H3("経路別CV率トレンド", 
                            **{
                                'role': 'heading',
                                'aria-level': '3'
                            },
                            className='text-subheading flex-1',
                            style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'}),
                        html.Div([
                            html.Span("CV率:", style={
                                'fontSize': '0.7rem',
                                'color': DARK_COLORS['text_muted'],
                                'marginRight': '4px'
                            }),
                            html.Div([
                                dcc.Dropdown(
                                    id='trend-cv-filter',
                                    options=[
                                        {'label': 'to 商談', 'value': '1to2'},
                                        {'label': 'to 具体検討', 'value': '2to3'},
                                        {'label': 'to 内諾', 'value': '3to4'},
                                        {'label': 'to 獲得', 'value': '4to5'}
                                    ],
                                    value='2to3',
                                    style={'width': '120px', 'fontSize': '0.65rem'},
                                    className='dark-dropdown-small'
                                )
                            ], **{
                                'aria-label': 'CV率ステージを選択',
                                'role': 'combobox'
                            })
                        ], className='flex-row items-center')
                    ], className='flex-row items-center card-header',
                    style={
                        'borderBottom': '1px solid #2d3748',
                        'backgroundColor': '#4a5568',  # 複合グラフと同じ色
                        'flexShrink': 0,
                        'padding': '4px',
                        'marginBottom': '2px'
                    }),
                    html.Div(id='channel-trends', 
                        **{
                            'role': 'region',
                            'aria-label': 'チャネル別トレンドリスト'
                        },
                        className='p-m',
                        style={
                            'flex': '1 1 auto',
                            'overflowY': 'auto',
                            'minHeight': '0'
                        })
                ], className='card-base',
                style={
                    'height': '100%',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflow': 'hidden',
                    'minHeight': '0'  # flex item内での縮小を許可
                })
            ], style={
                'gridArea': 'trends',
                'minHeight': '0',  # grid item内での縮小を許可
                'minWidth': '0'   # 幅の制約も解除
            },
            **{
                'role': 'region',
                'aria-label': 'CV率トレンドセクション'
            }),
            
            # 右下：ステージ別CV率トレンド
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-exchange-alt", style={'marginRight': '4px'}),
                        html.H3("ステージ別CV率トレンド", 
                            **{
                                'role': 'heading',
                                'aria-level': '3'
                            },
                            className='text-subheading',
                            style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'}),
                    ], className='flex-row items-center card-header',
                    style={
                        'borderBottom': '1px solid #2d3748',
                        'backgroundColor': '#4a5568',  # 複合グラフと同じ色
                        'flexShrink': 0,
                        'padding': '4px',
                        'marginBottom': '2px'
                    }),
                    html.Div(id='stage-cv-cards', 
                        **{
                            'role': 'region',
                            'aria-label': 'ステージ別CV率カードリスト'
                        },
                        className='p-m',
                        style={
                            'flex': '1 1 auto',
                            'overflowY': 'auto',
                            'minHeight': '0'
                        })
                ], className='card-base',
                style={
                    'height': '100%',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflow': 'hidden',
                    'minHeight': '0'  # flex item内での縮小を許可
                })
            ], style={
                'gridArea': 'stage-trends',
                'minHeight': '0',  # grid item内での縮小を許可
                'minWidth': '0'   # 幅の制約も解除
            },
            **{
                'role': 'region',
                'aria-label': 'ステージ別CV率トレンドセクション'
            })
        ], 
        className='funnel-middle-bottom-section',
        style={
            'flex': '0 0 70%',
            'display': 'grid',
            'gridTemplateColumns': 'minmax(0, 2fr) minmax(0, 1fr)',
            'gridTemplateRows': 'minmax(0, 1fr) minmax(0, 1fr)',
            'gap': '16px',
            'gridTemplateAreas': '"funnel trends" "funnel stage-trends"',
            'padding': '8px 16px',
            'boxSizing': 'border-box',
            'minHeight': '0'
        })
    ], 
    className='funnel-tab-wrapper',
    style={
        'backgroundColor': DARK_COLORS['bg_dark'],
        'height': 'calc(100dvh - var(--header-height))',
        'display': 'flex',
        'flexDirection': 'column',
        'boxSizing': 'border-box',
        'overflow': 'hidden'
    })