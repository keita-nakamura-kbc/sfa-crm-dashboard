"""
Microsoft Edge用の互換性チェックとデバッグスクリプト
"""

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# シンプルなテストアプリケーション
app = dash.Dash(__name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
    ]
)

app.layout = html.Div([
    html.H1("Edge互換性テスト", style={'textAlign': 'center', 'margin': '20px'}),
    html.Div([
        html.P("このページが正しく表示されていれば、基本的なDash機能は動作しています。"),
        html.Hr(),
        html.H3("チェック項目:"),
        html.Ul([
            html.Li("✓ ページが読み込まれた"),
            html.Li("✓ テキストが表示されている"),
            html.Li("✓ スタイルが適用されている"),
        ]),
        dcc.Graph(
            id='test-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'テスト'},
                ],
                'layout': {
                    'title': 'テストグラフ'
                }
            }
        )
    ], style={'padding': '20px', 'maxWidth': '800px', 'margin': '0 auto'})
])

if __name__ == '__main__':
    import sys
    import webbrowser
    import threading
    import time
    
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:8051')
    
    if getattr(sys, 'frozen', False):
        print("Edge互換性テストを開始...")
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    app.run_server(debug=False, port=8051, host='127.0.0.1')