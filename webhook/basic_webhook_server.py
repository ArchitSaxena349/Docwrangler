#!/usr/bin/env python3
"""
Basic webhook server that definitely works
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
from datetime import datetime
from typing import Dict, Any
import urllib.parse

class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for webhook endpoints"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/webhook/health':
            self.send_json_response({
                "status": "healthy",
                "service": "Basic LLM Document Processing Webhook",
                "timestamp": datetime.utcnow().isoformat(),
                "endpoints": [
                    "/webhook/health",
                    "/webhook/query", 
                    "/webhook/insurance-claim",
                    "/webhook/document-upload"
                ]
            })
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def do_POST(self):
        """Handle POST requests"""
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON")
            return
        
        # Route to appropriate handler
        if self.path == '/webhook/query':
            response = self.handle_query(payload)
        elif self.path == '/webhook/insurance-claim':
            response = self.handle_insurance_claim(payload)
        elif self.path == '/webhook/document-upload':
            response = self.handle_document_upload(payload)
        else:
            self.send_error_response(404, "Endpoint not found")
            return
        
        self.send_json_response(response)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response"""
        error_data = {
            "error": message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.send_json_response(error_data, status_code)
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def handle_query(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query webhook"""
        query = payload.get('query', '')
        context = payload.get('context', {})
        
        print(f"📝 Processing query: {query}")
        
        # Simple mock analysis
        query_lower = query.lower()
        
        # Determine decision based on keywords
        if any(word in query_lower for word in ['surgery', 'operation', 'procedure']):
            decision = "approved"
            confidence = 0.85
            amount = 50000
            justification = f"Medical procedure '{query}' is typically covered under standard health insurance policies."
        elif any(word in query_lower for word in ['dental', 'teeth']):
            decision = "pending"
            confidence = 0.60
            amount = 15000
            justification = f"Dental procedures may require waiting period verification. Query: {query}"
        elif any(word in query_lower for word in ['maternity', 'pregnancy']):
            decision = "approved"
            confidence = 0.75
            amount = 75000
            justification = f"Maternity benefits are covered after waiting period. Query: {query}"
        else:
            decision = "pending"
            confidence = 0.50
            amount = None
            justification = f"Query requires manual review for proper assessment: {query}"
        
        response = {
            "status": "success",
            "query": query,
            "decision": decision,
            "justification": justification,
            "confidence": confidence,
            "amount": amount,
            "source_clauses": ["mock_section_1", "mock_section_2"],
            "processing_time": round(time.time() % 10, 2),  # Mock processing time
            "timestamp": datetime.utcnow().isoformat(),
            "context": context
        }
        
        return response
    
    def handle_insurance_claim(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle insurance claim webhook"""
        claim_id = payload.get('claim_id', f"CLM-{int(time.time())}")
        age = payload.get('age', 0)
        gender = payload.get('gender', '')
        procedure = payload.get('procedure', '')
        location = payload.get('location', '')
        policy_duration = payload.get('policy_duration', '')
        claim_amount = payload.get('claim_amount', 0)
        
        print(f"🏥 Processing insurance claim: {claim_id}")
        print(f"   Details: {age}y {gender}, {procedure}, {location}")
        
        # Mock decision logic
        procedure_lower = procedure.lower()
        
        if 'surgery' in procedure_lower:
            approved = True
            coverage_amount = min(claim_amount, 100000)  # Cap at 1 lakh
            confidence = 0.90
            justification = f"Surgery procedures are covered. {procedure} approved for {age}-year-old {gender} in {location}."
        elif 'dental' in procedure_lower:
            approved = False
            coverage_amount = 0
            confidence = 0.70
            justification = f"Dental procedures require 6-month waiting period verification."
        elif 'maternity' in procedure_lower:
            approved = True if age >= 18 and age <= 45 else False
            coverage_amount = min(claim_amount, 75000) if approved else 0
            confidence = 0.85
            justification = f"Maternity benefits {'approved' if approved else 'not approved'} for {age}-year-old."
        else:
            approved = True
            coverage_amount = min(claim_amount, 50000)
            confidence = 0.60
            justification = f"General medical claim approved with standard coverage limits."
        
        response = {
            "claim_id": claim_id,
            "status": "processed",
            "decision": "approved" if approved else "rejected",
            "approved": approved,
            "coverage_amount": coverage_amount,
            "justification": justification,
            "confidence_score": confidence,
            "source_documents": ["policy_doc_1", "coverage_terms"],
            "processing_time_seconds": round(time.time() % 5, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "claim_details": {
                "age": age,
                "gender": gender,
                "procedure": procedure,
                "location": location,
                "policy_duration": policy_duration,
                "requested_amount": claim_amount
            }
        }
        
        return response
    
    def handle_document_upload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document upload webhook"""
        file_path = payload.get('file_path', '')
        callback_url = payload.get('callback_url', '')
        metadata = payload.get('metadata', {})
        
        print(f"📄 Processing document upload: {file_path}")
        
        response = {
            "status": "received",
            "message": "Document upload webhook processed successfully",
            "document_id": f"doc_{int(time.time())}",
            "file_path": file_path,
            "callback_url": callback_url,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Document processing started in background"
        }
        
        return response
    
    def log_message(self, format, *args):
        """Custom log message format"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def start_webhook_server(port=8001):
    """Start the webhook server"""
    print(f"🚀 Starting Basic Webhook Server")
    print(f"="*40)
    print(f"📍 Server: http://localhost:{port}")
    print(f"📋 Endpoints:")
    print(f"   GET  /webhook/health")
    print(f"   POST /webhook/query")
    print(f"   POST /webhook/insurance-claim")
    print(f"   POST /webhook/document-upload")
    print(f"="*40)
    
    try:
        server = HTTPServer(('localhost', port), WebhookHandler)
        print(f"✅ Server running on http://localhost:{port}")
        print(f"💡 Press Ctrl+C to stop the server")
        print(f"🧪 Test with: python test_simple_webhooks.py")
        print()
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
        server.shutdown()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use")
            print(f"💡 Try a different port or stop the existing server")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    start_webhook_server()