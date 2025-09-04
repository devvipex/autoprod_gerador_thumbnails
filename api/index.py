from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Resposta básica para verificar se a API está funcionando
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "Thumbnail Generator API v1.0.3",
            "status": "active",
            "endpoints": {
                "/": "API status",
                "/health": "Health check",
                "/app": "Redirect to Streamlit app"
            },
            "note": "This is a Streamlit application. For full functionality, please run locally with 'streamlit run streamlit_app.py'"
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_POST(self):
        # Placeholder para futuras funcionalidades de API
        self.send_response(501)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "error": "Not implemented",
            "message": "POST endpoints not yet implemented"
        }
        
        self.wfile.write(json.dumps(response).encode())