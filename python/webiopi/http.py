from .utils import *

import os
import threading
import re
import codecs
import mimetypes as mime

if PYTHON_MAJOR >= 3:
    import http.server as BaseHTTPServer
else:
    import BaseHTTPServer

try :
    import _webiopi.GPIO as GPIO
except:
    pass

class HTTPServer(BaseHTTPServer.HTTPServer, threading.Thread):
    def __init__(self, host, port, context, index, handler, auth=None):
        BaseHTTPServer.HTTPServer.__init__(self, ("", port), HTTPHandler)
        threading.Thread.__init__(self)

        self.docroot = "/usr/share/webiopi/htdocs"
        self.log_enabled = False
        self.host = host
        self.port = port
        self.context = context
        self.index = index
        self.handler = handler
        self.auth = auth

        self.start()
            
    def run(self):
        log("HTTP Server binded on http://%s:%s%s" % (self.host, self.port, self.context))
        self.running = True
        try:
            self.serve_forever()
        except Exception as e:
            if self.running:
                error("%s" % e)
        log("HTTP Server stopped")

    def stop(self):
        self.running = False
        self.server_close()

class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if self.server.log_enabled:
            log(format % args)

    def version_string(self):
        return SERVER_VERSION + ' ' + self.sys_version
    
    def checkAuthentication(self):
        if self.server.auth == None or len(self.server.auth) == 0:
            return True
        
        authHeader = self.headers.get('Authorization')
        if authHeader == None:
            return False
        
        if not authHeader.startswith("Basic "):
            return False
        
        auth = authHeader.replace("Basic ", "")
        if PYTHON_MAJOR >= 3:
            hash = hashlib.sha256(auth.encode()).hexdigest()
        else:
            hash = hashlib.sha256(auth).hexdigest()
            
        if hash == self.server.auth:
            return True
        return False

    def requestAuthentication(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="webiopi"')
        self.end_headers();
    
    def sendResponse(self, code, body=None, type="text/plain"):
        if code >= 400:
            if body != None:
                self.send_error(code, body)
            else:
                self.send_error(code)
        else:
            self.send_response(code)
            self.send_header("Content-type", type);
            self.end_headers();
            self.wfile.write(body.encode())
            
    def serveFile(self, relativePath):
        if relativePath == "":
            relativePath = self.server.index
                        
        realPath = relativePath;
        
        if not os.path.exists(realPath):
            realPath = self.server.docroot + os.sep + relativePath
            
        if not os.path.exists(realPath):
            return self.sendResponse(404, "Not Found")

        realPath = os.path.realpath(realPath)
        
        if realPath.endswith(".py"):
            return self.sendResponse(403, "Not Authorized")
        
        if not (realPath.startswith(self.server.docroot) or realPath.startswith(os.getcwd())):
            return self.sendResponse(403, "Not Authorized")
            
        if os.path.isdir(realPath):
            realPath += os.sep + self.server.index;
            if not os.path.exists(realPath):
                return self.sendResponse(403, "Not Authorized")
            
        (type, encoding) = mime.guess_type(realPath)
        f = codecs.open(realPath, encoding=encoding)
        data = f.read()
        f.close()
        self.send_response(200)
        self.send_header("Content-type", type);
#            self.send_header("Content-length", os.path.getsize(realPath))
        self.end_headers()
        self.wfile.write(data)
        
    def processRequest(self):
        if not self.checkAuthentication():
            return self.requestAuthentication()
        
        relativePath = self.path.replace(self.server.context, "/")
        if relativePath.startswith("/"):
            relativePath = relativePath[1:];

        try:
            result = (None, None, None)
            if self.command == "GET":
                result = self.server.handler.do_GET(relativePath)
            elif self.command == "POST":
                result = self.server.handler.do_POST(relativePath)
            else:
                result = (405, None, None)
                
            (code, body, type) = result
            
            if code > 0:
                self.sendResponse(code, body, type)
            else:
                if self.command == "GET":
                    self.serveFile(relativePath)
                else:
                    self.sendResponse(404)

        except (GPIO.InvalidDirectionException, GPIO.InvalidChannelException, GPIO.SetupException) as e:
            self.sendResponse(403, "%s" % e)
        except Exception as e:
            self.sendResponse(500)
            raise e
            
    def do_GET(self):
        self.processRequest()

    def do_POST(self):
        self.processRequest()
