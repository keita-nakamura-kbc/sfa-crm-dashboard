"""
チャートコンポーネント
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import DARK_COLORS, PLOTLY_TEMPLATE, CHART_CONFIG

def with_a11y(fig, description, chart_type="chart"):
    """グラフにアクセシビリティメタデータを追加
    
    Args:
        fig: Plotly図表オブジェクト
        description: 代替説明テキスト
        chart_type: チャートタイプ（chart, trend, funnel, comparison等）
    
    Returns:
        アクセシビリティメタデータ付きのfig
    """
    # スクリーンリーダー用の代替説明
    fig.update_layout(
        meta={
            "description": description,
            "type": chart_type,
            "accessible": True
        }
    )
    
    # レンダリング後のDOMにaria-label属性が追加されるよう設定
    if hasattr(fig, 'layout') and hasattr(fig.layout, 'title'):
        current_title = fig.layout.title.text if fig.layout.title and fig.layout.title.text else ""
        # 既存の透明タイトルを保持しつつ、aria用の情報を追加
        if "color: transparent;" in str(current_title):
            # 既存の透明タイトルはそのまま保持
            pass
        else:
            # 新しく透明タイトルを設定
            fig.update_layout(
                title={
                    'text': f'<span style="font-size: 1px; color: transparent;">{description}</span>',
                    'font': {'size': 1},
                    'xref': 'paper',
                    'x': 0
                }
            )
    
    return fig

def get_achievement_color(achievement_rate, stage_index):
    """達成率とステージに応じた色を取得"""
    # ベースとなるステージ色を取得
    base_color = DARK_COLORS.get(f'stage_{stage_index+1}', DARK_COLORS.get('stage_5', '#4A90E2'))
    
    # 達成率に応じて透明度や色を調整
    if achievement_rate >= 0.9:  # 90%以上
        return base_color  # フル色
    elif achievement_rate >= 0.7:  # 70%以上
        return f"{base_color}CC"  # 80%透明度
    elif achievement_rate >= 0.5:  # 50%以上
        return f"{base_color}99"  # 60%透明度
    elif achievement_rate >= 0.3:  # 30%以上
        return f"{base_color}66"  # 40%透明度
    else:  # 30%未満
        return f"{base_color}33"  # 20%透明度

def get_heatmap_color(achievement_rate):
    """計画比に応じた5段階ヒートマップ色を取得（コントラスト改善版）"""
    if achievement_rate == 0:
        return '#6b7280'  # グレー（値が0の場合）- より明るく
    elif achievement_rate >= 120:
        return '#059669'  # 深い緑 - コントラスト向上
    elif achievement_rate >= 110:
        return '#65a30d'  # 濃い明るい緑 - コントラスト向上
    elif achievement_rate >= 100:
        return '#d97706'  # 濃い黄色 - コントラスト向上
    elif achievement_rate >= 90:
        return '#ea580c'  # 濃いオレンジ - コントラスト向上
    else:
        return '#b91c1c'  # 濃い赤 - コントラスト向上

def create_empty_chart(message="データなし"):
    """空のチャートを作成"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=14, color=DARK_COLORS['text_muted'])
    )
    layout_config = PLOTLY_TEMPLATE['layout'].copy()
    layout_config['title'] = {
        'text': '',
        'font': {'size': 1},
        'xref': 'paper',
        'x': 0
    }
    fig.update_layout(**layout_config)
    # アクセシビリティ用の説明を追加
    fig.update_layout(
        annotations=[{
            'text': message,
            'x': 0.5, 'y': 0.5,
            'xref': 'paper', 'yref': 'paper',
            'showarrow': False,
            'font': dict(size=14, color=DARK_COLORS['text_muted']),
            'name': 'empty-chart-message'
        }]
    )
    return with_a11y(fig, f"空のグラフ: {message}", "empty")

