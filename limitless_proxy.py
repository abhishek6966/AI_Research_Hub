import http.server
import socketserver
import urllib.request
import urllib.parse
import ssl
import json

PORT = 8080

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/proxy?url='):
            target_url = urllib.parse.unquote(self.path.split('/proxy?url=')[1])
            print(f"Proxying request to: {target_url}")
            try:
                # Ignore SSL errors for strict government sites
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                # Spoof as a standard browser to bypass basic anti-bot blocks
                req = urllib.request.Request(
                    target_url, 
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9'
                    }
                )
                
                with urllib.request.urlopen(req, context=ctx) as response:
                    content_type = response.getheader('Content-Type', '')
                    
                    # MAGIC PDF CONVERTER: If the website returned HTML instead of a PDF, seamlessly convert it!
                    if 'text/html' in content_type.lower():
                        print(f"Detected HTML webpage instead of PDF! Converting {target_url} to a real PDF...")
                        pdf_api_url = f"https://api.microlink.io/?url={urllib.parse.quote(target_url)}&pdf=true"
                        pdf_req = urllib.request.Request(pdf_api_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(pdf_req, context=ctx) as pdf_res:
                            pdf_data = json.loads(pdf_res.read())
                            pdf_file_url = pdf_data.get('data', {}).get('pdf', {}).get('url')
                            
                            if pdf_file_url:
                                print(f"Successfully converted! Downloading converted PDF: {pdf_file_url}")
                                # Fetch the actual PDF file
                                with urllib.request.urlopen(pdf_file_url, context=ctx) as final_pdf_res:
                                    self.send_response(200)
                                    self.send_header('Access-Control-Allow-Origin', '*')
                                    self.send_header('Content-Type', 'application/pdf')
                                    # Pass content length if available
                                    if final_pdf_res.getheader('Content-Length'):
                                        self.send_header('Content-Length', final_pdf_res.getheader('Content-Length'))
                                    self.end_headers()
                                    
                                    while True:
                                        chunk = final_pdf_res.read(65536)
                                        if not chunk:
                                            break
                                        self.wfile.write(chunk)
                                return
                            else:
                                print("Failed to get PDF URL from conversion API. Returning raw HTML.")
                    
                    # Standard Proxy flow for normal PDFs
                    self.send_response(response.status)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    
                    # Pass through relevant headers (especially Content-Length and Content-Type)
                    for header, value in response.getheaders():
                        if header.lower() not in ['transfer-encoding', 'connection']:
                            self.send_header(header, value)
                    self.end_headers()
                    
                    # Stream the body in chunks to handle massive 100MB+ files perfectly
                    while True:
                        chunk = response.read(65536)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
            except Exception as e:
                print(f"Proxy Error: {str(e)}")
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f"Proxy Error: {str(e)}".encode('utf-8'))
        else:
            super().do_GET()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"=================================================")
        print(f"Limitless Proxy running at http://localhost:{PORT}")
        print(f"=================================================")
        print(f"Keep this terminal open while zipping files in the Research Hub.")
        print(f"Press Ctrl+C to exit.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down proxy...")
