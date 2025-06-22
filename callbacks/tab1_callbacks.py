"""
Tab1: ファネル分析のコールバック
"""
import pandas as pd
from dash import Input, Output, State, ALL, html, dcc, no_update
import logging

logger = logging.getLogger(__name__)
from data_manager import (
    data_manager, get_dataframe_from_store, apply_filters,
    format_number, clean_channel_names
)
from components.cards import (
    create_metric_card, create_channel_funnel, create_insight_card,
    create_trend_item, get_performance_color
)
from components.loading import create_chart_loading_placeholder, create_skeleton_card
from config import INTEGRATED_STAGES, DARK_COLORS, LAYOUT, PLOTLY_CONFIG

def register_tab1_callbacks(app):
    """Tab1のコールバックを登録"""
    
    # ビュータイプの切り替え
    @app.callback(
        [Output('funnel-view-actual', 'className'),
         Output('funnel-view-achievement', 'className'),
         Output('funnel-view-conversion', 'className'),
         Output('funnel-view-type', 'data')],
        [Input('funnel-view-actual', 'n_clicks'),
         Input('funnel-view-achievement', 'n_clicks'),
         Input('funnel-view-conversion', 'n_clicks')],
        [State('funnel-view-type', 'data')]
    )
    def update_view_type(actual_clicks, achievement_clicks, conversion_clicks, current_view):
        from dash import ctx
        if not ctx.triggered:
            return 'view-toggle-btn active', 'view-toggle-btn', 'view-toggle-btn', 'actual'
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'funnel-view-actual':
            return 'view-toggle-btn active', 'view-toggle-btn', 'view-toggle-btn', 'actual'
        elif button_id == 'funnel-view-achievement':
            return 'view-toggle-btn', 'view-toggle-btn active', 'view-toggle-btn', 'achievement'
        elif button_id == 'funnel-view-conversion':
            return 'view-toggle-btn', 'view-toggle-btn', 'view-toggle-btn active', 'conversion'
        
        return 'view-toggle-btn active', 'view-toggle-btn', 'view-toggle-btn', 'actual'
    
    # ファネルメトリクスバー更新（ステージ別複合グラフ）
    @app.callback(
        Output('funnel-metrics-bar', 'children'),
        [Input('month-selector', 'value'),
         Input('btn-plan-ratio', 'className'),
         Input('channel-filter', 'value'),
         Input('plan-filter', 'value'),
         Input('channel-filter-tab1', 'value')]
    )
    def update_funnel_metrics(selected_month, plan_ratio_class, 
                            channel_filter, plan_filter, channel_filter_tab1):
        data = data_manager.get_data()
        if not data or not selected_month:
            return []
        
        try:
            from components.charts import create_trend_chart
            from data_manager import should_display_actual_data, get_last_data_month
            
            # データタイプの判定（Tab1は常に元データをそのまま表示）
            data_type = 'plan_ratio' if 'active' in plan_ratio_class else 'plan_diff'
            # Tab1では累月・単月の概念がないため、常に元データを使用
            
            # ステージ定義
            stages = [
                {'title': 'リード・アプローチ', 'plans': ['新規リード数', 'アプローチ数']},
                {'title': '商談', 'plans': ['商談ステージ']},
                {'title': '具体検討', 'plans': ['具体検討ステージ']},
                {'title': '内諾', 'plans': ['内諾ステージ']},
                {'title': '獲得', 'plans': ['新規アプリ獲得数（単月）']}
            ]
            
            # 全体の最終データ月を取得（全ステージで統一するため）
            global_last_month = None
            if 'indicators' in data:
                actual_df_global = get_dataframe_from_store(data, 'indicators', 'actual')
                if actual_df_global is not None:
                    current_channel_filter = [channel_filter_tab1] if channel_filter_tab1 else []
                    filtered_all_actual = apply_filters(actual_df_global, current_channel_filter, plan_filter)
                    month_cols_global = [col for col in filtered_all_actual.columns if col.endswith('月')]
                    global_last_month = get_last_data_month(filtered_all_actual, month_cols_global)
            
            graphs = []
            
            for stage in stages:
                actual_df = get_dataframe_from_store(data, 'indicators', 'actual')
                budget_df = get_dataframe_from_store(data, 'indicators', 'budget')
                
                if actual_df is not None and budget_df is not None:
                    # ステージ関連のプランだけをフィルタリング
                    stage_actual = actual_df[actual_df['plan'].isin(stage['plans'])]
                    stage_budget = budget_df[budget_df['plan'].isin(stage['plans'])]
                    
                    # チャネル・プランフィルター適用
                    # Tab1専用のチャネルフィルターを使用
                    current_channel_filter = [channel_filter_tab1] if channel_filter_tab1 else []
                    filtered_actual = apply_filters(stage_actual, current_channel_filter, plan_filter)
                    filtered_budget = apply_filters(stage_budget, current_channel_filter, plan_filter)
                    
                    if not filtered_actual.empty and not filtered_budget.empty:
                        month_cols = [col for col in filtered_actual.columns if col.endswith('月')]
                        all_months = [f"{i}月" for i in range(1, 13)]
                        
                        budget_totals = []
                        actual_totals = []
                        actual_months = []
                        
                        # 月別データの集計
                        for month in all_months:
                            if month in month_cols:
                                budget_total = filtered_budget[month].sum()
                                budget_totals.append(budget_total)
                                
                                # グローバルな最終データ月を使用して表示判定
                                if global_last_month and month in month_cols_global:
                                    try:
                                        global_last_idx = month_cols_global.index(global_last_month)
                                        target_idx = month_cols_global.index(month)
                                        if target_idx <= global_last_idx:
                                            actual_months.append(month)
                                            actual_total = filtered_actual[month].sum()
                                            actual_totals.append(actual_total)
                                    except (ValueError, IndexError):
                                        pass
                            else:
                                budget_totals.append(0)
                        
                        # Tab1では期間変換は行わず、元データをそのまま使用
                        
                        # 達成率計算（実績がある月全てに対して計算）
                        achievement_rates = []
                        if data_type == 'plan_ratio':
                            # actual_monthsに含まれる月のインデックスを作成
                            actual_month_indices = {}
                            for i, month in enumerate(actual_months):
                                if month in all_months:
                                    actual_month_indices[all_months.index(month)] = i
                            
                            # 全ての月に対して達成率を計算
                            for month_idx, month in enumerate(all_months):
                                if month_idx in actual_month_indices:
                                    # 実績データがある月
                                    actual_idx = actual_month_indices[month_idx]
                                    actual_val = actual_totals[actual_idx]
                                    budget_val = budget_totals[month_idx]
                                    if budget_val > 0:
                                        achievement_rates.append((actual_val / budget_val) * 100)
                                    else:
                                        achievement_rates.append(0)
                                else:
                                    # 実績データがない月はNoneを追加（線を表示しない）
                                    achievement_rates.append(None)
                        
                        # タブ2と同じスタイルのトレンドチャート作成
                        fig = create_trend_chart(
                            all_months, budget_totals, actual_totals, actual_months,
                            achievement_rates if data_type == 'plan_ratio' else None,
                            selected_month, 'count', None, data_type
                        )
                        
                        # 縦軸タイトルを削除してグラフサイズを拡大
                        fig.update_yaxes(title_text="", secondary_y=False)
                        fig.update_yaxes(title_text="", secondary_y=True)
                        
                        # 左右マージンを最小化してグラフ横幅を最大化
                        fig.update_layout(
                            margin=dict(l=3, r=3, t=1, b=8),  # マージンを大幅削減して高さを確保
                            height=None,  # 親コンテナの高さに自動調整
                            autosize=True
                        )
                        
                        # KPIサマリー作成
                        kpi_summary = []
                        if selected_month in actual_months:
                            month_idx = actual_months.index(selected_month)
                            actual_current = actual_totals[month_idx]
                            budget_idx = all_months.index(selected_month)
                            budget_current = budget_totals[budget_idx]
                            achievement_rate = (actual_current / budget_current * 100) if budget_current > 0 else 0
                            
                            from components.cards import get_performance_color
                            
                            kpi_summary = [
                                html.Div([
                                    html.Span(f"{round(achievement_rate)}%", style={
                                        'fontSize': '1.1rem',
                                        'fontWeight': '700',
                                        'color': get_performance_color(achievement_rate)
                                    }),
                                    html.Span(" 計画比", style={
                                        'fontSize': '0.7rem',
                                        'color': DARK_COLORS['text_muted']
                                    })
                                ]),
                                html.Div([
                                    html.Span(f"{format_number(actual_current):,}", style={
                                        'fontSize': '1.1rem',
                                        'fontWeight': '700',
                                        'color': DARK_COLORS['text_primary']
                                    }),
                                    html.Span(f" / {format_number(budget_current):,}", style={
                                        'fontSize': '0.7rem',
                                        'color': DARK_COLORS['text_muted']
                                    })
                                ])
                            ]
                        
                        # タブ2と同じセクション構造を作成
                        section = html.Div([
                            # ヘッダー（タイトルとKPIサマリー）
                            html.Div([
                                html.H3(stage['title'], style={
                                    'fontSize': '1rem',
                                    'fontWeight': '600',
                                    'color': DARK_COLORS['text_primary']
                                }),
                                html.Div(kpi_summary, style={
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'gap': '8px'
                                })
                            ], style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'marginBottom': '2px',
                                'paddingBottom': '2px',
                                'paddingLeft': '2px',
                                'paddingRight': '2px',
                                'borderBottom': f'1px solid {DARK_COLORS["border_color"]}'
                            }),
                            
                            # グラフ
                            dcc.Graph(
                                figure=fig,
                                style={'height': '100%', 'minHeight': 0, 'maxHeight': '100%'},
                                config=PLOTLY_CONFIG
                            )
                        ], 
                        className='plan-card',
                        style={
                            'backgroundColor': DARK_COLORS['bg_card'],
                            'borderRadius': LAYOUT['card_radius'],
                            'padding': '4px',  # パディングを削減して高さを確保
                            'overflow': 'hidden',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'height': '100%',
                            'border': f'1px solid {DARK_COLORS["border_color"]}'
                        })
                        
                        graphs.append(section)
            
            return graphs
            
        except Exception as e:
            logger.error(f"Error in update_funnel_metrics: {str(e)}")
            return []
    
    # ファネルグリッド更新
    @app.callback(
        Output('funnel-grid', 'children'),
        [Input('month-selector', 'value'),
         Input('channel-filter', 'value'),
         Input('plan-filter', 'value'),
         Input('channel-filter-tab1', 'value')]
    )
    def update_funnel_grid(selected_month, channel_filter, plan_filter, channel_filter_tab1):
        data = data_manager.get_data()
        if not data or not selected_month:
            return []
        
        try:
            from components.charts import create_funnel_chart
            # チャネルリスト - フィルターが設定されている場合はそのチャネルのみ表示
            if channel_filter_tab1:
                channels = [channel_filter_tab1]
            else:
                channels = ['全体']
                if 'indicators' in data:
                    actual_df = get_dataframe_from_store(data, 'indicators', 'actual')
                    if actual_df is not None:
                        raw_channels = clean_channel_names(actual_df['channel'].unique())
                        main_channels = []
                        for ch in ['新規web', '新規法人', '新規代理店', 'クロスセル']:
                            if ch in raw_channels:
                                main_channels.append(ch)
                        channels.extend(main_channels[:4])
            
            funnel_charts = []
            
            for channel in channels:
                # チャネル別のフィルタ設定
                if channel == '全体':
                    ch_filter = []
                else:
                    ch_filter = [channel]
                
                # ファネルステージデータの取得
                if 'indicators' in data:
                    indicators_actual = get_dataframe_from_store(data, 'indicators', 'actual')
                    indicators_budget = get_dataframe_from_store(data, 'indicators', 'budget')
                    
                    if indicators_actual is not None and indicators_budget is not None:
                        # チャネルフィルター適用
                        filtered_actual = apply_filters(indicators_actual, ch_filter, plan_filter or [])
                        filtered_budget = apply_filters(indicators_budget, ch_filter, plan_filter or [])
                        
                        # 月のコラム名
                        month_cols = [col for col in filtered_actual.columns if col.endswith('月')]
                        
                        if selected_month not in month_cols:
                            continue
                        
                        # 統合ステージのデータを計算
                        stage_names = []
                        actual_values = []
                        budget_values = []
                        
                        for stage_name, plans in INTEGRATED_STAGES.items():
                            # 該当プランをフィルタリング
                            stage_actual = filtered_actual[filtered_actual['plan'].isin(plans)]
                            stage_budget = filtered_budget[filtered_budget['plan'].isin(plans)]
                            
                            if not stage_actual.empty and not stage_budget.empty:
                                # 月別データを合計
                                actual_total = stage_actual[selected_month].sum()
                                budget_total = stage_budget[selected_month].sum()
                                
                                # チャネルに応じてステージ名を調整
                                display_stage_name = stage_name
                                if stage_name == "リード・アプローチ":
                                    if channel == "全体":
                                        display_stage_name = "リード・アプローチ"
                                    elif channel in ["新規web", "新規代理店"]:
                                        display_stage_name = "リード"
                                    elif channel == "クロスセル":
                                        display_stage_name = "アプローチ"
                                    else:
                                        display_stage_name = "リード・アプローチ"
                                
                                stage_names.append(display_stage_name)
                                actual_values.append(actual_total)
                                budget_values.append(budget_total)
                        
                        # Plotlyファネルチャートを作成
                        if stage_names and actual_values:
                            # 各ステージの達成率を計算
                            achievement_rates = []
                            for i in range(len(actual_values)):
                                if budget_values and i < len(budget_values) and budget_values[i] > 0:
                                    rate = (actual_values[i] / budget_values[i]) * 100
                                    achievement_rates.append(rate)
                                else:
                                    achievement_rates.append(0)
                            
                            fig = create_funnel_chart(stage_names, actual_values, budget_values, achievement_rates)
                            
                            # チャネル専用のタイトルとKPIを追加
                            overall_achievement = (actual_values[-1] / budget_values[-1] * 100) if budget_values and budget_values[-1] > 0 else 0
                            
                            funnel_chart_div = html.Div([
                                # ヘッダー（チャネル名と達成率を横並び）
                                html.Div([
                                    html.Div(channel, style={
                                        'fontSize': '0.8rem',
                                        'fontWeight': '600',
                                        'flex': '1'
                                    }),
                                    html.Div([
                                        html.Span(f"{round(overall_achievement)}%", style={
                                            'fontSize': '0.9rem',
                                            'fontWeight': '700',
                                            'color': '#48bb78' if overall_achievement >= 100 else '#ed8936' if overall_achievement >= 80 else '#e53e3e',
                                            'marginRight': '4px'
                                        }),
                                        html.Span("最終CV率(獲得)", style={
                                            'fontSize': '0.7rem',
                                            'color': DARK_COLORS['text_muted']
                                        })
                                    ], style={
                                        'display': 'flex',
                                        'alignItems': 'center'
                                    })
                                ], style={
                                    'backgroundColor': DARK_COLORS['bg_hover'],
                                    'padding': '6px 8px',  # パディングを縮小
                                    'borderRadius': '6px',
                                    'border': f'1px solid {DARK_COLORS["border_color"]}',
                                    'marginBottom': '8px',  # マージンを縮小
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'space-between'
                                }),
                                # Plotlyファネルチャート
                                dcc.Graph(
                                    figure=fig,
                                    style={
                                        'height': '300px',
                                        'maxHeight': '300px',
                                        'minHeight': '300px'
                                    },
                                    config=PLOTLY_CONFIG
                                )
                            ], style={
                                'height': '100%',
                                'maxHeight': '400px',
                                'display': 'flex',
                                'flexDirection': 'column'
                            })
                            
                            funnel_charts.append(funnel_chart_div)
            
            return funnel_charts
            
        except Exception as e:
            logger.error(f"Error in update_funnel_grid: {str(e)}")
            return []
    
    # チャネルトレンド更新
    @app.callback(
        Output('channel-trends', 'children'),
        [Input('month-selector', 'value'),
         Input('trend-cv-filter', 'value'),
         Input('channel-filter-tab1', 'value')]
    )
    def update_channel_trends(selected_month, cv_filter, channel_filter_tab1):
        data = data_manager.get_data()
        if not data or not selected_month:
            return []
        
        try:
            # デフォルト値設定
            if cv_filter is None:
                cv_filter = '3to4'
                
            # ボリュームは常に全ステージ表示（獲得数ベース）
            volume_plans = ['新規アプリ獲得数（単月）']
            
            # CV率フィルタのマッピング
            cv_stage_mapping = {
                '1to2': (['新規リード数', 'アプローチ数'], ['商談ステージ']),
                '2to3': (['商談ステージ'], ['具体検討ステージ']),
                '3to4': (['具体検討ステージ'], ['内諾ステージ']),
                '4to5': (['内諾ステージ'], ['新規アプリ獲得数（単月）'])
            }
            
            if 'indicators' in data:
                indicators_actual = get_dataframe_from_store(data, 'indicators', 'actual')
                
                if indicators_actual is not None and not indicators_actual.empty:
                    # チャネルフィルターが設定されている場合はそのチャネルのみ、そうでなければ主要4チャネル
                    if channel_filter_tab1:
                        channels = [channel_filter_tab1]
                    else:
                        raw_channels = clean_channel_names(indicators_actual['channel'].unique())
                        # 主要4チャネルを選択 - 清理済みチャネル名を使用
                        channels = []
                        for ch in ['新規web', '新規法人', '新規代理店', 'クロスセル']:
                            if ch in raw_channels:
                                channels.append(ch)
                        channels = channels[:4]
                    
                    # チャネル別のデータを格納するリスト
                    channel_data_list = []
                    for channel in channels:
                        # チャネルフィルターをapply_filtersと同じ形式で設定
                        ch_filter = [channel]
                        
                        
                        # 獲得数データを取得（ボリューム表示用）
                        volume_data_list = []
                        
                        for plan in volume_plans:
                            plan_data = indicators_actual[indicators_actual['plan'] == plan]
                            filtered_data = apply_filters(plan_data, ch_filter, [])
                            if not filtered_data.empty:
                                volume_data_list.append(filtered_data)
                        
                        # CV率計算用のステージデータを取得
                        cv_from_plans, cv_to_plans = cv_stage_mapping.get(cv_filter, (['内諾ステージ'], ['新規アプリ獲得数（単月）']))
                        
                        # 法人チャネルの特殊処理（1ステージがない）
                        if channel == '新規法人' and cv_filter == '1to2':
                            # 法人の場合、1to2は存在しないのでスキップ（データなしとして処理）
                            continue
                        
                        
                        cv_from_data_list = []
                        cv_to_data_list = []
                        
                        for plan in cv_from_plans:
                            plan_data = indicators_actual[indicators_actual['plan'] == plan]
                            filtered_data = apply_filters(plan_data, ch_filter, [])
                            if not filtered_data.empty:
                                cv_from_data_list.append(filtered_data)
                        
                        for plan in cv_to_plans:
                            plan_data = indicators_actual[indicators_actual['plan'] == plan]
                            filtered_data = apply_filters(plan_data, ch_filter, [])
                            if not filtered_data.empty:
                                cv_to_data_list.append(filtered_data)
                        
                        if selected_month in indicators_actual.columns:
                            # 選択されたボリュームの合計を計算
                            volume_total = 0
                            for vol_data in volume_data_list:
                                volume_total += vol_data[selected_month].sum() if not vol_data.empty else 0
                            
                            # CV率計算用の数値を取得
                            cv_from_total = 0
                            cv_to_total = 0
                            
                            for cv_from_data in cv_from_data_list:
                                cv_from_total += cv_from_data[selected_month].sum() if not cv_from_data.empty else 0
                                
                            for cv_to_data in cv_to_data_list:
                                cv_to_total += cv_to_data[selected_month].sum() if not cv_to_data.empty else 0
                            
                            # CV率を計算
                            cv_rate = (cv_to_total / cv_from_total * 100) if cv_from_total > 0 else 0
                            
                            # ボリュームのトレンドデータを取得
                            month_cols = [col for col in indicators_actual.columns if col.endswith('月')]
                            volume_trend = {
                                'actual_values': [],
                                'budget_values': []
                            }
                            
                            # 計画データを事前に取得
                            budget_df = get_dataframe_from_store(data, 'indicators', 'budget')
                            
                            # 各月のデータを取得
                            for month in month_cols:
                                # 実績データ - 選択されたボリュームフィルタに基づく
                                month_volume = 0
                                for plan in volume_plans:
                                    plan_data = indicators_actual[indicators_actual['plan'] == plan]
                                    filtered_data = apply_filters(plan_data, ch_filter, [])
                                    if not filtered_data.empty and month in filtered_data.columns:
                                        month_volume += filtered_data[month].sum()
                                volume_trend['actual_values'].append(month_volume)
                                
                                # 計画データを取得
                                if budget_df is not None:
                                    budget_volume = 0
                                    for plan in volume_plans:
                                        budget_plan_data = budget_df[budget_df['plan'] == plan]
                                        filtered_budget = apply_filters(budget_plan_data, ch_filter, [])
                                        if not filtered_budget.empty and month in filtered_budget.columns:
                                            budget_volume += filtered_budget[month].sum()
                                    volume_trend['budget_values'].append(budget_volume)
                                else:
                                    volume_trend['budget_values'].append(0)
                            
                            # CV率計算用のデータ準備
                            cv_trend_data = {
                                'volume_actual': [],
                                'acq_actual': [],
                                'cv_budget_values': []
                            }
                            
                            # 月別データを取得
                            
                            for month in month_cols:
                                # 実績データ - 選択されたCV率フィルタに基づく
                                month_cv_from_total = 0
                                month_cv_to_total = 0
                                
                                for plan in cv_from_plans:
                                    plan_data = indicators_actual[indicators_actual['plan'] == plan]
                                    filtered_data = apply_filters(plan_data, ch_filter, [])
                                    if not filtered_data.empty and month in filtered_data.columns:
                                        plan_value = filtered_data[month].sum()
                                        month_cv_from_total += plan_value
                                    
                                for plan in cv_to_plans:
                                    plan_data = indicators_actual[indicators_actual['plan'] == plan]
                                    filtered_data = apply_filters(plan_data, ch_filter, [])
                                    if not filtered_data.empty and month in filtered_data.columns:
                                        plan_value = filtered_data[month].sum()
                                        month_cv_to_total += plan_value
                                
                                cv_trend_data['volume_actual'].append(month_cv_from_total)
                                cv_trend_data['acq_actual'].append(month_cv_to_total)
                                
                                # 計画CV率計算
                                if budget_df is not None:
                                    budget_cv_from_total = 0
                                    budget_cv_to_total = 0
                                    
                                    for plan in cv_from_plans:
                                        budget_plan_data = budget_df[budget_df['plan'] == plan]
                                        filtered_budget = apply_filters(budget_plan_data, ch_filter, [])
                                        if not filtered_budget.empty and month in filtered_budget.columns:
                                            budget_cv_from_total += filtered_budget[month].sum()
                                    
                                    for plan in cv_to_plans:
                                        budget_plan_data = budget_df[budget_df['plan'] == plan]
                                        filtered_budget = apply_filters(budget_plan_data, ch_filter, [])
                                        if not filtered_budget.empty and month in filtered_budget.columns:
                                            budget_cv_to_total += filtered_budget[month].sum()
                                    
                                    budget_cv = (budget_cv_to_total / budget_cv_from_total * 100) if budget_cv_from_total > 0 else 0
                                    cv_trend_data['cv_budget_values'].append(budget_cv)
                                else:
                                    cv_trend_data['cv_budget_values'].append(0)
                            
                            # チャネルデータを格納（後でソート用）
                            is_selected = (channel_filter_tab1 == channel)
                            
                            # CV率の達成率を計算（選択月の予算CV率との比較）
                            month_index = month_cols.index(selected_month) if selected_month in month_cols else -1
                            if month_index >= 0 and month_index < len(cv_trend_data['cv_budget_values']):
                                budget_cv_rate = cv_trend_data['cv_budget_values'][month_index]
                            else:
                                budget_cv_rate = 0
                            cv_achievement_rate = (cv_rate / budget_cv_rate * 100) if budget_cv_rate > 0 else 0
                            
                            channel_data_list.append({
                                'channel': channel,
                                'volume_total': volume_total,
                                'cv_rate': cv_rate,
                                'cv_achievement_rate': cv_achievement_rate,
                                'volume_trend_data': volume_trend,
                                'cv_trend_data': cv_trend_data,
                                'is_selected': is_selected
                            })
                    
                    # CV率達成率でソート（0%・N/Aを最下段に配置）
                    channel_data_list.sort(key=lambda x: (x['cv_achievement_rate'] == 0, x['cv_achievement_rate'] if x['cv_achievement_rate'] > 0 else float('inf')))
                    
                    # ソート済みのデータからトレンドカードを作成
                    trend_items = []
                    for data in channel_data_list:
                        trend_items.append(
                            create_trend_item(
                                data['channel'], 
                                format_number(data['volume_total']), 
                                data['cv_rate'],
                                volume_trend_data=data['volume_trend_data'],
                                cv_trend_data=data['cv_trend_data'],
                                is_selected=data['is_selected']
                            )
                        )
                    
                    return trend_items
            
            return []
            
        except Exception as e:
            logger.error(f"Error in update_channel_trends: {str(e)}")
            return []
    
    # ファネルインサイト更新
    @app.callback(
        Output('funnel-insights', 'children'),
        [Input('month-selector', 'value')]
    )
    def update_funnel_insights(selected_month):
        data = data_manager.get_data()
        if not data or not selected_month:
            return []
        
        insights = []
        
        try:
            if 'indicators' in data:
                indicators_actual = get_dataframe_from_store(data, 'indicators', 'actual')
                
                if indicators_actual is not None and not indicators_actual.empty:
                    # 新規webのCV率分析
                    web_lead = indicators_actual[indicators_actual['plan'].isin(['新規リード数', 'アプローチ数'])]
                    web_lead = apply_filters(web_lead, ['新規web'], [])
                    web_acq = indicators_actual[indicators_actual['plan'] == '新規アプリ獲得数（単月）']
                    web_acq = apply_filters(web_acq, ['新規web'], [])
                    
                    if not web_lead.empty and not web_acq.empty and selected_month in web_lead.columns:
                        lead_val = web_lead[selected_month].sum()
                        acq_val = web_acq[selected_month].sum()
                        
                        if lead_val > 0:
                            cv_rate = (acq_val / lead_val * 100)
                            if cv_rate < 10:
                                insights.append(
                                    create_insight_card(
                                        'critical',
                                        '新規(WEB) CV率改善が急務',
                                        f'全体平均18.7%に対し{round(cv_rate)}%と大幅に低い。特に商談→具体検討の転換率が課題。'
                                    )
                                )
                    
                    # 新規代理店のリード減少分析
                    agent_data = indicators_actual[indicators_actual['plan'] == '新規リード数']
                    agent_data = apply_filters(agent_data, ['新規代理店'], [])
                    
                    if not agent_data.empty:
                        month_cols = [col for col in agent_data.columns if col.endswith('月')]
                        month_idx = month_cols.index(selected_month) if selected_month in month_cols else -1
                        
                        if month_idx > 0:
                            current_val = agent_data[selected_month].sum()
                            prev_val = agent_data[month_cols[month_idx-1]].sum()
                            
                            if prev_val > 0:
                                change_rate = ((current_val - prev_val) / prev_val * 100)
                                if change_rate < -10:
                                    insights.append(
                                        create_insight_card(
                                            'warning',
                                            '新規(代理店) リード数減少',
                                            f'前月比{change_rate:.0f}%のリード減少。パートナー施策の見直しが必要。'
                                        )
                                    )
                    
                    # クロスセル好調の分析
                    cross_lead = indicators_actual[indicators_actual['plan'] == 'アプローチ数']
                    cross_lead = apply_filters(cross_lead, ['クロスセル'], [])
                    cross_acq = indicators_actual[indicators_actual['plan'] == '新規アプリ獲得数（単月）']
                    cross_acq = apply_filters(cross_acq, ['クロスセル'], [])
                    
                    if not cross_lead.empty and not cross_acq.empty and selected_month in cross_lead.columns:
                        lead_val = cross_lead[selected_month].sum()
                        acq_val = cross_acq[selected_month].sum()
                        
                        if lead_val > 0:
                            cv_rate = (acq_val / lead_val * 100)
                            if cv_rate > 20:
                                insights.append(
                                    create_insight_card(
                                        'info',
                                        'クロスセル好調維持',
                                        f'CV率{round(cv_rate)}%と高水準。成功要因の横展開を推奨。'
                                    )
                                )
            
            # インサイトが少ない場合はデフォルトを追加
            if len(insights) == 0:
                insights.append(
                    create_insight_card(
                        'info',
                        'データ分析中',
                        '追加のインサイトは継続的なデータ収集により明らかになります。'
                    )
                )
            
            return insights
            
        except Exception as e:
            logger.error(f"Error in update_funnel_insights: {str(e)}")
            return []
    
    # KPIカードクリックでチャネルフィルターを設定/解除
    @app.callback(
        Output('channel-filter-tab1', 'value'),
        [Input({'type': 'trend-card', 'channel': ALL}, 'n_clicks')],
        [State('channel-filter-tab1', 'value')],
        prevent_initial_call=True
    )
    def update_channel_filter_from_card(n_clicks_list, current_filter):
        from dash import ctx
        if not ctx.triggered or not any(n_clicks_list):
            return current_filter
        
        # クリックされたカードのチャネルを取得
        triggered_id = ctx.triggered[0]['prop_id']
        
        if 'trend-card' in triggered_id:
            # JSONパースして チャネル名を取得
            import json
            try:
                card_info = json.loads(triggered_id.split('.')[0])
                channel = card_info.get('channel')
                if channel:
                    # 同じチャネルが既に選択されている場合はフィルターを解除
                    if current_filter == channel:
                        return None  # フィルター解除
                    else:
                        return channel  # 新しいチャネルを設定
            except:
                pass
        
        return current_filter
    
    # ステージ別CV率カードの更新
    @app.callback(
        Output('stage-cv-cards', 'children'),
        [Input('month-selector', 'value'),
         Input('stage-cv-filter', 'data'),
         Input('channel-filter-tab1', 'value')]
    )
    def update_stage_cv_cards(selected_month, selected_stage, channel_filter_tab1):
        data = data_manager.get_data()
        if not data or not selected_month:
            return []
        
        try:
            # ステージの定義
            stage_definitions = [
                {'id': '1to2', 'label': 'to 商談', 'from_plans': ['新規リード数', 'アプローチ数'], 'to_plans': ['商談ステージ']},
                {'id': '2to3', 'label': 'to 具体検討', 'from_plans': ['商談ステージ'], 'to_plans': ['具体検討ステージ']},
                {'id': '3to4', 'label': 'to 内諾', 'from_plans': ['具体検討ステージ'], 'to_plans': ['内諾ステージ']},
                {'id': '4to5', 'label': 'to 獲得', 'from_plans': ['内諾ステージ'], 'to_plans': ['新規アプリ獲得数（単月）']}
            ]
            
            cards = []
            
            if 'indicators' in data:
                indicators_actual = get_dataframe_from_store(data, 'indicators', 'actual')
                indicators_budget = get_dataframe_from_store(data, 'indicators', 'budget')
                
                if indicators_actual is not None and indicators_budget is not None:
                    for stage_def in stage_definitions:
                        # チャネルフィルタの設定
                        ch_filter = [channel_filter_tab1] if channel_filter_tab1 else []
                        
                        from_total_actual = 0
                        to_total_actual = 0
                        from_total_budget = 0
                        to_total_budget = 0
                        
                        # FROM側のデータ集計（チャネルフィルタ適用）
                        for plan in stage_def['from_plans']:
                            plan_actual = indicators_actual[indicators_actual['plan'] == plan]
                            plan_budget = indicators_budget[indicators_budget['plan'] == plan]
                            
                            # チャネルフィルタを適用
                            filtered_actual = apply_filters(plan_actual, ch_filter, [])
                            filtered_budget = apply_filters(plan_budget, ch_filter, [])
                            
                            if not filtered_actual.empty and selected_month in filtered_actual.columns:
                                from_total_actual += filtered_actual[selected_month].sum()
                            
                            if not filtered_budget.empty and selected_month in filtered_budget.columns:
                                from_total_budget += filtered_budget[selected_month].sum()
                        
                        # TO側のデータ集計（チャネルフィルタ適用）
                        for plan in stage_def['to_plans']:
                            plan_actual = indicators_actual[indicators_actual['plan'] == plan]
                            plan_budget = indicators_budget[indicators_budget['plan'] == plan]
                            
                            # チャネルフィルタを適用
                            filtered_actual = apply_filters(plan_actual, ch_filter, [])
                            filtered_budget = apply_filters(plan_budget, ch_filter, [])
                            
                            if not filtered_actual.empty and selected_month in filtered_actual.columns:
                                to_total_actual += filtered_actual[selected_month].sum()
                            
                            if not filtered_budget.empty and selected_month in filtered_budget.columns:
                                to_total_budget += filtered_budget[selected_month].sum()
                        
                        # CV率計算
                        cv_rate_actual = (to_total_actual / from_total_actual * 100) if from_total_actual > 0 else 0
                        cv_rate_budget = (to_total_budget / from_total_budget * 100) if from_total_budget > 0 else 0
                        
                        # 月別のCV率トレンドデータを計算
                        month_cols = [col for col in indicators_actual.columns if col.endswith('月')]
                        cv_trend_actual = []
                        cv_trend_budget = []
                        
                        for month in month_cols:
                            # 月別実績CV率計算
                            month_from_actual = 0
                            month_to_actual = 0
                            month_from_budget = 0
                            month_to_budget = 0
                            
                            for plan in stage_def['from_plans']:
                                plan_actual = indicators_actual[indicators_actual['plan'] == plan]
                                plan_budget = indicators_budget[indicators_budget['plan'] == plan]
                                
                                # チャネルフィルタを適用
                                filtered_actual = apply_filters(plan_actual, ch_filter, [])
                                filtered_budget = apply_filters(plan_budget, ch_filter, [])
                                
                                if not filtered_actual.empty and month in filtered_actual.columns:
                                    month_from_actual += filtered_actual[month].sum()
                                
                                if not filtered_budget.empty and month in filtered_budget.columns:
                                    month_from_budget += filtered_budget[month].sum()
                            
                            for plan in stage_def['to_plans']:
                                plan_actual = indicators_actual[indicators_actual['plan'] == plan]
                                plan_budget = indicators_budget[indicators_budget['plan'] == plan]
                                
                                # チャネルフィルタを適用
                                filtered_actual = apply_filters(plan_actual, ch_filter, [])
                                filtered_budget = apply_filters(plan_budget, ch_filter, [])
                                
                                if not filtered_actual.empty and month in filtered_actual.columns:
                                    month_to_actual += filtered_actual[month].sum()
                                
                                if not filtered_budget.empty and month in filtered_budget.columns:
                                    month_to_budget += filtered_budget[month].sum()
                            
                            # 月別CV率
                            month_cv_actual = (month_to_actual / month_from_actual * 100) if month_from_actual > 0 else 0
                            month_cv_budget = (month_to_budget / month_from_budget * 100) if month_from_budget > 0 else 0
                            
                            cv_trend_actual.append(month_cv_actual)
                            cv_trend_budget.append(month_cv_budget)
                        
                        # カード作成（trend_itemと同じスタイル）
                        is_selected = (selected_stage == stage_def['id'])
                        
                        # 実際にCV率データ（分母>0）がある最後の月を探す
                        valid_months = 0
                        for i, month in enumerate(month_cols):
                            # 分母データを確認
                            month_from_actual = 0
                            for plan in stage_def['from_plans']:
                                plan_actual = indicators_actual[indicators_actual['plan'] == plan]
                                filtered_actual = apply_filters(plan_actual, ch_filter, [])
                                if not filtered_actual.empty and month in filtered_actual.columns:
                                    month_from_actual += filtered_actual[month].sum()
                            
                            if month_from_actual > 0:
                                valid_months = i + 1
                        
                        # CV率の計画値を取得（最後の有効月の計画値）
                        cv_budget_rate = 0
                        if cv_trend_budget and valid_months > 0:
                            # 最後の有効月のインデックス（0ベース）
                            last_valid_index = valid_months - 1
                            if last_valid_index < len(cv_trend_budget):
                                cv_budget_rate = cv_trend_budget[last_valid_index]
                        
                        # CV率スパークライン作成（create_dual_sparklineを使用）
                        from components.charts import create_dual_sparkline
                        
                        # CV率の達成率を計算（実績÷計画）
                        if cv_budget_rate > 0 and cv_rate_actual > 0:
                            achievement_rate = (cv_rate_actual / cv_budget_rate) * 100
                        else:
                            achievement_rate = 0
                        
                        sparkline = create_dual_sparkline(
                            cv_trend_actual,
                            cv_trend_budget,
                            achievement_rate,  # 正しい達成率を使用
                            height=42,
                            width=120,
                            enable_hover=True,
                            value_type='percentage',
                            actual_months=valid_months
                        )
                        from components.charts import get_heatmap_color
                        from components.cards import get_performance_class
                        cv_color = get_heatmap_color(achievement_rate)
                        performance_class = get_performance_class(achievement_rate)
                        
                        # trend_itemと完全に同じスタイルのカード作成
                        card = html.Div([
                            html.Div([
                                # 左側：メトリクス表示
                                html.Div([
                                    # 上段：経路名と実績値
                                    html.Div([
                                        html.Div(stage_def['label'], style={
                                            'fontSize': '0.75rem',
                                            'fontWeight': '600',
                                            'color': DARK_COLORS['bg_dark'] if is_selected else DARK_COLORS['text_primary'],
                                            'marginRight': '8px',
                                            'flexShrink': '0'
                                        }),
                                        html.Div(f"{round(cv_rate_actual)}%", style={
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
                                            'color': DARK_COLORS['bg_dark'] if is_selected else get_performance_color(achievement_rate),
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
                        id={'type': 'stage-cv-card', 'stage': stage_def['id']},
                        className=f'performance-card {performance_class} animate-slideIn',
                        **{
                            'role': 'figure',
                            'aria-label': f"{stage_def['label']}: CV率{round(cv_rate_actual)}%" + (" (選択中)" if is_selected else "")
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
                        
                        cards.append(card)
            
            return cards
            
        except Exception as e:
            logger.error(f"Error in update_stage_cv_cards: {str(e)}")
            return []
    
    # ステージ別CV率カードクリックで経路別フィルターを更新
    @app.callback(
        [Output('trend-cv-filter', 'value'),
         Output('stage-cv-filter', 'data')],
        [Input({'type': 'stage-cv-card', 'stage': ALL}, 'n_clicks')],
        [State('stage-cv-filter', 'data'),
         State('trend-cv-filter', 'value')],
        prevent_initial_call=True
    )
    def update_trend_filter_from_stage_card(n_clicks_list, current_stage, current_trend_filter):
        from dash import ctx
        if not ctx.triggered or not any(n_clicks_list):
            return no_update, None  # 現在の値を保持
        
        # クリックされたカードのステージを取得
        triggered_id = ctx.triggered[0]['prop_id']
        
        if 'stage-cv-card' in triggered_id:
            import json
            try:
                card_info = json.loads(triggered_id.split('.')[0])
                stage = card_info.get('stage')
                if stage:
                    # 同じステージが既に選択されている場合は解除
                    if current_stage == stage:
                        return '3to4', None  # デフォルトに戻す
                    else:
                        return stage, stage  # 新しいステージを設定
            except:
                pass
        
        return no_update, None  # 現在の値を保持