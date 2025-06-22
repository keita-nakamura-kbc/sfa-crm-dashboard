"""
Tab2: 売上・獲得分析のコールバック（新構成）
"""
from dash import Input, Output, State, ALL, html, dcc
import logging

logger = logging.getLogger(__name__)
from data_manager import (
    data_manager, get_dataframe_from_store, apply_filters, should_display_actual_data,
    format_number, clean_channel_names, clean_plan_names, calculate_single_month,
    calculate_cumulative, calculate_kpi_values, get_monthly_trend_data
)
from components.cards import (
    create_performance_card, create_insight_card, get_performance_color
)
from components.charts import create_trend_chart, create_horizontal_bar_chart, create_stacked_bar_chart
from components.loading import create_chart_loading_placeholder, create_skeleton_card
from config import DARK_COLORS, THRESHOLDS

def register_tab2_callbacks(app):
    """Tab2のコールバックを登録（新構成）"""
    
    # 動的タイトル更新（獲得/売上切り替えに応じて）
    @app.callback(
        [Output('main-trend-title', 'children'),
         Output('composition-channel-title', 'children'),
         Output('composition-app-title', 'children'),
         Output('detail-channel-title', 'children'),
         Output('detail-plan-title', 'children')],
        [Input('analysis-type-state', 'data')]
    )
    def update_dynamic_titles(analysis_type):
        if analysis_type == 'acquisition':
            return (
                "獲得数",
                html.Div([
                    html.I(className="fas fa-route", style={'marginRight': '4px'}),
                    html.H3("獲得構成 - 経路別", 
                        **{
                            'role': 'heading',
                            'aria-level': '3'
                        },
                        className='text-subheading',
                        style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                ], className='flex-row items-center'),
                html.Div([
                    html.I(className="fas fa-tasks", style={'marginRight': '4px'}),
                    html.H3("獲得構成 - プラン別", 
                        **{
                            'role': 'heading',
                            'aria-level': '3'
                        },
                        className='text-subheading',
                        style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                ], className='flex-row items-center'),
                html.Div([
                    html.I(className="fas fa-route", style={'marginRight': '4px'}),
                    html.H3("獲得数 - 経路別", 
                        **{
                            'role': 'heading',
                            'aria-level': '3'
                        },
                        className='text-subheading',
                        style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                ], className='flex-row items-center'),
                html.Div([
                    html.I(className="fas fa-tasks", style={'marginRight': '4px'}),
                    html.H3("獲得数 - プラン別", 
                        **{
                            'role': 'heading',
                            'aria-level': '3'
                        },
                        className='text-subheading',
                        style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                ], className='flex-row items-center')
            )
        else:  # revenue
            return (
                "売上高",
                html.Div([
                    html.I(className="fas fa-route", style={'marginRight': '4px'}),
                    html.H3("売上構成 - 経路別", 
                        **{
                            'role': 'heading',
                            'aria-level': '3'
                        },
                        className='text-subheading',
                        style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                ], className='flex-row items-center'),
                html.Div([
                    html.I(className="fas fa-tasks", style={'marginRight': '4px'}),
                    html.H3("売上構成 - プラン別", 
                        **{
                            'role': 'heading',
                            'aria-level': '3'
                        },
                        className='text-subheading',
                        style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                ], className='flex-row items-center'),
                html.Div([
                    html.I(className="fas fa-route", style={'marginRight': '4px'}),
                    html.H3("売上高 - 経路別", 
                        **{
                            'role': 'heading',
                            'aria-level': '3'
                        },
                        className='text-subheading',
                        style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                ], className='flex-row items-center'),
                html.Div([
                    html.I(className="fas fa-tasks", style={'marginRight': '4px'}),
                    html.H3("売上高 - プラン別", 
                        **{
                            'role': 'heading',
                            'aria-level': '3'
                        },
                        className='text-subheading',
                        style={'margin': '0', 'fontSize': '0.8rem', 'lineHeight': '1.1'})
                ], className='flex-row items-center')
            )
    
    # メイントレンドチャート（獲得/売上切り替え対応）
    @app.callback(
        [Output('main-trend-chart', 'figure'),
         Output('main-trend-kpi-summary', 'children')],
        [Input('month-selector', 'value'),
         Input('btn-plan-ratio', 'className'),
         Input('btn-cumulative', 'className'),
         Input('channel-filter', 'value'),
         Input('plan-filter', 'value'),
         Input('channel-filter-tab2', 'value'),
         Input('plan-filter-tab2', 'value'),
         Input('analysis-type-state', 'data')]
    )
    def update_main_trend_chart(selected_month, plan_ratio_class, cumulative_class,
                               channel_filter, plan_filter, channel_filter_tab2, plan_filter_tab2, analysis_type):
        data = data_manager.get_data()
        
        # データタイプに応じてsalesまたはacquisitionを選択
        data_key = 'sales' if analysis_type == 'revenue' else 'acquisition'
        value_type = 'currency' if analysis_type == 'revenue' else 'count'
        
        if not data or data_key not in data:
            from components.charts import create_empty_chart
            return create_empty_chart(), []
        
        try:
            # データタイプと期間タイプの判定
            data_type = 'plan_ratio' if 'active' in plan_ratio_class else 'plan_diff'
            period_type = 'cumulative' if 'active' in cumulative_class else 'single'
            
            actual_df = get_dataframe_from_store(data, data_key, 'actual')
            budget_df = get_dataframe_from_store(data, data_key, 'budget')
            
            if actual_df is not None and budget_df is not None:
                month_cols = [col for col in actual_df.columns if col.endswith('月')]
                
                # Tab2専用のフィルターを使用
                current_channel_filter = [channel_filter_tab2] if channel_filter_tab2 else channel_filter
                current_plan_filter = [plan_filter_tab2] if plan_filter_tab2 else plan_filter
                
                # フィルタリングはcalculate_kpi_values内で行われるため、ここでは不要
                if actual_df is not None and budget_df is not None:
                    # 月次データ取得（calculate_kpi_values()と同じロジックを使用）
                    all_months = [f"{i}月" for i in range(1, 13)]
                    budget_totals = []
                    actual_totals = []
                    actual_months = []
                    
                    # 各月のデータをcalculate_kpi_values()を使用して取得
                    # 注意: calculate_kpi_values()は既に期間タイプ（単月/累月）を考慮した値を返す
                    for month in all_months:
                        if month in month_cols:
                            # calculate_kpi_values()と同じ計算方法を使用（単月値を取得）
                            actual_val, budget_val = calculate_kpi_values(
                                data, data_key, month, data_type, 'single',  # 常に単月値を取得
                                current_channel_filter, current_plan_filter
                            )
                            
                            budget_totals.append(format_number(budget_val))
                            
                            if should_display_actual_data(actual_df, month_cols, month):
                                actual_months.append(month)
                                actual_totals.append(format_number(actual_val))
                        else:
                            budget_totals.append(0)
                    
                    # 期間変換（単月値から累月値への変換が必要な場合のみ）
                    if period_type == 'cumulative':
                        if len(actual_totals) > 0:
                            actual_totals = calculate_cumulative(actual_totals)
                        budget_totals = calculate_cumulative(budget_totals)
                    
                    # 達成率計算
                    achievement_rates = []
                    if data_type == 'plan_ratio' and actual_months:
                        for i, month in enumerate(actual_months):
                            if month in all_months:
                                month_idx = all_months.index(month)
                                actual_val = actual_totals[i]
                                budget_val = budget_totals[month_idx]
                                if budget_val > 0:
                                    achievement_rates.append((actual_val / budget_val) * 100)
                    
                    # チャート作成
                    fig = create_trend_chart(
                        all_months, budget_totals, actual_totals, actual_months,
                        achievement_rates if data_type == 'plan_ratio' else None,
                        selected_month, value_type, None, data_type
                    )
                    
                    # KPIサマリー
                    kpi_summary = []
                    if selected_month in actual_months:
                        month_idx = actual_months.index(selected_month)
                        actual_current = actual_totals[month_idx]
                        budget_idx = all_months.index(selected_month)
                        budget_current = budget_totals[budget_idx]
                        achievement_rate = (actual_current / budget_current * 100) if budget_current > 0 else 0
                        
                        if analysis_type == 'revenue':
                            kpi_summary = [
                                html.Div([
                                    html.Span(f"{round(achievement_rate)}%", style={
                                        'fontSize': '1.5rem',
                                        'fontWeight': '700',
                                        'color': get_performance_color(achievement_rate)
                                    }),
                                    html.Span(" 計画比", style={
                                        'fontSize': '0.875rem',
                                        'color': DARK_COLORS['text_muted']
                                    })
                                ]),
                                html.Div([
                                    html.Span(f"¥{actual_current/1000:.1f}K", style={
                                        'fontSize': '1.5rem',
                                        'fontWeight': '700',
                                        'color': DARK_COLORS['text_primary']
                                    }),
                                    html.Span(f" / ¥{budget_current/1000:.1f}K", style={
                                        'fontSize': '0.875rem',
                                        'color': DARK_COLORS['text_muted']
                                    })
                                ])
                            ]
                        else:  # acquisition
                            kpi_summary = [
                                html.Div([
                                    html.Span(f"{round(achievement_rate)}%", style={
                                        'fontSize': '1.5rem',
                                        'fontWeight': '700',
                                        'color': get_performance_color(achievement_rate)
                                    }),
                                    html.Span(" 計画比", style={
                                        'fontSize': '0.875rem',
                                        'color': DARK_COLORS['text_muted']
                                    })
                                ]),
                                html.Div([
                                    html.Span(f"{actual_current:.0f}", style={
                                        'fontSize': '1.5rem',
                                        'fontWeight': '700',
                                        'color': DARK_COLORS['text_primary']
                                    }),
                                    html.Span(f" / {budget_current:.0f}件", style={
                                        'fontSize': '0.875rem',
                                        'color': DARK_COLORS['text_muted']
                                    })
                                ])
                            ]
                    
                    return fig, kpi_summary
            
            from components.charts import create_empty_chart
            return create_empty_chart(), []
            
        except Exception as e:
            logger.error(f"Error in update_main_trend_chart: {str(e)}")
            from components.charts import create_empty_chart
            return create_empty_chart(f"エラー: {str(e)}"), []
    
    # 継続率カード（変更なし）
    @app.callback(
        Output('retention-rate-cards', 'children'),
        [Input('month-selector', 'value')]
    )
    def update_retention_rate_cards(selected_month):
        data = data_manager.get_data()
        if not data or not selected_month:
            return []
        
        try:
            cards = []
            
            if 'retention' in data:
                actual_df = get_dataframe_from_store(data, 'retention', 'actual')
                
                if actual_df is not None and not actual_df.empty:
                    channels = clean_channel_names(actual_df['channel'].unique())
                    
                    for channel in channels:
                        channel_data = actual_df[actual_df['channel'].str.contains(channel, na=False)]
                        
                        if not channel_data.empty and selected_month in channel_data.columns:
                            retention_rate = channel_data[selected_month].mean()
                            
                            cards.append(html.Div([
                                html.Div(channel, style={
                                    'fontSize': '0.7rem',
                                    'fontWeight': '600',
                                    'color': DARK_COLORS['text_primary'],
                                    'marginBottom': '2px'
                                }),
                                html.Div(f"{round(retention_rate)}%", style={
                                    'fontSize': '0.9rem',
                                    'fontWeight': '700',
                                    'color': get_performance_color(retention_rate * 5)  # 0-20% → 0-100%でスケール
                                })
                            ], style={
                                'padding': '4px',
                                'backgroundColor': DARK_COLORS['bg_hover'],
                                'borderRadius': '4px',
                                'marginBottom': '4px',
                                'textAlign': 'center'
                            }))
            
            return cards
            
        except Exception as e:
            logger.error(f"Error in update_retention_rate_cards: {str(e)}")
            return []
    
    # 客単価分析カード（既存のロジックを使用、IDは変更なし）
    @app.callback(
        Output('unit-price-analysis-cards', 'children'),
        [Input('month-selector', 'value'),
         Input('btn-plan-ratio', 'className'),
         Input('btn-cumulative', 'className'),
         Input('channel-filter', 'value'),
         Input('plan-filter', 'value'),
         Input('channel-filter-tab2', 'value'),
         Input('plan-filter-tab2', 'value')]
    )
    def update_unit_price_analysis_cards(selected_month, plan_ratio_class, cumulative_class,
                                       channel_filter, plan_filter, channel_filter_tab2, plan_filter_tab2):
        data = data_manager.get_data()
        if not data or not selected_month:
            return []
        
        try:
            data_type = 'plan_ratio' if 'active' in plan_ratio_class else 'plan_diff'
            period_type = 'cumulative' if 'active' in cumulative_class else 'single'
            
            cards_data = []
            
            if 'unit_price' in data:
                actual_df = get_dataframe_from_store(data, 'unit_price', 'actual')
                budget_df = get_dataframe_from_store(data, 'unit_price', 'budget')
                
                if actual_df is not None and budget_df is not None:
                    channels = clean_channel_names(actual_df['channel'].unique())
                    
                    for channel in channels:
                        # Tab2専用のフィルターを使用
                        current_channel_filter = [channel_filter_tab2] if channel_filter_tab2 else channel_filter
                        current_plan_filter = [plan_filter_tab2] if plan_filter_tab2 else plan_filter
                        # 客単価は個別チャネル表示なので、現在のチャネルのみを使用
                        actual_val, budget_val = calculate_kpi_values(
                            data, 'unit_price', selected_month, data_type, period_type,
                            [channel], current_plan_filter
                        )
                        
                        # 常にカードを追加
                        achievement = (actual_val / budget_val * 100) if budget_val > 0 else 0
                        
                        # 月別トレンドデータを取得
                        trend_data = get_monthly_trend_data(
                            data, 'unit_price', data_type, period_type,
                            channel_filter=[channel],
                            plan_filter=current_plan_filter,
                            target_item=channel
                        )
                        
                        cards_data.append({
                            'category': channel,
                            'value': f"¥{actual_val/1000:.1f}K" if actual_val >= 1000 else f"¥{actual_val:.0f}",
                            'achievement_rate': achievement,
                            'budget_value': f"¥{budget_val/1000:.1f}K" if budget_val >= 1000 else f"¥{budget_val:.0f}",
                            'trend_data': trend_data,
                            'plan_diff': actual_val - budget_val
                        })
            
            # ソート処理
            if data_type == 'plan_ratio':
                # 計画比の場合：0%・N/Aを最下段に、その他は達成率で昇順
                cards_data.sort(key=lambda x: (x['achievement_rate'] == 0, x['achievement_rate'] if x['achievement_rate'] > 0 else float('inf')))
            else:
                # 計画差の場合：計画差で昇順（低い順）
                cards_data.sort(key=lambda x: x['plan_diff'])
            
            # show_metricsの設定
            show_type = 'diff' if data_type == 'plan_diff' else 'ratio'
            
            # カードを通常のコンテナに配置（クリック可能、選択状態を反映）
            cards = []
            for card in cards_data:
                is_selected = (channel_filter_tab2 == card['category'])
                card_id = {'type': 'unit-price-channel-card', 'channel': card['category']}
                cards.append(create_performance_card(
                    **card, 
                    show_metrics=show_type,
                    is_clickable=True,
                    card_id=card_id,
                    is_selected=is_selected
                ))
            return cards
            
        except Exception as e:
            logger.error(f"Error in update_unit_price_analysis_cards: {str(e)}")
            return []
    
    # 構成チャート（経路別）- 獲得/売上切り替え対応
    @app.callback(
        Output('composition-channel-chart', 'figure'),
        [Input('month-selector', 'value'),
         Input('btn-plan-ratio', 'className'),
         Input('btn-cumulative', 'className'),
         Input('plan-filter', 'value'),
         Input('plan-filter-tab2', 'value'),
         Input('analysis-type-state', 'data')]
    )
    def update_composition_channel_chart(selected_month, plan_ratio_class, cumulative_class,
                                       plan_filter, plan_filter_tab2, analysis_type):
        data = data_manager.get_data()
        
        # データタイプに応じてsalesまたはacquisitionを選択
        data_key = 'sales' if analysis_type == 'revenue' else 'acquisition'
        
        if not data or data_key not in data:
            from components.charts import create_empty_chart
            return create_empty_chart()
        
        try:
            # データタイプと期間タイプの判定
            data_type = 'plan_ratio' if 'active' in plan_ratio_class else 'plan_diff'
            period_type = 'cumulative' if 'active' in cumulative_class else 'single'
            
            actual_df = get_dataframe_from_store(data, data_key, 'actual')
            budget_df = get_dataframe_from_store(data, data_key, 'budget')
            
            if actual_df is not None and budget_df is not None:
                # Tab2専用のプランフィルターを使用
                current_plan_filter = [plan_filter_tab2] if plan_filter_tab2 else plan_filter
                
                # 各チャネルごとのデータを取得
                channels = clean_channel_names(actual_df['channel'].unique())
                data_dict = {'actual': {}, 'budget': {}}
                
                # 各チャネルごとのデータを取得（calculate_kpi_values()と同じロジックを使用）
                for channel in channels:
                    # calculate_kpi_values()と同じ計算方法を使用
                    actual_val, budget_val = calculate_kpi_values(
                        data, data_key, selected_month, data_type, period_type,
                        [channel], current_plan_filter
                    )
                    
                    # フォーマット処理
                    data_dict['actual'][channel] = format_number(actual_val) if actual_val > 0 else 0
                    data_dict['budget'][channel] = format_number(budget_val) if budget_val > 0 else 0
                
                # チャート作成（横棒グラフ、積み上げ比較モード）
                value_type = 'currency' if analysis_type == 'revenue' else 'count'
                return create_stacked_bar_chart(
                    categories=[selected_month],
                    data_dict=data_dict,
                    selected_category=selected_month,
                    height=None,
                    horizontal=True,
                    comparison_mode=True,
                    value_type=value_type
                )
            
            from components.charts import create_empty_chart
            return create_empty_chart()
            
        except Exception as e:
            logger.error(f"Error in update_composition_channel_chart: {str(e)}")
            from components.charts import create_empty_chart
            return create_empty_chart(f"エラー: {str(e)}")
    
    # 構成チャート（アプリ別）- 獲得/売上切り替え対応
    @app.callback(
        Output('composition-app-chart', 'figure'),
        [Input('month-selector', 'value'),
         Input('btn-plan-ratio', 'className'),
         Input('btn-cumulative', 'className'),
         Input('channel-filter', 'value'),
         Input('channel-filter-tab2', 'value'),
         Input('analysis-type-state', 'data')]
    )
    def update_composition_app_chart(selected_month, plan_ratio_class, cumulative_class,
                                   channel_filter, channel_filter_tab2, analysis_type):
        data = data_manager.get_data()
        
        # データタイプに応じてsalesまたはacquisitionを選択
        data_key = 'sales' if analysis_type == 'revenue' else 'acquisition'
        
        if not data or data_key not in data:
            from components.charts import create_empty_chart
            return create_empty_chart()
        
        try:
            # データタイプと期間タイプの判定
            data_type = 'plan_ratio' if 'active' in plan_ratio_class else 'plan_diff'
            period_type = 'cumulative' if 'active' in cumulative_class else 'single'
            
            actual_df = get_dataframe_from_store(data, data_key, 'actual')
            budget_df = get_dataframe_from_store(data, data_key, 'budget')
            
            if actual_df is not None and budget_df is not None:
                # Tab2専用のチャネルフィルターを使用
                current_channel_filter = [channel_filter_tab2] if channel_filter_tab2 else channel_filter
                
                # 各プラン（アプリ）ごとのデータを取得
                plans = clean_plan_names(actual_df['plan'].unique())
                data_dict = {'actual': {}, 'budget': {}}
                
                # 各プランごとのデータを取得（calculate_kpi_values()と同じロジックを使用）
                for plan in plans:
                    # calculate_kpi_values()と同じ計算方法を使用
                    actual_val, budget_val = calculate_kpi_values(
                        data, data_key, selected_month, data_type, period_type,
                        current_channel_filter, [plan]
                    )
                    
                    # フォーマット処理
                    data_dict['actual'][plan] = format_number(actual_val) if actual_val > 0 else 0
                    data_dict['budget'][plan] = format_number(budget_val) if budget_val > 0 else 0
                
                # チャート作成（横棒グラフ、積み上げ比較モード）
                value_type = 'currency' if analysis_type == 'revenue' else 'count'
                fig = create_stacked_bar_chart(
                    categories=[selected_month],
                    data_dict=data_dict,
                    selected_category=selected_month,
                    height=None,
                    horizontal=True,
                    comparison_mode=True,
                    value_type=value_type
                )
                
                return fig
            
            from components.charts import create_empty_chart
            return create_empty_chart()
            
        except Exception as e:
            logger.error(f"Error in update_composition_app_chart: {str(e)}")
            from components.charts import create_empty_chart
            return create_empty_chart(f"エラー: {str(e)}")
    
    # 詳細カードリスト（経路別）- 獲得/売上切り替え対応
    @app.callback(
        Output('channel-cards', 'children'),
        [Input('month-selector', 'value'),
         Input('btn-plan-ratio', 'className'),
         Input('btn-cumulative', 'className'),
         Input('channel-filter', 'value'),
         Input('plan-filter', 'value'),
         Input('channel-filter-tab2', 'value'),
         Input('plan-filter-tab2', 'value'),
         Input('analysis-type-state', 'data')]
    )
    def update_channel_cards(selected_month, plan_ratio_class, cumulative_class,
                           channel_filter, plan_filter, channel_filter_tab2, plan_filter_tab2, analysis_type):
        data = data_manager.get_data()
        
        # データタイプに応じてsalesまたはacquisitionを選択
        data_key = 'sales' if analysis_type == 'revenue' else 'acquisition'
        
        if not data or not selected_month:
            return []
        
        try:
            data_type = 'plan_ratio' if 'active' in plan_ratio_class else 'plan_diff'
            period_type = 'cumulative' if 'active' in cumulative_class else 'single'
            
            cards_data = []
            
            if data_key in data:
                actual_df = get_dataframe_from_store(data, data_key, 'actual')
                budget_df = get_dataframe_from_store(data, data_key, 'budget')
                
                if actual_df is not None and budget_df is not None:
                    channels = clean_channel_names(actual_df['channel'].unique())
                    
                    for channel in channels:
                        # Tab2専用のフィルターを使用
                        current_channel_filter = [channel_filter_tab2] if channel_filter_tab2 else channel_filter
                        current_plan_filter = [plan_filter_tab2] if plan_filter_tab2 else plan_filter
                        # 経路別は個別チャネル表示なので、現在のチャネルのみを使用
                        actual_val, budget_val = calculate_kpi_values(
                            data, data_key, selected_month, data_type, period_type,
                            [channel], current_plan_filter
                        )
                        
                        # 常にカードを追加
                        achievement = (actual_val / budget_val * 100) if budget_val > 0 else 0
                        
                        # 月別トレンドデータを取得
                        trend_data = get_monthly_trend_data(
                            data, data_key, data_type, period_type,
                            channel_filter=[channel],
                            plan_filter=current_plan_filter,
                            target_item=channel
                        )
                        
                        # 値の表示形式を分析タイプに応じて調整
                        if analysis_type == 'revenue':
                            value_display = f"¥{actual_val/1000:.1f}K" if actual_val >= 1000 else f"¥{actual_val:.0f}"
                            budget_display = f"¥{budget_val/1000:.1f}K" if budget_val >= 1000 else f"¥{budget_val:.0f}"
                        else:
                            value_display = f"{actual_val:.0f}件"
                            budget_display = f"{budget_val:.0f}件"
                        
                        cards_data.append({
                            'category': channel,
                            'value': value_display,
                            'achievement_rate': achievement,
                            'budget_value': budget_display,
                            'trend_data': trend_data,
                            'plan_diff': actual_val - budget_val
                        })
            
            # ソート処理
            if data_type == 'plan_ratio':
                # 計画比の場合：0%・N/Aを最下段に、その他は達成率で昇順
                cards_data.sort(key=lambda x: (x['achievement_rate'] == 0, x['achievement_rate'] if x['achievement_rate'] > 0 else float('inf')))
            else:
                # 計画差の場合：計画差で昇順（低い順）
                cards_data.sort(key=lambda x: x['plan_diff'])
            
            # show_metricsの設定
            show_type = 'diff' if data_type == 'plan_diff' else 'ratio'
            
            # カードを通常のコンテナに配置（クリック可能、選択状態を反映）
            cards = []
            for card in cards_data:
                is_selected = (channel_filter_tab2 == card['category'])
                card_type = f'{analysis_type}-channel-card'
                card_id = {'type': card_type, 'channel': card['category']}
                cards.append(create_performance_card(
                    **card, 
                    show_metrics=show_type,
                    is_clickable=True,
                    card_id=card_id,
                    is_selected=is_selected
                ))
            return cards
            
        except Exception as e:
            logger.error(f"Error in update_channel_cards: {str(e)}")
            return []
    
    # 詳細カードリスト（プラン別）- 獲得/売上切り替え対応
    @app.callback(
        Output('plan-cards', 'children'),
        [Input('month-selector', 'value'),
         Input('btn-plan-ratio', 'className'),
         Input('btn-cumulative', 'className'),
         Input('channel-filter', 'value'),
         Input('plan-filter', 'value'),
         Input('channel-filter-tab2', 'value'),
         Input('plan-filter-tab2', 'value'),
         Input('analysis-type-state', 'data')]
    )
    def update_plan_cards(selected_month, plan_ratio_class, cumulative_class,
                         channel_filter, plan_filter, channel_filter_tab2, plan_filter_tab2, analysis_type):
        data = data_manager.get_data()
        
        # データタイプに応じてsalesまたはacquisitionを選択
        data_key = 'sales' if analysis_type == 'revenue' else 'acquisition'
        
        if not data or not selected_month:
            return []
        
        try:
            data_type = 'plan_ratio' if 'active' in plan_ratio_class else 'plan_diff'
            period_type = 'cumulative' if 'active' in cumulative_class else 'single'
            
            cards_data = []
            
            if data_key in data:
                actual_df = get_dataframe_from_store(data, data_key, 'actual')
                budget_df = get_dataframe_from_store(data, data_key, 'budget')
                
                if actual_df is not None and budget_df is not None:
                    plans = clean_plan_names(actual_df['plan'].unique())
                    
                    for plan in plans:
                        # Tab2専用のフィルターを使用
                        current_channel_filter = [channel_filter_tab2] if channel_filter_tab2 else channel_filter
                        current_plan_filter = [plan_filter_tab2] if plan_filter_tab2 else plan_filter
                        # プラン別は個別プラン表示なので、現在のプランのみを使用
                        actual_val, budget_val = calculate_kpi_values(
                            data, data_key, selected_month, data_type, period_type,
                            current_channel_filter, [plan]
                        )
                        
                        # 常にカードを追加
                        achievement = (actual_val / budget_val * 100) if budget_val > 0 else 0
                        
                        # 月別トレンドデータを取得
                        trend_data = get_monthly_trend_data(
                            data, data_key, data_type, period_type,
                            channel_filter=current_channel_filter,
                            plan_filter=[plan],
                            target_item=plan
                        )
                        
                        # 値の表示形式を分析タイプに応じて調整
                        if analysis_type == 'revenue':
                            value_display = f"¥{actual_val/1000:.1f}K" if actual_val >= 1000 else f"¥{actual_val:.0f}"
                            budget_display = f"¥{budget_val/1000:.1f}K" if budget_val >= 1000 else f"¥{budget_val:.0f}"
                        else:
                            value_display = f"{actual_val:.0f}件"
                            budget_display = f"{budget_val:.0f}件"
                        
                        cards_data.append({
                            'category': plan,
                            'value': value_display,
                            'achievement_rate': achievement,
                            'budget_value': budget_display,
                            'trend_data': trend_data,
                            'plan_diff': actual_val - budget_val
                        })
            
            # ソート処理
            if data_type == 'plan_ratio':
                # 計画比の場合：0%・N/Aを最下段に、その他は達成率で昇順
                cards_data.sort(key=lambda x: (x['achievement_rate'] == 0, x['achievement_rate'] if x['achievement_rate'] > 0 else float('inf')))
            else:
                # 計画差の場合：計画差で昇順（低い順）
                cards_data.sort(key=lambda x: x['plan_diff'])
            
            # show_metricsの設定
            show_type = 'diff' if data_type == 'plan_diff' else 'ratio'
            
            # カードを通常のコンテナに配置（クリック可能、選択状態を反映）
            cards = []
            for card in cards_data:
                is_selected = (plan_filter_tab2 == card['category'])
                card_type = f'{analysis_type}-plan-card'
                card_id = {'type': card_type, 'plan': card['category']}
                cards.append(create_performance_card(
                    **card, 
                    show_metrics=show_type,
                    is_clickable=True,
                    card_id=card_id,
                    is_selected=is_selected
                ))
            return cards
            
        except Exception as e:
            logger.error(f"Error in update_plan_cards: {str(e)}")
            return []
    
    # KPIカードクリックでチャネルフィルターを設定/解除（Tab2）
    @app.callback(
        Output('channel-filter-tab2', 'value'),
        [Input({'type': 'revenue-channel-card', 'channel': ALL}, 'n_clicks'),
         Input({'type': 'acquisition-channel-card', 'channel': ALL}, 'n_clicks'),
         Input({'type': 'unit-price-channel-card', 'channel': ALL}, 'n_clicks')],
        [State('channel-filter-tab2', 'value')],
        prevent_initial_call=True
    )
    def update_channel_filter_from_tab2_card(revenue_clicks, acquisition_clicks, unit_price_clicks, current_filter):
        from dash import ctx
        if not ctx.triggered or not any(revenue_clicks + acquisition_clicks + unit_price_clicks):
            return current_filter
        
        # クリックされたカードのチャネルを取得
        triggered_id = ctx.triggered[0]['prop_id']
        
        if any(card_type in triggered_id for card_type in ['revenue-channel-card', 'acquisition-channel-card', 'unit-price-channel-card']):
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
    
    # KPIカードクリックでプランフィルターを設定/解除（Tab2）
    @app.callback(
        Output('plan-filter-tab2', 'value'),
        [Input({'type': 'revenue-plan-card', 'plan': ALL}, 'n_clicks'),
         Input({'type': 'acquisition-plan-card', 'plan': ALL}, 'n_clicks')],
        [State('plan-filter-tab2', 'value')],
        prevent_initial_call=True
    )
    def update_plan_filter_from_tab2_card(revenue_clicks, acquisition_clicks, current_filter):
        from dash import ctx
        if not ctx.triggered or not any(revenue_clicks + acquisition_clicks):
            return current_filter
        
        # クリックされたカードのプランを取得
        triggered_id = ctx.triggered[0]['prop_id']
        
        if any(card_type in triggered_id for card_type in ['revenue-plan-card', 'acquisition-plan-card']):
            # JSONパースして プラン名を取得
            import json
            try:
                card_info = json.loads(triggered_id.split('.')[0])
                plan = card_info.get('plan')
                if plan:
                    # 同じプランが既に選択されている場合はフィルターを解除
                    if current_filter == plan:
                        return None  # フィルター解除
                    else:
                        return plan  # 新しいプランを設定
            except:
                pass
        
        return current_filter