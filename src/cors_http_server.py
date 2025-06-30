import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Change the current working directory to 'knowledgebase' folder
# This ensures the server serves files relative to this folder
os.chdir("knowledgebase")


# Custom request handler class that adds CORS headers
class CORSRequestHandler(SimpleHTTPRequestHandler):
    # Override method to add CORS headers after sending HTTP headers
    def end_headers(self):
        # Allow any origin to access resources (wide-open CORS)
        self.send_header("Access-Control-Allow-Origin", "*")
        # Allow GET, POST and OPTIONS methods from clients
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        # Allow the Content-Type header in requests (needed for some POST requests)
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        # Call parent method to complete sending headers
        super().end_headers()

    # Handle HTTP OPTIONS method (preflight request for CORS)
    def do_OPTIONS(self):
        # Send 200 OK response for OPTIONS requests
        self.send_response(200, "ok")
        # Send the same CORS headers as in end_headers()
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        # End the headers
        self.end_headers()


# Main block to start the HTTP server
if __name__ == "__main__":
    # Server address: '' means listen on all interfaces, port 8000
    server_address = ("", 8000)
    # Create the HTTP server with our custom handler
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print("Serving HTTP with CORS enabled on port 8000 from 'knowledgebase' folder")
    # Start the server loop (blocking call)
    httpd.serve_forever()
