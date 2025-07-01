"""
Windows用アイコンファイル（.ico）作成スクリプト
既存のPNGまたはWebPファイルからICOファイルを生成
"""

import os
from PIL import Image

def create_ico_from_image(source_path, output_path='images/w_logo.ico'):
    """画像ファイルからICOファイルを作成"""
    try:
        # 画像を開く
        img = Image.open(source_path)
        
        # RGBAモードに変換（透過をサポート）
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Windows標準のアイコンサイズのリスト
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # 各サイズのアイコンを作成
        icons = []
        for size in icon_sizes:
            # アスペクト比を維持してリサイズ
            icon = img.copy()
            icon.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 正方形のキャンバスを作成（透明背景）
            square_icon = Image.new('RGBA', size, (0, 0, 0, 0))
            
            # 中央に配置
            offset = ((size[0] - icon.width) // 2, (size[1] - icon.height) // 2)
            square_icon.paste(icon, offset, icon)
            
            icons.append(square_icon)
        
        # ICOファイルとして保存
        icons[0].save(output_path, format='ICO', sizes=icon_sizes)
        print(f"ICOファイルを作成しました: {output_path}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def main():
    """メイン処理"""
    # 可能なソースファイル
    possible_sources = [
        'images/w_logo.png',
        'images/w_logo.webp',
        'assets/w_logo.webp'
    ]
    
    # 存在するファイルを探す
    source_file = None
    for source in possible_sources:
        if os.path.exists(source):
            source_file = source
            print(f"ソースファイル発見: {source}")
            break
    
    if not source_file:
        print("エラー: ロゴファイルが見つかりません")
        print("以下のいずれかのファイルが必要です:")
        for source in possible_sources:
            print(f"  - {source}")
        return
    
    # ディレクトリが存在しない場合は作成
    os.makedirs('images', exist_ok=True)
    
    # ICOファイル作成
    if create_ico_from_image(source_file):
        print("\n成功！次のステップ:")
        print("1. build_windows.spec の icon パラメータを更新:")
        print("   icon='images/w_logo.ico',")
        print("2. PyInstallerを実行:")
        print("   pyinstaller build_windows.spec")

if __name__ == "__main__":
    main()