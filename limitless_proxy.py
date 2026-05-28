import http.server
import socketserver
import urllib.request
import urllib.parse
import ssl
import json
import re
import os

# ── Port: Render injects PORT env var; fall back to 8080 for local use ──────
PORT = int(os.environ.get('PORT', 8080))

# ── Groq API key pool — loaded from .env (never committed to git) ──────────
def _load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())
_load_env()

# Collect all GROQ_API_KEY_1, GROQ_API_KEY_2, ... keys in order
GROQ_API_KEYS = []
for _i in range(1, 20):
    _k = os.environ.get(f'GROQ_API_KEY_{_i}', '')
    if _k:
        GROQ_API_KEYS.append(_k)
# Also accept the plain GROQ_API_KEY for backwards compatibility
_plain = os.environ.get('GROQ_API_KEY', '')
if _plain and _plain not in GROQ_API_KEYS:
    GROQ_API_KEYS.append(_plain)

if GROQ_API_KEYS:
    print(f'[+] Loaded {len(GROQ_API_KEYS)} Groq API key(s) for rotation.')
else:
    print('[!] WARNING: No Groq API keys found — AI ranking will be skipped.')


class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Cloud-ready proxy handler — no local file serving."""

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.end_headers()

    def do_GET(self):
        # Health check
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'Limitless Proxy OK')
            return

        # Debug endpoint — shows key count without revealing key values
        if self.path == '/debug':
            import traceback
            debug_info = {
                "keys_loaded": len(GROQ_API_KEYS),
                "key_prefixes": [k[:8] + '...' for k in GROQ_API_KEYS],
                "status": "ok" if GROQ_API_KEYS else "no_keys"
            }
            body = json.dumps(debug_info).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path.startswith('/proxy?url='):
            target_url = urllib.parse.unquote(self.path.split('/proxy?url=')[1])
            print(f"Proxying request to: {target_url}")
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

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
                    for header, value in response.getheaders():
                        h_lower = header.lower()
                        if h_lower not in ['transfer-encoding', 'connection', 'x-frame-options', 'content-security-policy', 'content-encoding']:
                            if h_lower == 'content-disposition':
                                value = value.replace('attachment', 'inline')
                            self.send_header(header, value)
                    self.end_headers()
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
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == '/search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            year_str = data.get('year', '')
            kw_str = data.get('keywords', '')
            query_parts = [data.get('company'), data.get('docType')]
            if year_str: query_parts.append(str(year_str))
            if kw_str: query_parts.append(kw_str)
            query_parts.append("english document pdf")
            query = " ".join([p for p in query_parts if p]).strip()
            query = re.sub(r'\s+', ' ', query)

            # Server key pool only (no client key for security on cloud)
            key_pool = list(GROQ_API_KEYS)

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

                with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                    html = response.read().decode('utf-8')

                links_raw = re.findall(r'<a rel="nofollow" href="([^"]+)" class=[\'"]result-link[\'"][^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
                snippets_raw = re.findall(r"<td class='result-snippet'>(.*?)</td>", html, re.DOTALL | re.IGNORECASE)

                results = []
                seen_urls = set()
                for i in range(len(links_raw)):
                    if len(results) >= 15: break
                    url, title = links_raw[i]
                    snippet = snippets_raw[i] if i < len(snippets_raw) else ""
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                    if re.search(r'[äöüßÄÖÜ]', title + snippet):
                        continue
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    results.append({"title": title, "url": url, "snippet": snippet})

            except Exception as e:
                print(f"Scrape Error: {str(e)}")
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Search failed: {str(e)}"}).encode('utf-8'))
                return

            # Step 2: Groq API Evaluation with key rotation
            if not key_pool:
                response_bytes = json.dumps({"results": results[:5]}).encode('utf-8')
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)
                return

            final_results = None
            last_error = None
            import traceback as tb

            for key_index, api_key in enumerate(key_pool):
                api_key = api_key.strip()  # Remove any whitespace/newlines from Render env vars
                if not api_key:
                    print(f'[!] Key #{key_index + 1} is empty — skipping.')
                    last_error = f'Key #{key_index + 1} is empty'
                    continue

                try:
                    print(f'[*] Trying Groq key #{key_index + 1}: {api_key[:8]}...')
                    prompt_details = f"company '{data.get('company')}' and document type '{data.get('docType')}'"
                    if year_str: prompt_details += f" for the year '{year_str}'"
                    if kw_str: prompt_details += f" related to '{kw_str}'"
                    prompt = f"""Evaluate these search results for {prompt_details}. Return ONLY a JSON array of the 5 most relevant objects containing 'title', 'url', and 'snippet'.
CRITICAL RULE: You must EXCLUDE any documents that are not in English. Only return results where the title and snippet are in English.
Do not return markdown, just the raw JSON array.

Results: {json.dumps(results)}"""

                    groq_req = urllib.request.Request(
                        "https://api.groq.com/openai/v1/chat/completions",
                        data=json.dumps({
                            "model": "llama-3.1-8b-instant",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.1
                        }).encode('utf-8'),
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                            "User-Agent": "Mozilla/5.0"
                        }
                    )

                    # Use default SSL context — api.groq.com has a valid certificate
                    with urllib.request.urlopen(groq_req, timeout=30) as response:
                        raw = response.read().decode('utf-8')
                        print(f'[+] Groq raw response (first 200 chars): {raw[:200]}')
                        groq_res = json.loads(raw)
                        answer = groq_res['choices'][0]['message']['content'].strip()
                        # Strip markdown code fences if present
                        if answer.startswith('```json'): answer = answer[7:]
                        if answer.startswith('```'): answer = answer[3:]
                        if answer.endswith('```'): answer = answer[:-3]
                        answer = answer.strip()
                        print(f'[+] Groq answer (first 200 chars): {answer[:200]}')
                        final_results = json.loads(answer)
                        print(f'[+] Groq key #{key_index + 1} succeeded. Got {len(final_results)} results.')
                        break

                except urllib.error.HTTPError as e:
                    err_body = ''
                    try: err_body = e.read().decode('utf-8')[:200]
                    except: pass
                    if e.code == 429:
                        print(f'[!] Groq key #{key_index + 1} hit rate limit (429). Trying next key...')
                        last_error = f'Key #{key_index + 1} rate limited'
                        continue
                    else:
                        last_error = f'HTTP {e.code}: {e.reason} — {err_body}'
                        print(f'[!] Groq key #{key_index + 1} failed: {last_error}')
                        break
                except Exception as e:
                    last_error = f'{type(e).__name__}: {str(e)}'
                    print(f'[!] Groq key #{key_index + 1} exception: {last_error}')
                    print(tb.format_exc())
                    break

            if final_results is not None:
                response_bytes = json.dumps({"results": final_results}).encode('utf-8')
            else:
                warn_msg = f'All {len(key_pool)} Groq API key(s) failed. Showing raw results. Last error: {last_error}'
                print(f'[!] {warn_msg}')
                response_bytes = json.dumps({"results": results[:5], "warning": warn_msg}).encode('utf-8')

            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default request logs for cleaner cloud output
        print(f"[{self.address_string()}] {format % args}")


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    # Bind to 0.0.0.0 so Render can route traffic to us
    with socketserver.TCPServer(("0.0.0.0", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"=================================================")
        print(f"[*] Limitless Proxy running on port {PORT}")
        print(f"=================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down proxy...")
