import http.server
import socketserver
import urllib.request
import urllib.parse
import ssl
import json
import re

PORT = 8080

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
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

    def do_POST(self):
        if self.path == '/search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = f"{data.get('company')} {data.get('docType')} filetype:pdf OR filetype:html"
            api_key = data.get('apiKey')
            
            # Step 1: DuckDuckGo Lite Scrape
            try:
                url = "https://lite.duckduckgo.com/lite/"
                req_data = urllib.parse.urlencode({'q': query}).encode('utf-8')
                req = urllib.request.Request(url, data=req_data, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded'
                })
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, context=ctx) as response:
                    html = response.read().decode('utf-8')
                
                # Extract results using regex
                links_raw = re.findall(r"<a rel="nofollow" href="([^"]+)" class='result-link'>(.*?)</a>", html, re.DOTALL)
                snippets_raw = re.findall(r"<td class='result-snippet'>(.*?)</td>", html, re.DOTALL)
                
                results = []
                for i in range(min(len(links_raw), 15)):
                    url, title = links_raw[i]
                    snippet = snippets_raw[i] if i < len(snippets_raw) else ""
                    # clean HTML tags from title/snippet
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                    results.append({"title": title, "url": url, "snippet": snippet})
                    
            except Exception as e:
                print(f"Scrape Error: {str(e)}")
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Search failed: {str(e)}"}).encode('utf-8'))
                return

            # Step 2: Groq API Evaluation
            if not api_key:
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"results": results[:5]}).encode('utf-8'))
                return

            try:
                prompt = f"Evaluate these search results for the company '{data.get('company')}' and document type '{data.get('docType')}'. Return ONLY a JSON array of the 5 most relevant objects containing 'title', 'url', and 'snippet'. Do not return markdown, just the raw JSON array.

Results: {json.dumps(results)}"
                
                groq_req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=json.dumps({
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1
                    }).encode('utf-8'),
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                with urllib.request.urlopen(groq_req, context=ctx) as response:
                    groq_res = json.loads(response.read().decode('utf-8'))
                    answer = groq_res['choices'][0]['message']['content'].strip()
                    # Strip markdown code blocks if present
                    if answer.startswith('```json'): answer = answer[7:]
                    if answer.startswith('```'): answer = answer[3:]
                    if answer.endswith('```'): answer = answer[:-3]
                    
                    final_results = json.loads(answer.strip())
                    
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"results": final_results}).encode('utf-8'))
                
            except Exception as e:
                print(f"Groq Error: {str(e)}")
                # Fallback to pure scrape results if LLM fails
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"results": results[:5], "warning": "Groq API failed, showing raw results."}).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"=================================================")
        print(f"🚀 Limitless Proxy running at http://localhost:{PORT}")
        print(f"=================================================")
        print(f"Keep this terminal open while zipping files in the Research Hub.")
        print(f"Press Ctrl+C to exit.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down proxy...")
