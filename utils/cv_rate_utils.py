"""
CV率計算のユーティリティ関数
タイムラグを考慮したCV率計算を提供
"""
import sys
import os

# パス設定（PyInstaller実行時対応）
if getattr(sys, 'frozen', False):
    # EXE実行時
    application_path = sys._MEIPASS
    sys.path.insert(0, application_path)
else:
    # 開発時
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

from config import CV_RATE_TIME_LAG

def get_cv_rate_denominator_month(current_month, cv_type, channel, month_cols):
    """
    CV率計算の分母となる月を取得
    
    Parameters:
    -----------
    current_month : str
        計算対象の月（例: "5月"）
    cv_type : str
        CV率のタイプ（例: "to商談", "to具体検討", "to内諾", "to獲得"）
    channel : str
        チャネル名（例: "新規web", "新規法人", "新規代理店", "クロスセル"）
    month_cols : list
        利用可能な月のリスト
        
    Returns:
    --------
    str : 分母として使用する月
    """
    # チャネル名を正規化（タイムラグ設定のキーに合わせる）
    normalized_channel = channel
    if channel in ['既存', 'フロー']:
        # 既存とフローはタイムラグ設定がないので、デフォルト（当月）を使用
        return current_month
    
    # タイムラグ設定を取得
    if normalized_channel not in CV_RATE_TIME_LAG:
        # 設定がない場合はデフォルト（当月）を使用
        return current_month
    
    if cv_type not in CV_RATE_TIME_LAG[normalized_channel]:
        # CV率タイプの設定がない場合はデフォルト（当月）を使用
        return current_month
    
    # タイムラグ（月数）を取得
    lag_months = CV_RATE_TIME_LAG[normalized_channel][cv_type]
    
    # 現在の月のインデックスを取得
    if current_month not in month_cols:
        return current_month
    
    current_index = month_cols.index(current_month)
    
    # タイムラグを適用したインデックスを計算
    target_index = current_index - lag_months
    
    # インデックスが有効な範囲内かチェック
    if target_index < 0:
        # 範囲外の場合は最初の月を返す
        return month_cols[0] if month_cols else current_month
    
    return month_cols[target_index]


def calculate_cv_rate_with_lag(from_data, to_data, current_month, cv_type, channel, month_cols):
    """
    タイムラグを考慮してCV率を計算
    
    Parameters:
    -----------
    from_data : DataFrame or Series
        分母となるデータ（前段階のステージ）
    to_data : DataFrame or Series  
        分子となるデータ（後段階のステージ）
    current_month : str
        計算対象の月
    cv_type : str
        CV率のタイプ（例: "to商談", "to具体検討", "to内諾", "to獲得"）
    channel : str
        チャネル名
    month_cols : list
        利用可能な月のリスト
        
    Returns:
    --------
    float : CV率（パーセンテージ）
    """
    # 分母となる月を取得
    denominator_month = get_cv_rate_denominator_month(current_month, cv_type, channel, month_cols)
    
    # 分母の値を取得
    from_value = 0
    if from_data is not None and not from_data.empty and denominator_month in from_data.columns:
        from_value = from_data[denominator_month].sum()
    
    # 分子の値を取得（常に現在の月）
    to_value = 0
    if to_data is not None and not to_data.empty and current_month in to_data.columns:
        to_value = to_data[current_month].sum()
    
    # CV率を計算
    if from_value > 0:
        return (to_value / from_value) * 100
    else:
        return 0


def get_cv_type_from_stage_transition(from_stage, to_stage):
    """
    ステージ遷移からCV率タイプを判定
    
    Parameters:
    -----------
    from_stage : str
        遷移元のステージ
    to_stage : str
        遷移先のステージ
        
    Returns:
    --------
    str : CV率タイプ（例: "to商談", "to具体検討", "to内諾", "to獲得"）
    """
    # ステージ名のマッピング
    stage_mapping = {
        ('リード・アプローチ', '商談'): 'to商談',
        ('商談', '具体検討'): 'to具体検討',
        ('具体検討', '内諾'): 'to内諾',
        ('内諾', '獲得'): 'to獲得'
    }
    
    return stage_mapping.get((from_stage, to_stage), None)


def calculate_cv_rate_trend_with_lag(from_data, to_data, cv_type, channel, month_cols):
    """
    タイムラグを考慮したCV率トレンドデータを計算
    
    Parameters:
    -----------
    from_data : DataFrame
        分母となるデータ（前段階のステージ）
    to_data : DataFrame
        分子となるデータ（後段階のステージ）
    cv_type : str
        CV率のタイプ（例: "to商談", "to具体検討", "to内諾", "to獲得"）
    channel : str
        チャネル名
    month_cols : list
        利用可能な月のリスト
        
    Returns:
    --------
    dict : {'volume_actual': list, 'acq_actual': list} - 月次CV率計算用データ
    """
    cv_trend_data = {
        'volume_actual': [],  # 分母データ（タイムラグ適用済み）
        'acq_actual': []      # 分子データ（当月）
    }
    
    for month in month_cols:
        # 分母となる月を取得（タイムラグ適用）
        denominator_month = get_cv_rate_denominator_month(month, cv_type, channel, month_cols)
        
        # 分母の値を取得（タイムラグ適用後の月）
        from_value = 0
        if from_data is not None and not from_data.empty and denominator_month in from_data.columns:
            from_value = from_data[denominator_month].sum()
        
        # 分子の値を取得（当月）
        to_value = 0
        if to_data is not None and not to_data.empty and month in to_data.columns:
            to_value = to_data[month].sum()
        
        cv_trend_data['volume_actual'].append(from_value)
        cv_trend_data['acq_actual'].append(to_value)
    
    return cv_trend_data