def create_trend_chart(months, budget_values, actual_values, actual_months, 
                      achievement_rates=None, selected_month=None, value_type='currency', height=None, data_type='plan_ratio'):
    """トレンドチャートを作成"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # ARIA用のタイトルを設定
    chart_title = '売上高推移' if value_type == 'currency' else '獲得数推移'
    
    # 計画バー（背景、太い、薄い）
    fig.add_trace(
        go.Bar(
            x=months,
            y=budget_values,
            name='計画',
            marker=dict(
                color=DARK_COLORS['chart_budget'],
                opacity=DARK_COLORS['chart_budget_opacity']
            ),
            width=0.8,
            hovertemplate='計画: ' + ('¥%{y:,.0f}' if value_type == 'currency' else '%{y:,.0f}') + '<extra></extra>',
            showlegend=False
        ),
        secondary_y=False
    )
    
    # 実績バー（前景、細い、オレンジ）
    if actual_months and actual_values:
        # 当月のバーを特別に色付け
        marker_colors = [
            DARK_COLORS['danger'] if month == selected_month else DARK_COLORS['chart_actual']
            for month in actual_months
        ]
        
        fig.add_trace(
            go.Bar(
                x=actual_months,
                y=actual_values,
                name='実績',
                marker=dict(
                    color=marker_colors,
                    opacity=DARK_COLORS['chart_actual_opacity']
                ),
                width=0.4,
                hovertemplate='実績: ' + ('¥%{y:,.0f}' if value_type == 'currency' else '%{y:,.0f}') + '<extra></extra>',
                showlegend=False
            ),
            secondary_y=False
        )
        
        # 達成率ライン（計画比の場合）
        if achievement_rates and data_type == 'plan_ratio':
            heatmap_colors = [get_heatmap_color(rate) for rate in achievement_rates]
            
            fig.add_trace(
                go.Scatter(
                    x=actual_months,
                    y=achievement_rates,
                    mode='lines+markers',
                    name='計画比',
                    line=dict(color=DARK_COLORS['chart_line'], width=3),
                    marker=dict(
                        size=8,
                        color=heatmap_colors,
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate='計画比: %{y:.1f}%<extra></extra>',
                    showlegend=False
                ),
                secondary_y=True
            )
            
            fig.update_yaxes(
                title_text="",
                secondary_y=True,
                tickformat='.0f',
                ticksuffix='%',
                gridcolor=DARK_COLORS['border_color']
            )
        
        # 計画差ライン（計画差の場合）
        elif data_type == 'plan_diff' and actual_values and budget_values:
            # 計画差を計算（実績 - 計画）
            plan_diff_values = []
            plan_diff_months = []
            
            for i, month in enumerate(actual_months):
                if month in months:
                    budget_index = months.index(month)
                    if budget_index < len(budget_values):
                        diff_value = actual_values[i] - budget_values[budget_index]
                        plan_diff_values.append(diff_value)
                        plan_diff_months.append(month)
            
            if plan_diff_values:
                # 差分の色付け（プラスは緑、マイナスは赤）
                diff_colors = ['#48bb78' if val >= 0 else '#e53e3e' for val in plan_diff_values]
                
                fig.add_trace(
                    go.Scatter(
                        x=plan_diff_months,
                        y=plan_diff_values,
                        mode='lines+markers',
                        name='計画差',
                        line=dict(color=DARK_COLORS['chart_line'], width=3),
                        marker=dict(
                            size=8,
                            color=diff_colors,
                            line=dict(width=1, color='white')
                        ),
                        hovertemplate='計画差: ' + ('¥%{y:,.0f}' if value_type == 'currency' else '%{y:,.0f}') + '<extra></extra>',
                        showlegend=False
                    ),
                    secondary_y=True
                )
                
                fig.update_yaxes(
                    title_text="",
                    secondary_y=True,
                    tickformat=',.0f',
                    ticksuffix='円' if value_type == 'currency' else '件',
                    gridcolor=DARK_COLORS['border_color']
                )
    
    # レイアウト更新
    layout_config = PLOTLY_TEMPLATE['layout'].copy()
    layout_config.update({
        'barmode': 'overlay',
        'showlegend': False,
        'height': None,  # 高さをCSSで制御するためNoneに設定
        'autosize': True,
        'margin': dict(l=40, r=20, t=20, b=40),
        'title': {
            'text': f'<span style="font-size: 1px; color: transparent;">{chart_title}グラフ</span>',
            'font': {'size': 1},
            'xref': 'paper',
            'x': 0
        }
    })
    fig.update_layout(**layout_config)
    
    fig.update_xaxes(gridcolor=DARK_COLORS['border_color'])
    fig.update_yaxes(
        title_text='売上高（円）' if value_type == 'currency' else '獲得数',
        secondary_y=False,
        tickformat=',.0f',
        gridcolor=DARK_COLORS['border_color']
    )
    
    # アクセシビリティ説明の生成
    description = f"{chart_title}。計画と実績の推移を月別に表示。"
    if achievement_rates:
        description += "計画比も右軸に表示。"
    if selected_month:
        description += f"現在選択中: {selected_month}"
    
    return with_a11y(fig, description, "trend")

def create_mini_bar_chart(values, max_height=100, enable_hover=True):
    """ミニ棒グラフを作成（KPIカード用）"""
    fig = go.Figure()
    
    # 最新12個のデータ
    recent_values = values[-12:] if len(values) > 12 else values
    
    # ARIA用のタイトルを設定
    aria_title = 'トレンドチャート'
    
    # 月のラベルを生成
    month_labels = [f"{i+1}月" for i in range(len(recent_values))]
    
    fig.add_trace(
        go.Bar(
            x=month_labels,
            y=recent_values,
            marker=dict(
                color=DARK_COLORS['primary_orange'],
                opacity=0.6
            ),
            hovertemplate='<span style="color: white;"><b>%{x}</b><br>%{y:,.0f}</span><extra></extra>' if enable_hover else None,
            hoverinfo='text' if enable_hover else 'none'
        )
    )
    
    fig.update_layout(
        height=None,
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(
            visible=False,
            fixedrange=True
        ),
        yaxis=dict(
            visible=False,
            fixedrange=True
        ),
        hovermode='closest' if enable_hover else False,
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="rgba(255,255,255,0.2)",
            font_color="white",
            font_size=12
        ) if enable_hover else None,
        title={
            'text': f'<span style="font-size: 1px; color: transparent;">{aria_title}</span>',
            'font': {'size': 1},
            'xref': 'paper',
            'x': 0
        }
    )
    
    description = f"ミニ棒グラフ。直近{len(recent_values)}期間のトレンドを表示。"
    return with_a11y(fig, description, "mini-bar")

def create_horizontal_bar_chart(categories, values, colors=None, height=None, chart_type='retention'):
    """水平棒グラフを作成（継続率・客単価分析用）"""
    if colors is None:
        colors = [get_heatmap_color(val) for val in values]
    
    # ARIA用のタイトルを設定
    aria_title = '継続率分析' if chart_type == 'retention' else '客単価分析'
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=values,
            y=categories,
            orientation='h',
            marker=dict(
                color=colors,
                opacity=0.8
            ),
            text=[f'{val:.1f}%' for val in values],
            textposition='outside',
            textfont=dict(
                color=DARK_COLORS['text_secondary'],
                size=12
            ),
            hovertemplate='%{y}: %{x:.1f}%<extra></extra>'
        )
    )
    
    layout_config = PLOTLY_TEMPLATE['layout'].copy()
    layout_config.update({
        'height': None,
        'autosize': True,
        'showlegend': False,
        'title': {
            'text': f'<span style="font-size: 1px; color: transparent;">{aria_title}グラフ</span>',
            'font': {'size': 1},
            'xref': 'paper',
            'x': 0
        }
    })
    fig.update_layout(**layout_config)
    
    fig.update_xaxes(
        visible=False,
        range=[0, max(values) * 1.2]
    )
    
    fig.update_yaxes(
        tickfont=dict(size=12)
    )
    
    description = f"{aria_title}。{len(categories)}項目の水平棒グラフ。各項目の値: {', '.join([f'{cat}: {val:.1f}%' for cat, val in zip(categories, values)])}"
    return with_a11y(fig, description, chart_type)

def create_funnel_chart(stages, values, budget_values=None, achievement_rates=None):
    """ファネルチャートを作成"""
    fig = go.Figure()
    
    # ARIA用のタイトルを設定
    aria_title = 'ファネル分析'
    
    # 実績ファネル（達成率に応じたヒートマップ色で）
    colors = []
    for i in range(len(stages)):
        if achievement_rates and i < len(achievement_rates):
            # ヒートマップカラーを使用
            colors.append(get_heatmap_color(achievement_rates[i]))
        else:
            # デフォルト色
            colors.append(DARK_COLORS[f'stage_{i+1}'] if i < 5 else DARK_COLORS['stage_5'])
    
    fig.add_trace(
        go.Funnel(
            name='実績',
            y=stages,
            x=values,
            textposition="inside",
            textinfo="value",
            opacity=1.0,  # 透明度は1.0に固定
            textfont=dict(
                size=14,  # フォントサイズを大きく
                color='white',  # 白色で視認性向上
                family='Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            ),
            marker=dict(
                color=colors,
                line=dict(
                    color='rgba(255, 255, 255, 0.6)',  # 境界線を明るく
                    width=3  # 境界線を太く
                )
            ),
            connector=dict(
                line=dict(
                    color='rgba(255, 255, 255, 0.4)',  # コネクターも明るく
                    width=3
                )
            ),
            hovertemplate=(
                '<b>%{y}</b><br>' +
                '実績: <b>%{x:,.0f}</b><br>' +
                '全体比: %{percentInitial}<br>' +
                ('計画比: <b>%{customdata:.1f}%</b>' if achievement_rates else '') +
                '<extra></extra>'
            ),
            customdata=achievement_rates if achievement_rates else None
        )
    )
    
    # 計画との比較がある場合（より薄く表示）
    if budget_values:
        fig.add_trace(
            go.Funnel(
                name='計画',
                y=stages,
                x=budget_values,
                textposition="outside",
                textinfo="none",
                opacity=0.4,  # 透明度をさらに上げて視認性向上
                marker=dict(
                    color=DARK_COLORS['chart_budget'],
                    line=dict(color='rgba(255,255,255,0.4)', width=2)  # 境界線を明るく太く
                ),
                showlegend=False,
                hovertemplate='<b>%{y}</b><br>計画: <b>%{x:,.0f}</b><extra></extra>'
            )
        )
    
    layout_config = PLOTLY_TEMPLATE['layout'].copy()
    layout_config.update({
        'height': 400,  # 高さを増やして視認性向上
        'width': None,
        'autosize': True,
        'showlegend': False,
        'hovermode': 'closest',  # デフォルトのホバーモードに戻す
        'hoverlabel': dict(
            bgcolor='rgba(0, 0, 0, 0.95)',  # ホバー背景を濃く
            bordercolor='#ff6b35',
            font=dict(color='white', size=16)  # ホバーフォントを大きく
        ),
        'margin': dict(l=50, r=50, t=30, b=30),  # マージンを増やす
        'transition': dict(
            duration=300,  # アニメーション追加
            easing='cubic-out'  # Plotly有効なeasing値に修正
        ),
        'xaxis': dict(fixedrange=True),  # ズーム無効化
        'yaxis': dict(fixedrange=True),  # ズーム無効化
        'title': {
            'text': f'<span style="font-size: 1px; color: transparent;">{aria_title}チャート</span>',
            'font': {'size': 1},
            'xref': 'paper',
            'x': 0
        }
    })
    fig.update_layout(**layout_config)
    
    description = f"ファネル分析チャート。{len(stages)}段階のステージを表示: {', '.join(stages)}。"
    if budget_values:
        description += "計画との比較も含む。"
    return with_a11y(fig, description, "funnel")

def create_comparison_chart(categories, actual_values, budget_values, chart_type='bar', value_type='count'):
    """比較チャートを作成"""
    fig = go.Figure()
    
    # ARIA用のタイトルを設定
    aria_title = '実績と計画の比較'
    
    if chart_type == 'bar':
        # 計画
        fig.add_trace(
            go.Bar(
                name='計画',
                x=categories,
                y=budget_values,
                marker=dict(
                    color=DARK_COLORS['chart_budget'],
                    opacity=0.6
                ),
                width=0.8,
                hovertemplate='計画: ' + ('¥%{y:,.0f}' if value_type == 'currency' else '%{y:,.0f}') + '<extra></extra>'
            )
        )
        
        # 実績
        fig.add_trace(
            go.Bar(
                name='実績',
                x=categories,
                y=actual_values,
                marker=dict(
                    color=DARK_COLORS['chart_actual'],
                    opacity=0.8
                ),
                width=0.4,
                hovertemplate='実績: ' + ('¥%{y:,.0f}' if value_type == 'currency' else '%{y:,.0f}') + '<extra></extra>'
            )
        )
        
        layout_config = PLOTLY_TEMPLATE['layout'].copy()
        layout_config.update({
            'barmode': 'overlay',
            'showlegend': True,
            'legend': dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            'height': None,
            'autosize': True,
            'title': {
                'text': f'<span style="font-size: 1px; color: transparent;">{aria_title}グラフ</span>',
                'font': {'size': 1},
                'xref': 'paper',
                'x': 0
            }
        })
        fig.update_layout(**layout_config)
    
    description = f"{aria_title}。{len(categories)}項目の実績と計画の比較。"
    return with_a11y(fig, description, "comparison")

def create_sparkline(values, height=None, width=100, enable_hover=True):
    """スパークラインを作成"""
    fig = go.Figure()
    
    # ARIA用のタイトルを設定
    aria_title = 'トレンドスパークライン'
    
    # 月のラベルを生成
    month_labels = [f"{i+1}月" for i in range(len(values))]
    
    fig.add_trace(
        go.Scatter(
            x=month_labels,
            y=values,
            mode='lines+markers',
            line=dict(
                color=DARK_COLORS['primary_orange'],
                width=2
            ),
            marker=dict(
                size=3,
                color=DARK_COLORS['primary_orange']
            ),
            fill='tozeroy',
            fillcolor=f"rgba(255, 107, 53, 0.2)",
            hovertemplate='<span style="color: white;"><b>%{x}</b><br>%{y:,.0f}</span><extra></extra>' if enable_hover else None,
            hoverinfo='text' if enable_hover else 'none'
        )
    )
    
    fig.update_layout(
        height=None,
        width=width,
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        hovermode='closest' if enable_hover else False,
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="rgba(255,255,255,0.2)",
            font_color="white",
            font_size=12,
        ) if enable_hover else None,
        title={
            'text': f'<span style="font-size: 1px; color: transparent;">{aria_title}</span>',
            'font': {'size': 1},
            'xref': 'paper',
            'x': 0
        }
    )
    
    description = f"スパークライン。{len(values)}期間のトレンドを簡潔に表示。"
    return with_a11y(fig, description, "sparkline")

def create_dual_sparkline(actual_values, budget_values, achievement_rate, height=None, width=100, enable_hover=True, value_type='number', actual_months=None):
    """実績と計画の2本スパークラインを作成"""
    from dash import dcc
    
    fig = go.Figure()
    
    # ARIA用のタイトルを設定
    aria_title = '実績と計画の推移'
    
    # データが空の場合は空のグラフを返す
    if not actual_values or not budget_values:
        fig.update_layout(
            height=height,
            width=width,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(visible=False, fixedrange=True),
            yaxis=dict(visible=False, fixedrange=True),
            title={
                'text': f'<span style="font-size: 1px; color: transparent;">{aria_title}</span>',
                'font': {'size': 1},
                'xref': 'paper',
                'x': 0
            }
        )
        fig = with_a11y(fig, "データなしのスパークライン。", "dual-sparkline-empty")
        return dcc.Graph(
            figure=fig,
            style={'height': '100%', 'width': f'{width}px'},
            config={'displayModeBar': False, 'staticPlot': not enable_hover}
        )
    
    # 月のラベルを生成（1月から12月まで）
    all_month_labels = [f"{i+1}月" for i in range(12)]
    
    # データを最新12ヶ月に制限
    recent_actual = actual_values[-12:] if len(actual_values) > 12 else actual_values
    recent_budget = budget_values[-12:] if len(budget_values) > 12 else budget_values
    
    # 実際のデータ長に合わせて月ラベルを調整（実績と計画の長い方に合わせる）
    max_length = max(len(recent_actual), len(recent_budget))
    month_labels = all_month_labels[:max_length]
    
    # 実績データの月数制限がある場合
    if actual_months is not None and isinstance(actual_months, int):
        if actual_months == 0:
            # actual_months=0の場合、実績線を描画しない
            recent_actual_display = []
            month_labels_actual = []
        else:
            # actual_monthsで指定された月数まで表示
            recent_actual_display = recent_actual[:actual_months]
            month_labels_actual = month_labels[:actual_months]
    elif actual_months and not isinstance(actual_months, int):
        # リストが渡された場合
        actual_month_count = len(actual_months) if hasattr(actual_months, '__len__') else actual_months
        recent_actual_display = recent_actual[:actual_month_count]
        month_labels_actual = month_labels[:actual_month_count]
    else:
        recent_actual_display = recent_actual
        month_labels_actual = month_labels
    
    # 計画線（グレー、細線）
    if recent_budget and len(recent_budget) >= 2:
        fig.add_trace(
            go.Scatter(
                x=month_labels,
                y=recent_budget,
                mode='lines',
                name='計画',
                line=dict(
                    color=DARK_COLORS['chart_budget'],
                    width=1
                ),
                opacity=0.6,
                hovertemplate='<span style="color: white;"><b>計画</b><br>%{x}: %{y:,.0f}' + ('%' if value_type == 'percentage' else '') + '</span><extra></extra>' if enable_hover else None,
                hoverinfo='text' if enable_hover else 'none',
                showlegend=False
            )
        )
    
    # 実績線（ヒートマップカラー、太線）
    if recent_actual_display and len(recent_actual_display) >= 1:
        status_color = get_heatmap_color(achievement_rate)
        fig.add_trace(
            go.Scatter(
                x=month_labels_actual,
                y=recent_actual_display,
                mode='lines+markers',
                name='実績',
                line=dict(
                    color=status_color,
                    width=2
                ),
                marker=dict(
                    size=4,
                    color=status_color,
                    opacity=0.8
                ),
                opacity=0.9,
                hovertemplate='<span style="color: white;"><b>実績</b><br>%{x}: %{y:,.0f}' + ('%' if value_type == 'percentage' else '') + '</span><extra></extra>' if enable_hover else None,
                hoverinfo='text' if enable_hover else 'none',
                showlegend=False
            )
        )
    
    fig.update_layout(
        height=height,
        width=width,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        hovermode='closest' if enable_hover else False,
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="rgba(255,255,255,0.2)",
            font_color="white",
            font_size=12
        ) if enable_hover else None,
        title={
            'text': f'<span style="font-size: 1px; color: transparent;">{aria_title}</span>',
            'font': {'size': 1},
            'xref': 'paper',
            'x': 0
        }
    )
    
    description = f"実績と計画の推移比較。現在の計画比: {achievement_rate:.1f}%"
    fig = with_a11y(fig, description, "dual-sparkline")
    
    return dcc.Graph(
        figure=fig,
        style={'height': f'{height}px', 'width': f'{width}px'},
        config={'displayModeBar': False, 'staticPlot': not enable_hover}
    )

def create_stacked_bar_chart(categories, data_dict, selected_category=None, height=None, horizontal=False, comparison_mode=False, value_type='currency'):
    """積上棒グラフを作成（売上高構成分析用）
    
    Args:
        categories: カテゴリーのリスト（月）
        data_dict: チャネルごとのデータ辞書 {"チャネル名": 値 or [値のリスト]} または比較モード時は {'actual': {}, 'budget': {}}
        selected_category: 選択されたカテゴリー（月）
        height: グラフの高さ
        horizontal: 横棒グラフにするかどうか
        comparison_mode: 実績と計画の比較モードかどうか
    """
    fig = go.Figure()
    
    # ARIA用のタイトルを設定
    aria_title = '売上高構成（経路別）'
    
    # チャネルごとの色を設定（オレンジ・朱色系の濃淡とグレーのバランス）
    channel_colors = {
        'WEB': '#ff6b35',      # 鮮やかなオレンジ（メインカラー）
        'TEL': '#ff8f65',      # 薄いオレンジ
        'DIRECT': '#dc5a2d',   # 濃い朱色
        'REFERRAL': '#718096', # ミディアムグレー
        'OTHER': '#4a5568'     # ダークグレー
    }
    
    if comparison_mode:
        # 比較モード：実績と計画の2本の棒グラフ（横棒・縦棒両対応）
        actual_data = data_dict.get('actual', {})
        budget_data = data_dict.get('budget', {})
        
        # チャネルを実績売上高でソート（降順）
        all_channels = set(actual_data.keys()) | set(budget_data.keys())
        sorted_channels = sorted(all_channels, 
                               key=lambda x: actual_data.get(x, 0), 
                               reverse=True)
        
        # デフォルトの色リスト
        default_colors = ['#ff6b35', '#ff8f65', '#dc5a2d', '#718096', '#4a5568', '#ff9f40', '#a0aec0']
        
        # 計画の棒グラフ（薄い色で表示）
        budget_values = [budget_data.get(ch, 0) for ch in sorted_channels]
        for i, (channel, value) in enumerate(zip(sorted_channels, budget_values)):
            color = channel_colors.get(channel, default_colors[i % len(default_colors)])
            
            if horizontal:
                # 横棒グラフ
                fig.add_trace(
                    go.Bar(
                        name=f'{channel}(計画)',
                        y=["計画"],
                        x=[value],
                        orientation='h',
                        marker=dict(
                            color=color,
                            opacity=0.6,  # 薄く表示
                            line=dict(width=0.5, color=DARK_COLORS['bg_dark'])
                        ),
                        text='',
                        textposition='none',
                        hovertemplate=channel + '<br>計画: ' + ('¥%{x:,.0f}' if value_type == 'currency' else '%{x:,.0f}') + '<extra></extra>',
                        showlegend=False  # 凡例は実績のみ
                    )
                )
            else:
                # 縦棒グラフ
                fig.add_trace(
                    go.Bar(
                        name=f'{channel}(計画)',
                        x=["計画"],
                        y=[value],
                        marker=dict(
                            color=color,
                            opacity=0.6,  # 薄く表示
                            line=dict(width=0.5, color=DARK_COLORS['bg_dark'])
                        ),
                        text='',
                        textposition='none',
                        hovertemplate=channel + '<br>計画: ' + ('¥%{y:,.0f}' if value_type == 'currency' else '%{y:,.0f}') + '<extra></extra>',
                        showlegend=False  # 凡例は実績のみ
                    )
                )
        
        # 実績の棒グラフ
        actual_values = [actual_data.get(ch, 0) for ch in sorted_channels]
        for i, (channel, value) in enumerate(zip(sorted_channels, actual_values)):
            color = channel_colors.get(channel, default_colors[i % len(default_colors)])
            
            if horizontal:
                # 横棒グラフ
                fig.add_trace(
                    go.Bar(
                        name=channel,
                        y=["実績"],
                        x=[value],
                        orientation='h',
                        marker=dict(
                            color=color,
                            line=dict(width=0.5, color=DARK_COLORS['bg_dark'])
                        ),
                        text='',
                        textposition='none',
                        hovertemplate=channel + '<br>実績: ' + ('¥%{x:,.0f}' if value_type == 'currency' else '%{x:,.0f}') + '<extra></extra>',
                        showlegend=True
                    )
                )
            else:
                # 縦棒グラフ
                fig.add_trace(
                    go.Bar(
                        name=channel,
                        x=["実績"],
                        y=[value],
                        marker=dict(
                            color=color,
                            line=dict(width=0.5, color=DARK_COLORS['bg_dark'])
                        ),
                        text='',
                        textposition='none',
                        hovertemplate=channel + '<br>実績: ' + ('¥%{y:,.0f}' if value_type == 'currency' else '%{y:,.0f}') + '<extra></extra>',
                        showlegend=True
                    )
                )
    else:
        # 通常モード
        # データを単一値のリストに変換（横棒グラフ用）
        if horizontal and isinstance(next(iter(data_dict.values())), (int, float)):
            # 単一値の場合はリストに変換
            data_dict = {k: [v] for k, v in data_dict.items()}
        
        # チャネルを売上高でソート（降順）
        sorted_channels = sorted(data_dict.items(), 
                               key=lambda x: x[1][0] if isinstance(x[1], list) else x[1], 
                               reverse=True)
        
        # 各チャネルのデータを積上棒として追加
        for i, (channel, values) in enumerate(sorted_channels):
            # デフォルトの色リスト（オレンジ系とグレー系のバランス）
            default_colors = ['#ff6b35', '#ff8f65', '#dc5a2d', '#718096', '#4a5568', '#ff9f40', '#a0aec0']
            color = channel_colors.get(channel, default_colors[i % len(default_colors)])
            
            # 値がリストでない場合はリストに変換
            if not isinstance(values, list):
                values = [values]
            
            if horizontal:
                # 横棒グラフ
                fig.add_trace(
                    go.Bar(
                        name=channel,
                        y=categories,
                        x=values,
                        orientation='h',
                        marker=dict(
                            color=color,
                            line=dict(width=0.5, color=DARK_COLORS['bg_dark'])
                        ),
                        text='',
                        textposition='none',
                        hovertemplate=channel + '<br>' + ('¥%{x:,.0f}' if value_type == 'currency' else '%{x:,.0f}') + '<extra></extra>'
                    )
                )
            else:
                # 縦棒グラフ
                fig.add_trace(
                    go.Bar(
                        name=channel,
                        x=categories,
                        y=values,
                        marker=dict(
                            color=color,
                            line=dict(width=0.5, color=DARK_COLORS['bg_dark'])
                        ),
                        text=[f'¥{v:,.0f}' if value_type == 'currency' else f'{v:,.0f}' for v in values],
                        textposition='none',
                        hovertemplate=channel + '<br>%{x}: ' + ('¥%{y:,.0f}' if value_type == 'currency' else '%{y:,.0f}') + '<extra></extra>'
                    )
                )
    
    # レイアウト更新
    layout_config = PLOTLY_TEMPLATE['layout'].copy()
    layout_config.update({
        'barmode': 'stack',
        'showlegend': True,
        'legend': dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10)
        ),
        'height': None,
        'autosize': True,
        'margin': dict(l=40, r=100, t=10, b=20) if not (horizontal or comparison_mode) else dict(l=40, r=100, t=10, b=10),
        'title': {
            'text': f'<span style="font-size: 1px; color: transparent;">{aria_title}グラフ</span>',
            'font': {'size': 1},
            'xref': 'paper',
            'x': 0
        }
    })
    fig.update_layout(**layout_config)
    
    if horizontal:
        # 横棒グラフの軸設定
        fig.update_xaxes(
            title_text='',
            tickformat=',.0f',
            gridcolor=DARK_COLORS['border_color']
        )
        fig.update_yaxes(
            visible=True,  # Y軸ラベルを表示
            gridcolor=DARK_COLORS['border_color'],
            tickfont=dict(size=12, color=DARK_COLORS['text_primary'])
        )
    else:
        # 縦棒グラフの軸設定
        fig.update_xaxes(gridcolor=DARK_COLORS['border_color'])
        fig.update_yaxes(
            title_text='',
            tickformat=',.0f',
            gridcolor=DARK_COLORS['border_color']
        )
    
    description = f"{aria_title}。{len(categories)}期間の経路別売上構成を積上棒グラフで表示。"
    if selected_category:
        description += f"現在選択中: {selected_category}"
    
    return with_a11y(fig, description, "stacked-bar")