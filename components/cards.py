"""
カードコンポーネント
"""
from dash import html
from config import DARK_COLORS, LAYOUT, THRESHOLDS
from components.charts import create_dual_sparkline, get_heatmap_color

def get_performance_color(achievement_rate):
    """達成率に基づいて色を取得"""
    if achievement_rate == 0:
        return DARK_COLORS['text_muted']  # グレー（値が0の場合）
    elif achievement_rate >= THRESHOLDS['good']:
        return DARK_COLORS['success']
    elif achievement_rate >= THRESHOLDS['warning']:
        return DARK_COLORS['warning']
    else:
        return DARK_COLORS['danger']

def get_performance_class(achievement_rate):
    """達成率に基づいてCSSクラスを取得"""
    if achievement_rate == 0:
        return 'neutral'  # グレー（値が0の場合）
    elif achievement_rate >= THRESHOLDS['good']:
        return 'good'
    elif achievement_rate >= THRESHOLDS['warning']:
        return 'warning'
    else:
        return 'danger'

def create_metric_card(title, value, achievement_rate, icon_class="fas fa-chart-line"):
    """メトリクスカードを作成"""
    status_color = get_performance_color(achievement_rate)
    status_class = get_performance_class(achievement_rate)
    
    # ARIA用のラベルを生成
    aria_label = f"{title}: {value}、計画比{round(achievement_rate)}%"
    
    return html.Div([
        html.Div([
            html.Div([
                html.I(className=icon_class, style={
                    'fontSize': '1.2rem',
                    'marginBottom': '8px',
                    'color': DARK_COLORS['primary_orange']
                }),
                html.Div(title, style={
                    'fontSize': '0.75rem',
                    'color': DARK_COLORS['text_muted'],
                    'marginBottom': '4px'
                }),
                html.Div(value, style={
                    'fontSize': '1.5rem',
                    'fontWeight': '700',
                    'color': DARK_COLORS['text_primary']
                }),
            ], style={'flex': '1'}),
            
            html.Div([
                html.Div(f"{round(achievement_rate)}%", style={
                    'padding': '4px 8px',
                    'borderRadius': '6px',
                    'backgroundColor': f"{status_color}20",
                    'color': status_color,
                    'fontSize': '0.875rem',
                    'fontWeight': '600'
                })
            ])
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center'
        })
    ], className=f'metric-card {status_class} animate-fadeIn card-content', 
    **{
        'role': 'figure',
        'aria-label': aria_label
    },
    style={
        'backgroundColor': DARK_COLORS['bg_card'],
        'border': f'1px solid {DARK_COLORS["border_color"]}',
        'borderRadius': LAYOUT['card_radius'],
        'padding': LAYOUT['card_padding'],
        'height': '100%',
        'transition': LAYOUT['transition'],
        'cursor': 'pointer'
    })

