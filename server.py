import http.server
import urllib.request
import json
import os

PORT = 8080
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SINA_URL = 'https://hq.sinajs.cn/list=sh000001'

def fetch_sh_index():
    """返回 {price, pct, date, time}"""
    req = urllib.request.Request(SINA_URL, headers={
        'Referer': 'https://finance.sina.com.cn/',
        'User-Agent': 'Mozilla/5.0',
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = r.read()
    text = raw.decode('gbk')
    parts = text.split('"')[1].split(',')
    prev_close = float(parts[2])
    current = float(parts[3])
    pct = (current - prev_close) / prev_close * 100
    return {
        'price': current,
        'pct': round(pct, 2),
        'date': parts[-4],
        'time': parts[-3],
    }

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api':
            try:
                data = fetch_sh_index()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            super().do_GET()

if __name__ == '__main__':
    os.chdir(THIS_DIR)
    print(f'📊 吴老师心情指数 → http://192.168.3.201:{PORT}')
    try:
        http.server.HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print('\n关闭')
