"""
TradingVolt Web Portal Server
Run this script to serve the TradingVolt Quantitative Research Portal locally.
"""
import http.server
import socketserver
import webbrowser
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n========================================================")
        print(f"  [+] TRADINGVOLT QUANTITATIVE RESEARCH PORTAL ")
        print(f"========================================================")
        print(f"  Servidor local activo en: {url}")
        print(f"  Presiona Ctrl+C para detener el servidor.\n")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")

if __name__ == '__main__':
    run()
