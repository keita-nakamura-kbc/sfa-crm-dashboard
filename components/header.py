"""
ヘッダーコンポーネント
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from config import DARK_COLORS, LAYOUT
from .loading import create_inline_loading_text

def create_header():
    """ヘッダーコンポーネントを作成"""
    return html.Div([
        # ヘッダーとタブを含むコンテナ
        html.Div([
            # 上段：ヘッダー
            html.Div([
                # ロゴまたはタイトル
                html.Div([
                    html.H4("SFA/CRM Analytics", 
                        **{
                            'role': 'heading',
                            'aria-level': '1'
                        },
                        style={
                            'margin': '0',
                            'color': DARK_COLORS['text_primary'],
                            'fontSize': '1rem',
                            'fontWeight': '600',
                            'lineHeight': '1.2'
                        }),
                ], style={'display': 'flex', 'alignItems': 'center'}),
                
                # コントロールパネル
                html.Div([
                    # データアップロード
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            html.I(className="fas fa-upload", style={'marginRight': '8px'}),
                            'データ更新'
                        ], 
                        **{
                            'role': 'button',
                            'aria-label': 'Excelファイルをアップロードしてデータを更新'
                        },
                        style={
                            'background': 'transparent',
                            'border': f'1px solid {DARK_COLORS["border_light"]}',
                            'color': DARK_COLORS['text_secondary'],
                            'padding': '4px 8px',
                            'borderRadius': '6px',
                            'fontSize': '0.8rem',
                            'cursor': 'pointer',
                            'transition': LAYOUT['transition'],
                            'display': 'inline-flex',
                            'alignItems': 'center'
                        }),
                        style={'marginRight': '12px'},
                        multiple=False
                    ),
                    
                    # 月選択
                    html.Div([
                        dcc.Dropdown(
                            id='month-selector',
                            options=[],
                            value=None,
                            placeholder="対象月",
                            style={
                                'width': '100px',
                                'fontSize': '0.8rem'
                            },
                            className='dark-dropdown'
                        )
                    ], **{
                        'aria-label': '対象月を選択',
                        'role': 'combobox'
                    }, style={'marginRight': '12px'}),
                    
                    # 計画比/計画差切り替え
                    html.Div([
                        html.Button('計画比', id='btn-plan-ratio', className='control-button active', 
                                   style={'marginRight': '4px'},
                                   **{'aria-label': '計画比表示に切り替え', 'aria-pressed': 'true'}),
                        html.Button('計画差', id='btn-plan-diff', className='control-button',
                                   **{'aria-label': '計画差表示に切り替え', 'aria-pressed': 'false'})
                    ], style={'marginRight': '12px'},
                    **{'role': 'group', 'aria-label': '表示モードの選択'}),
                    
                    # 累月/単月切り替え
                    html.Div([
                        html.Button('累月', id='btn-cumulative', className='control-button active',
                                   style={'marginRight': '4px'},
                                   **{'aria-label': '累計表示に切り替え', 'aria-pressed': 'true'}),
                        html.Button('単月', id='btn-single', className='control-button',
                                   **{'aria-label': '単月表示に切り替え', 'aria-pressed': 'false'})
                    ], style={'marginRight': '12px'},
                    **{'role': 'group', 'aria-label': '期間タイプの選択'}),
                    
                    # 獲得/売上切り替え（Tab2専用）
                    html.Div([
                        html.Button('獲得', id='btn-acquisition', className='control-button active',
                                   style={'marginRight': '4px'},
                                   **{'aria-label': '獲得分析に切り替え', 'aria-pressed': 'true'}),
                        html.Button('売上', id='btn-revenue', className='control-button',
                                   **{'aria-label': '売上分析に切り替え', 'aria-pressed': 'false'})
                    ], id='acquisition-revenue-toggle-container', 
                    style={'marginRight': '12px', 'display': 'none'},  # 初期は非表示（Tab1では不要）
                    **{'role': 'group', 'aria-label': '分析タイプの選択'}),
                    
                    # 経路フィルタ（タブ1専用）
                    html.Div([
                        dcc.Dropdown(
                            id='channel-filter-tab1',
                            options=[],
                            value=None,
                            placeholder="経路",
                            style={
                                'width': '80px',
                                'fontSize': '0.8rem'
                            },
                            className='dark-dropdown'
                        )
                    ], id='channel-filter-tab1-container',
                    **{
                        'aria-label': '経路フィルタを選択',
                        'role': 'combobox'
                    }, 
                    style={'marginRight': '12px', 'display': 'none'}),  # 初期は非表示
                    
                    # 経路フィルタ（タブ2専用）
                    html.Div([
                        dcc.Dropdown(
                            id='channel-filter-tab2',
                            options=[],
                            value=None,
                            placeholder="経路",
                            style={
                                'width': '80px',
                                'fontSize': '0.8rem'
                            },
                            className='dark-dropdown'
                        )
                    ], id='channel-filter-tab2-container',
                    **{
                        'aria-label': '経路フィルタを選択',
                        'role': 'combobox'
                    }, 
                    style={'marginRight': '8px', 'display': 'none'}),  # 初期は非表示
                    
                    # プランフィルタ（タブ2専用）
                    html.Div([
                        dcc.Dropdown(
                            id='plan-filter-tab2',
                            options=[],
                            value=None,
                            placeholder="アプリ",
                            style={
                                'width': '80px',
                                'fontSize': '0.8rem'
                            },
                            className='dark-dropdown'
                        )
                    ], id='plan-filter-tab2-container',
                    **{
                        'aria-label': 'アプリフィルタを選択',
                        'role': 'combobox'
                    }, 
                    style={'marginRight': '24px', 'display': 'none'}),  # 初期は非表示
                    
                    # 最終更新時刻（ローディング表示対応）
                    html.Div(id='last-update-container',
                        children=html.Span(id='last-update', 
                            **{
                                'role': 'status',
                                'aria-live': 'polite',
                                'aria-label': '最終更新時刻'
                            },
                            style={
                                'color': DARK_COLORS['text_muted'],
                                'fontSize': '0.75rem'
                            }),
                        style={
                            'marginLeft': 'auto',
                            'marginRight': '20px'
                        }),
                    
                    # タブボタン（右上に配置）
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-filter", style={'marginRight': '6px'}),
                            'ファネル分析'
                        ], id='tab-1-button', className='tab-button active',
                        **{
                            'aria-label': 'ファネル分析タブに切り替え',
                            'aria-current': 'page'
                        },
                        style={
                            'background': DARK_COLORS['primary_orange'],
                            'border': 'none',
                            'color': DARK_COLORS['text_primary'],
                            'padding': '4px 8px',
                            'borderRadius': '6px',
                            'fontSize': '0.7rem',
                            'fontWeight': '500',
                            'cursor': 'pointer',
                            'marginRight': '4px'
                        }),
                        
                        html.Button([
                            html.I(className="fas fa-chart-line", style={'marginRight': '6px'}),
                            '売上・獲得分析'
                        ], id='tab-2-button', className='tab-button',
                        **{
                            'aria-label': '売上・獲得分析タブに切り替え',
                            'aria-current': 'false'
                        },
                        style={
                            'background': 'transparent',
                            'border': f'1px solid {DARK_COLORS["border_light"]}',
                            'color': DARK_COLORS['text_secondary'],
                            'padding': '4px 8px',
                            'borderRadius': '6px',
                            'fontSize': '0.7rem',
                            'fontWeight': '500',
                            'cursor': 'pointer'
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'},
                    **{'role': 'tablist', 'aria-label': 'タブナビゲーション'}),
                    
                    # フィルタ（非表示）
                    dcc.Dropdown(
                        id='channel-filter',
                        options=[],
                        value=[],
                        multi=True,
                        placeholder="経路",
                        style={'display': 'none'}
                    ),
                    
                    dcc.Dropdown(
                        id='plan-filter',
                        options=[],
                        value=[],
                        multi=True,
                        placeholder="プラン",
                        style={'display': 'none'}
                    ),
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'flex': '1'
                }),
            ], 
            **{
                'role': 'banner'
            },
            style={
                'background': DARK_COLORS['bg_card'],
                'borderBottom': f'1px solid {DARK_COLORS["border_color"]}',
                'padding': '6px 16px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'height': '48px'  # ヘッダー高さを最適化
            })
        ])
    ], style={
        'position': 'sticky',
        'top': '0',
        'zIndex': '1000'
    })