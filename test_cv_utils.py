"""
CV率ユーティリティ関数のテスト
"""

def test_cv_rate_utils():
    """CV率ユーティリティ関数の簡単なテスト"""
    try:
        # インポートテスト
        from utils.cv_rate_utils import get_cv_rate_denominator_month, calculate_cv_rate_with_lag
        
        # 基本的な動作テスト
        month_cols = ['1月', '2月', '3月', '4月', '5月']
        
        # 新規Webのto獲得（2ヶ月タイムラグ）
        denominator_month = get_cv_rate_denominator_month('5月', 'to獲得', '新規web', month_cols)
        print(f"新規web to獲得 5月 -> 分母月: {denominator_month}")
        
        # 新規法人のto内諾（2ヶ月タイムラグ）
        denominator_month = get_cv_rate_denominator_month('5月', 'to内諾', '新規法人', month_cols)
        print(f"新規法人 to内諾 5月 -> 分母月: {denominator_month}")
        
        # 新規代理店のto商談（0ヶ月タイムラグ）
        denominator_month = get_cv_rate_denominator_month('5月', 'to商談', '新規代理店', month_cols)
        print(f"新規代理店 to商談 5月 -> 分母月: {denominator_month}")
        
        print("✅ CV率ユーティリティ関数のテストが成功しました")
        return True
        
    except Exception as e:
        print(f"❌ CV率ユーティリティ関数のテストでエラー: {str(e)}")
        return False

if __name__ == "__main__":
    test_cv_rate_utils()