def create_performance_card(category, value, achievement_rate, budget_value, trend_data=None, plan_diff=None, show_metrics="both", is_clickable=False, card_id=None, is_selected=False):
    """パフォーマンスカードを作成"""
    status_class = get_performance_class(achievement_rate)
    status_color = get_performance_color(achievement_rate)
    
    # ARIA用のラベルを生成
    aria_label = f"{category}: 実績{value}、計画{budget_value}、計画比{round(achievement_rate)}%"
    
    # 計画差の計算と表示形式の統一
    if plan_diff is None and budget_value:
        try:
            # 実績と計画から数値を抽出（単位を考慮）
            value_str = str(value).replace(',', '').replace('¥', '').replace('円', '').replace('件', '').replace('%', '')
            budget_str = str(budget_value).replace(',', '').replace('¥', '').replace('円', '').replace('件', '').replace('%', '')
            
            # M（百万）やK（千）単位の処理
            if 'M' in value_str:
                actual_num = float(value_str.replace('M', '')) * 1000000
            elif 'K' in value_str or 'k' in value_str:
                actual_num = float(value_str.replace('K', '').replace('k', '')) * 1000
            else:
                actual_num = float(value_str)
                
            if 'M' in budget_str:
                budget_num = float(budget_str.replace('M', '')) * 1000000
            elif 'K' in budget_str or 'k' in budget_str:
                budget_num = float(budget_str.replace('K', '').replace('k', '')) * 1000
            else:
                budget_num = float(budget_str)
                
            plan_diff = actual_num - budget_num
        except (ValueError, TypeError):
            plan_diff = 0
    
    # 計画差の表示用フォーマット
    if plan_diff is not None:
        # 元の単位に合わせてフォーマット
        if abs(plan_diff) >= 1000000:
            plan_diff_text = f"+¥{plan_diff/1000000:.1f}M" if plan_diff >= 0 else f"-¥{abs(plan_diff)/1000000:.1f}M"
        elif abs(plan_diff) >= 1000:
            plan_diff_text = f"+¥{plan_diff/1000:.1f}K" if plan_diff >= 0 else f"-¥{abs(plan_diff)/1000:.1f}K"
        elif '件' in str(value):
            plan_diff_text = f"+{plan_diff:,.0f}件" if plan_diff >= 0 else f"{plan_diff:,.0f}件"
        elif '%' in str(value):
            plan_diff_text = f"+{round(plan_diff)}%" if plan_diff >= 0 else f"{round(plan_diff)}%"
        else:
            plan_diff_text = f"+{plan_diff:,.0f}" if plan_diff >= 0 else f"{plan_diff:,.0f}"
        
        plan_diff_color = DARK_COLORS['success'] if plan_diff >= 0 else DARK_COLORS['danger']
    else:
        plan_diff_text = "-"
        plan_diff_color = DARK_COLORS['text_muted']
    
    # スパークライン作成（縦幅最大化）
    if trend_data and trend_data.get('actual_values') and trend_data.get('budget_values'):
        sparkline = create_dual_sparkline(
            trend_data['actual_values'],
            trend_data['budget_values'],
            achievement_rate,
            height=42,  # スパークライン最適化
            width=75,   # 横幅も若干拡大
            enable_hover=True,
            value_type='number',  # デフォルトは数値
            actual_months=trend_data.get('actual_months')  # 実際のデータがある月数
        )
    else:
        # フォールバック: 静的スパークライン（縦幅最大化）
        sparkline = html.Div([
            html.Div(style={
                'height': '2px',
                'backgroundColor': DARK_COLORS['chart_budget'],
                'borderRadius': '1px',  
                'opacity': 0.6,
                'position': 'absolute',
                'top': '45%',
                'width': '100%'
            }),
            html.Div(style={
                'height': '3px',
                'backgroundColor': status_color,
                'borderRadius': '1px',
                'opacity': 0.9,
                'position': 'absolute',
                'top': '55%',
                'width': f'{min(100, achievement_rate)}%'
            })
        ], style={'width': '100%', 'height': '100%', 'position': 'relative'})
    
    # メトリクス表示の条件分岐
    metrics_display = []
    
    # 上段：項目名と実値（横並び表示）
    metrics_display.append(html.Div([
        html.Div(category, style={
            'fontSize': '0.75rem',
            'fontWeight': '600',
            'color': DARK_COLORS['bg_dark'] if is_selected else DARK_COLORS['text_primary'],
            'marginRight': '8px',
            'flexShrink': '0'
        }),
        html.Div(value, style={
            'fontSize': '1.1rem',
            'fontWeight': '700',
            'color': DARK_COLORS['bg_dark'] if is_selected else DARK_COLORS['text_primary'],
            'lineHeight': '1.2'
        })
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'marginBottom': '4px'
    }))
    
    # 下段：計画比または計画差、計画値（横並び表示）
    if show_metrics == "ratio" or show_metrics == "both":
        metrics_display.append(html.Div([
            html.Div(f"計画比 {round(achievement_rate)}%", style={
                'fontSize': '0.65rem',
                'fontWeight': '600',
                'color': status_color,
                'marginRight': '8px',
                'flexShrink': '0'
            }),
            html.Div(f"計画 {budget_value}", style={
                'fontSize': '0.6rem',
                'fontWeight': '500',
                'color': DARK_COLORS['bg_dark'] if is_selected else DARK_COLORS['text_muted']
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center'
        }))
    elif show_metrics == "diff":
        metrics_display.append(html.Div([
            html.Div(f"計画差 {plan_diff_text}", style={
                'fontSize': '0.65rem',
                'fontWeight': '600',
                'color': plan_diff_color,
                'marginRight': '8px',
                'flexShrink': '0'
            }),
            html.Div(f"計画 {budget_value}", style={
                'fontSize': '0.6rem',
                'fontWeight': '500',
                'color': DARK_COLORS['bg_dark'] if is_selected else DARK_COLORS['text_muted']
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center'
        }))
    
    # カードレイアウト：左側〜中央にメトリクス、右側にスパークライン
    return html.Div([
        html.Div([
            # 左側〜中央：メトリクス表示
            html.Div(metrics_display, style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'space-between',
                'paddingRight': '8px'
            }),
            
            # 右側：スパークライン（カード中央に配置）
            html.Div([
                html.Div([sparkline], style={
                    'height': '100%',
                    'backgroundColor': 'rgba(0,0,0,0.15)',
                    'borderRadius': '4px',
                    'padding': '3px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center'
                })
            ], style={
                'width': '75px',
                'height': '100%',
                'display': 'flex',
                'alignItems': 'center'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'stretch',
            'height': '100%'
        })
    ], 
    **({"id": card_id} if is_clickable and card_id else {}),
    className=f'performance-card {status_class} animate-slideIn card-content',
    **{
        'role': 'figure',
        'aria-label': aria_label + (" (選択中)" if is_selected else "")
    },
    style={
        'backgroundColor': DARK_COLORS['primary_orange'] if is_selected else DARK_COLORS['bg_hover'],
        'border': f'2px solid {DARK_COLORS["primary_orange"]}' if is_selected else f'1px solid {DARK_COLORS["border_color"]}',
        'borderRadius': '8px',
        'padding': '8px 12px',
        'marginBottom': '6px',
        'cursor': 'pointer',
        'transition': LAYOUT['transition'],
        'position': 'relative',
        'minHeight': '48px',
        'display': 'flex',
        'flexDirection': 'column',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)' if is_selected else '0 2px 4px rgba(0,0,0,0.1)',
        'transform': 'translateY(-2px)' if is_selected else 'none'
    })

def create_funnel_stage(stage_data, index, total_stages):
    """ファネルステージを作成（ステージ名なし）"""
    width_percent = 100 - (index * 15)  # 段階的に狭くなる
    
    # 達成率に基づいてボックスの色を設定（ヒートマップカラー）
    achievement_rate = stage_data.get('achievement', 0)
    stage_color = get_performance_color(achievement_rate)
    
    # ARIA用のラベルを生成
    stage_name = stage_data.get('stage', f'ステージ{index+1}')
    aria_label = f"{stage_name}: 実績{stage_data['value']:,}、計画{stage_data.get('budget_value', 'N/A')}、計画比{round(achievement_rate)}%"
    
    return html.Div([
        html.Div([
            html.Div([
                # 実績値と達成率
                html.Div([
                    html.Span(f"{stage_data['value']:,}", style={
                        'fontSize': '1.125rem',
                        'fontWeight': '700',
                        'color': 'white'
                    }),
                    html.Span(
                        f" {round(stage_data['achievement'])}%",
                        style={
                            'fontSize': '0.75rem',
                            'fontWeight': '600',
                            'marginLeft': '8px',
                            'color': 'white'
                        }
                    )
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center'
                }),
                # 計画値
                html.Div(
                    f"計画: {stage_data.get('budget_value', 'N/A'):,}" if stage_data.get('budget_value') != 'N/A' else "計画: N/A",
                    style={
                        'fontSize': '0.625rem',
                        'fontWeight': '400',
                        'color': 'rgba(255, 255, 255, 0.8)',
                        'marginTop': '2px'
                    }
                )
            ], style={
                'textAlign': 'center',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center'
            })
        ], 
        id={'type': 'funnel-stage', 'index': index},
        className='funnel-stage animate-fadeIn',
        **{
            'role': 'figure',
            'aria-label': aria_label
        },
        style={
            'position': 'relative',
            'height': '60px',
            'borderRadius': '8px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'padding': '8px 20px',
            'color': 'white',
            'fontWeight': '600',
            'transition': LAYOUT['transition'],
            'cursor': 'pointer',
            'marginBottom': '8px',
            'width': f"{width_percent}%",
            'backgroundColor': stage_color,
            'margin': '0 auto',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)'
        }),
        
        # コンバージョン率
        html.Div([
            html.I(className="fas fa-arrow-down", style={
                'fontSize': '0.75rem',
                'color': get_performance_color(stage_data.get('conversion_rate', 0) * 5),  # ヒートマップ色
                'marginRight': '4px'
            }),
            html.Span(f"{round(stage_data.get('conversion_rate', 0))}%", style={  # 小数点以下四捨五入
                'color': get_performance_color(stage_data.get('conversion_rate', 0) * 5)  # ヒートマップ色
            })
        ], style={
            'fontSize': '0.875rem',
            'margin': '8px 0',
            'fontWeight': '500',
            'textAlign': 'center'
        }) if index < total_stages - 1 else None
    ], style={'marginBottom': '4px'})

def create_channel_funnel(channel_name, achievement_rate, stages):
    """チャネル別ファネルを作成"""
    status_class = get_performance_class(achievement_rate)
    
    # ARIA用のラベルを生成
    aria_label = f"{channel_name}のファネル分析、全体計画比{round(achievement_rate)}%"
    
    # チャネルヘッダー
    channel_header = html.Div([
        html.Div(channel_name, style={
            'fontSize': '0.875rem',
            'fontWeight': '600',
            'marginBottom': '4px'
        }),
        html.Div(
            f"{round(achievement_rate)}%",
            style={
                'fontSize': '1.25rem',
                'fontWeight': '700',
                'color': get_performance_color(achievement_rate)
            }
        )
    ], className=f'channel-header {status_class}', style={
        'backgroundColor': DARK_COLORS['bg_hover'],
        'padding': '12px',
        'borderRadius': '8px',
        'textAlign': 'center',
        'border': f'1px solid {DARK_COLORS["border_color"]}',
        'marginBottom': '16px'
    })
    
    # ファネルビジュアル
    funnel_visual = html.Div([
        *[create_funnel_stage(stage, i, len(stages)) for i, stage in enumerate(stages)]
    ])
    
    return html.Div([channel_header, funnel_visual], 
        **{
            'role': 'region',
            'aria-label': aria_label
        },
        style={'height': '100%'})

def create_insight_card(insight_type, title, description, impact=None):
    """インサイトカードを作成"""
    type_config = {
        'critical': {
            'icon': 'fas fa-exclamation-triangle',
            'color': DARK_COLORS['danger'],
            'class': 'insight-critical',
            'aria_type': '重要な警告'
        },
        'warning': {
            'icon': 'fas fa-exclamation-circle',
            'color': DARK_COLORS['warning'],
            'class': 'insight-warning',
            'aria_type': '警告'
        },
        'info': {
            'icon': 'fas fa-info-circle',
            'color': DARK_COLORS['secondary_blue'],
            'class': 'insight-info',
            'aria_type': '情報'
        }
    }
    
    config = type_config.get(insight_type, type_config['info'])
    
    # ARIA用のラベルを生成
    aria_label = f"{config['aria_type']}: {title}. {description}"
    if impact:
        aria_label += f" 影響: {impact}"
    
    content = [
        html.Div([
            html.I(className=config['icon'], style={
                'marginRight': '6px',
                'color': config['color']
            }),
            title
        ], style={
            'fontSize': '0.875rem',
            'fontWeight': '600',
            'color': DARK_COLORS['text_primary'],
            'marginBottom': '4px'
        }),
        html.Div(description, style={
            'fontSize': '0.75rem',
            'color': DARK_COLORS['text_secondary'],
            'lineHeight': '1.4'
        })
    ]
    
    if impact:
        content.append(
            html.Div([
                html.I(className="fas fa-chart-line", style={'marginRight': '4px'}),
                impact
            ], style={
                'fontSize': '0.75rem',
                'color': DARK_COLORS['text_muted'],
                'marginTop': '4px'
            })
        )
    
    return html.Div(content, 
        className=f'insight-item {config["class"]} animate-fadeIn',
        **{
            'role': 'alert' if insight_type in ['critical', 'warning'] else 'note',
            'aria-label': aria_label
        },
        style={
            'padding': '12px',
            'backgroundColor': DARK_COLORS['bg_hover'],
            'borderRadius': '8px',
            'borderLeft': f'3px solid {config["color"]}',
            'marginBottom': '8px',
            'transition': LAYOUT['transition']
        }
    )

def create_section_card(title, icon_class, content, height='100%'):
    """セクションカードを作成"""
    # ARIA用のラベルを生成
    aria_label = f"{title}セクション"
    
    return html.Div([
        # ヘッダー
        html.Div([
            html.I(className=icon_class, style={'marginRight': '4px'}),
            html.H3(title, style={
                'fontSize': '0.8rem',
                'fontWeight': '600',
                'color': DARK_COLORS['text_primary'],
                'margin': '0',
                'lineHeight': '1.1'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'backgroundColor': DARK_COLORS['bg_hover'],
            'padding': '6px 8px',
            'borderBottom': f'1px solid {DARK_COLORS["border_color"]}'
        }),
        
        # コンテンツ
        html.Div(content, className='card-content', style={
            'padding': '16px',
            'flex': '1'
        })
    ], 
    **{
        'role': 'region',
        'aria-label': aria_label
    },
    style={
        'backgroundColor': DARK_COLORS['bg_card'],
        'border': f'1px solid {DARK_COLORS["border_color"]}',
        'borderRadius': LAYOUT['card_radius'],
        'display': 'flex',
        'flexDirection': 'column',
        'height': height,
        'overflow': 'hidden'
    })

def make_scroll_card(title, body_id):
    """スクロール可能なカードを作成"""
    from config import DARK_COLORS, LAYOUT
    
    return html.Div([
        html.Div([
            html.Span(title, style={
                'fontSize': '0.8rem',
                'fontWeight': '600',
                'color': DARK_COLORS['text_primary'],
                'margin': '0',
                'lineHeight': '1.1'
            })
        ], className='flex-row items-center card-header',
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
                    'aria-label': f'{title}一覧'
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
        'aria-label': f'{title}セクション'
    },
    style={
        'display': 'flex', 
        'flexDirection': 'column',
        'height': '100%',
        'overflow': 'hidden'
    })

def create_trend_item(channel, volume, cv_rate, volume_trend_data=None, cv_trend_data=None, is_selected=False):
    """経路別CV率トレンドアイテムを作成（タブ2のカードレイアウトと同様）"""
    # CV率の計画値を計算（スパークラインと同じロジックで最新の有効な計画値を取得）
    cv_budget_rate = 0
    if cv_trend_data and cv_trend_data.get('cv_budget_values'):
        cv_budget_values = cv_trend_data['cv_budget_values']
        # 最新の有効な計画値を取得（0より大きい値を逆順検索）
        for val in reversed(cv_budget_values):
            if val > 0:
                cv_budget_rate = val
                break
    
    # CV率の達成率を計算（実績÷計画）
    if cv_budget_rate > 0 and cv_rate > 0:
        achievement_rate = (cv_rate / cv_budget_rate) * 100
    else:
        achievement_rate = 0
    cv_color = get_heatmap_color(achievement_rate)
    performance_class = get_performance_class(achievement_rate)
    
    # ARIA用のラベルを生成
    aria_label = f"{channel}チャネル: CV率{round(cv_rate)}%"
    if is_selected:
        aria_label += " (選択中)"
    
    
    # CV率スパークライン作成
    if cv_trend_data and cv_trend_data.get('volume_actual') and cv_trend_data.get('acq_actual'):
        # CV率の実績値を計算
        cv_actual_values = []
        
        for i in range(len(cv_trend_data.get('volume_actual', []))):
            vol = cv_trend_data.get('volume_actual', [])[i]
            acq = cv_trend_data.get('acq_actual', [])[i]
            if vol > 0:  # 分母があればデータがあると見なす
                cv_rate_val = (acq / vol * 100) if acq > 0 else 0
                cv_actual_values.append(cv_rate_val)
            else:
                cv_actual_values.append(0)
        
        # 実際にCV率データ（分母>0）がある最後の月を探す
        valid_months = 0
        last_valid_index = -1
        for i in range(len(cv_trend_data.get('volume_actual', []))):
            if cv_trend_data.get('volume_actual', [])[i] > 0:
                valid_months = i + 1  # 1ベースのインデックス
                last_valid_index = i
        
        # カード左側の計画値を、最後の有効月の計画値に更新
        if last_valid_index >= 0 and cv_trend_data.get('cv_budget_values'):
            cv_budget_values = cv_trend_data['cv_budget_values']
            if last_valid_index < len(cv_budget_values):
                cv_budget_rate = cv_budget_values[last_valid_index]
                # 達成率を再計算
                if cv_budget_rate > 0 and cv_rate > 0:
                    achievement_rate = (cv_rate / cv_budget_rate) * 100
                else:
                    achievement_rate = 0
        
        sparkline = create_dual_sparkline(
            cv_actual_values,
            cv_trend_data.get('cv_budget_values', []),
            achievement_rate,  # 正しい達成率を使用
            height=42,
            width=120,
            enable_hover=True,
            value_type='percentage',
            actual_months=valid_months  # 実際にデータがある月数を渡す
        )
    else:
        # フォールバック: 静的スパークライン
        sparkline = html.Div([
            html.Div(style={
                'height': '2px',
                'backgroundColor': DARK_COLORS['chart_budget'],
                'borderRadius': '1px',  
                'opacity': 0.6,
                'position': 'absolute',
                'top': '45%',
                'width': '100%'
            }),
            html.Div(style={
                'height': '3px',
                'backgroundColor': cv_color,
                'borderRadius': '1px',
                'opacity': 0.9,
                'position': 'absolute',
                'top': '55%',
                'width': f'{min(100, cv_rate * 10)}%'
            })
        ], style={'width': '100%', 'height': '100%', 'position': 'relative'})
    
    # タブ2のパフォーマンスカードと同じレイアウト構造
    return html.Div([
        html.Div([
            # 左側：メトリクス表示
            html.Div([
                # 上段：経路名と実績値
                html.Div([
                    html.Div(channel, style={
                        'fontSize': '0.75rem',
                        'fontWeight': '600',
                        'color': DARK_COLORS['bg_dark'] if is_selected else DARK_COLORS['text_primary'],
                        'marginRight': '8px',
                        'flexShrink': '0'
                    }),
                    html.Div(f"{round(cv_rate)}%", style={
                        'fontSize': '1.1rem',
                        'fontWeight': '700',
                        'color': DARK_COLORS['bg_dark'] if is_selected else DARK_COLORS['text_primary'],
                        'lineHeight': '1.2'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginBottom': '4px'
                }),
                
                # 下段：達成率と計画値
                html.Div([
                    html.Div(f"計画比: {round(achievement_rate)}%", style={
                        'fontSize': '0.6rem',
                        'fontWeight': '500',
                        'color': DARK_COLORS['bg_dark'] if is_selected else DARK_COLORS['text_muted'],
                        'marginRight': '8px'
                    }),
                    html.Div(f"計画: {round(cv_budget_rate)}%" if cv_budget_rate > 0 else "計画: N/A", style={
                        'fontSize': '0.6rem',
                        'fontWeight': '500',
                        'color': DARK_COLORS['bg_dark'] if is_selected else DARK_COLORS['text_muted']
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center'
                })
            ], style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'space-between',
                'paddingRight': '8px'
            }),
            
            # 右側：スパークライン（カード中央まで拡大）
            html.Div([
                html.Div([sparkline], style={
                    'height': '100%',
                    'backgroundColor': 'rgba(0,0,0,0.15)',
                    'borderRadius': '4px',
                    'padding': '3px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center'
                })
            ], style={
                'width': '120px',
                'height': '100%',
                'display': 'flex',
                'alignItems': 'center'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'stretch',
            'height': '100%'
        })
    ], 
    id={'type': 'trend-card', 'channel': channel},
    className=f'performance-card {performance_class} animate-slideIn',
    **{
        'role': 'figure',
        'aria-label': aria_label
    },
    style={
        'backgroundColor': DARK_COLORS['primary_orange'] if is_selected else DARK_COLORS['bg_hover'],
        'border': f'2px solid {DARK_COLORS["primary_orange"]}' if is_selected else f'1px solid {DARK_COLORS["border_color"]}',
        'borderRadius': '8px',
        'padding': '8px 12px',
        'marginBottom': '6px',
        'cursor': 'pointer',
        'transition': LAYOUT['transition'],
        'position': 'relative',
        'minHeight': '48px',
        'display': 'flex',
        'flexDirection': 'column',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)' if is_selected else '0 2px 4px rgba(0,0,0,0.1)',
        'transform': 'translateY(-2px)' if is_selected else 'none'
    })