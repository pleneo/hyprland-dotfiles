#!/usr/bin/env python3
import os
import sys
import json
import time
import base64
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-library-read user-library-modify"
TOKEN_FILE = os.path.expanduser("~/.config/spotify_api_auth.json")

CREDENTIALS_PATHS = [
    os.path.expanduser("~/.config/spotify_app_credentials.json"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "spotify_credentials.json"),
    os.path.expanduser("~/.config/waybar/modules/spotify_credentials.json"),
]

def load_credentials():
    cid = os.environ.get("SPOTIFY_CLIENT_ID")
    csecret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if cid and csecret:
        return cid.strip(), csecret.strip()

    for path in CREDENTIALS_PATHS:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    creds = json.load(f)
                    c_id = creds.get("client_id", "").strip()
                    c_sec = creds.get("client_secret", "").strip()
                    if c_id and c_sec and not c_id.startswith("your_") and not c_sec.startswith("your_"):
                        return c_id, c_sec
            except Exception:
                pass
    return "", ""

CLIENT_ID, CLIENT_SECRET = load_credentials()

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_tokens(tokens):
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)

def refresh_access_token(refresh_token):
    global CLIENT_ID, CLIENT_SECRET
    if not CLIENT_ID or not CLIENT_SECRET:
        CLIENT_ID, CLIENT_SECRET = load_credentials()
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Erro: Credenciais do Spotify não configuradas.", file=sys.stderr)
        return None

    url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    })
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tokens = load_tokens() or {}
            tokens["access_token"] = data["access_token"]
            tokens["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
            if "refresh_token" in data:
                tokens["refresh_token"] = data["refresh_token"]
            save_tokens(tokens)
            return tokens["access_token"]
    except Exception as e:
        print(f"Erro ao atualizar token: {e}", file=sys.stderr)
        return None

def get_valid_token():
    tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        return None
    if time.time() < tokens.get("expires_at", 0):
        return tokens.get("access_token")
    return refresh_access_token(tokens["refresh_token"])

def is_authorized():
    tokens = load_tokens()
    return bool(tokens and "refresh_token" in tokens)

class OAuthHandler(BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            OAuthHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html>
            <body style="background:#12131b;color:#f5f5f7;font-family:sans-serif;text-align:center;padding:50px;">
                <h1 style="color:#1db954;">Conectado com sucesso!</h1>
                <p>O Spotify foi integrado ao seu Dynamic Island. Pode fechar esta aba.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def authorize():
    global CLIENT_ID, CLIENT_SECRET
    if not CLIENT_ID or not CLIENT_SECRET:
        CLIENT_ID, CLIENT_SECRET = load_credentials()
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Erro: Credenciais do Spotify não configuradas. Crie o arquivo spotify_credentials.json baseado no exemplo.", file=sys.stderr)
        return False

    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    })

    print(f"Abrindo navegador para autorização: {auth_url}")
    os.system(f"xdg-open '{auth_url}' &")

    server = HTTPServer(("127.0.0.1", 8888), OAuthHandler)
    server.timeout = 60
    while not OAuthHandler.auth_code:
        server.handle_request()

    code = OAuthHandler.auth_code
    if not code:
        print("Autorização falhou: código não recebido.")
        return False

    # Trocar código por token
    url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    })
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
            token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600) - 60
            save_tokens(token_data)
            print("Tokens salvos com sucesso!")
            return True
    except Exception as e:
        print(f"Erro ao trocar código por token: {e}", file=sys.stderr)
        return False

def is_track_liked(track_id):
    if not track_id:
        return False
    token = get_valid_token()
    if not token:
        return False
    # Limpar track_id caso venha com prefixos
    clean_id = track_id.split("/")[-1].split(":")[-1]
    url = f"https://api.spotify.com/v1/me/library/contains?uris=spotify:track:{clean_id}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 0:
                return bool(data[0])
    except Exception as e:
        print(f"Erro ao verificar like: {e}", file=sys.stderr)
    return False

def set_track_liked(track_id, liked=True):
    if not track_id:
        return False
    token = get_valid_token()
    if not token:
        return False
    clean_id = track_id.split("/")[-1].split(":")[-1]
    url = f"https://api.spotify.com/v1/me/library?uris=spotify:track:{clean_id}"
    method = "PUT" if liked else "DELETE"
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Content-Length": "0"
    })
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status in (200, 201, 204)
    except Exception as e:
        print(f"Erro ao alterar like: {e}", file=sys.stderr)
        return False

def toggle_like(track_id):
    current = is_track_liked(track_id)
    new_state = not current
    success = set_track_liked(track_id, new_state)
    return new_state if success else current

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        authorize()
    else:
        if not is_authorized():
            print("Não autorizado. Rodando fluxo de autorização...")
            authorize()
        else:
            print("Já autorizado! Token válido disponível.")
