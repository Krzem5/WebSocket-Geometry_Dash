from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, HTTPServer
import io
import os
import sys
import threading
import urllib



global WS_URL
WS_URL=""
global C_WS_URL
C_WS_URL=""



class Client(SimpleHTTPRequestHandler):
	server_version="HTTP/1.3"
	protocol_version="HTTP/1.0"
	def send_head(self):
		path=self.translate_path(self.path)
		f=None
		if (path==os.getcwd()+"\\WS_URL"):
			enc=WS_URL.encode(sys.getfilesystemencoding(),"surrogateescape")
			f=io.BytesIO()
			f.write(enc)
			f.seek(0)
			self.send_response(HTTPStatus.OK)
			self.send_header("Content-type","text/plain")
			self.send_header("Content-Length",str(len(enc)))
			self.send_header("Last-Modified",0)
			self.end_headers()
			self.copyfile(f,self.wfile)
			return
		path=os.getcwd()+"\\web"+path.replace(os.getcwd(),"")
		if (os.path.isdir(path)):
			parts=urllib.parse.urlsplit(self.path)
			if not parts.path.endswith("/"):
				self.send_response(HTTPStatus.MOVED_PERMANENTLY)
				new_parts=(parts[0],parts[1],parts[2]+"/",parts[3],parts[4])
				new_url=urllib.parse.urlunsplit(new_parts)
				self.send_header("Location",new_url)
				self.end_headers()
				return None
			for index in "index.html","index.htm":
				index=os.path.join(path,index)
				if (os.path.exists(index)):
					path=index
					break
			else:
				return self.list_directory(path)
		ctype=self.guess_type(path)
		try:
			f=open(path,"rb")
		except OSError:
			self.send_error(HTTPStatus.NOT_FOUND,"File not found")
			return None
		try:
			self.send_response(HTTPStatus.OK)
			self.send_header("Content-type",ctype)
			fs=os.fstat(f.fileno())
			self.send_header("Content-Length",str(fs[6]))
			self.send_header("Last-Modified",self.date_time_string(fs.st_mtime))
			self.end_headers()
			return f
		except:
			f.close()
			raise



class CClient(SimpleHTTPRequestHandler):
	server_version="HTTP/1.3"
	protocol_version="HTTP/1.0"
	def send_head(self):
		path=self.translate_path(self.path)
		f=None
		if (path==os.getcwd()+"\\C_WS_URL"):
			enc=C_WS_URL.encode(sys.getfilesystemencoding(),"surrogateescape")
			f=io.BytesIO()
			f.write(enc)
			f.seek(0)
			self.send_response(HTTPStatus.OK)
			self.send_header("Content-type","text/plain")
			self.send_header("Content-Length",str(len(enc)))
			self.send_header("Last-Modified",0)
			self.end_headers()
			self.copyfile(f,self.wfile)
			return
		with open("./console.html","rb") as f:
			self.send_response(HTTPStatus.OK)
			self.send_header("Content-type","text/html")
			fs=os.fstat(f.fileno())
			self.send_header("Content-Length",str(fs[6]))
			self.send_header("Last-Modified",0)
			self.end_headers()
			self.copyfile(f,self.wfile)



def start_c():
	with HTTPServer(("localhost",8002),CClient) as httpd:
		print("HTTP server started on port 8002!")
		httpd.serve_forever()




def start(url,wsurl,curl,cwsurl):
	global WS_URL
	WS_URL=wsurl
	global C_WS_URL
	C_WS_URL=cwsurl
	thr=threading.Thread(target=start_c,args=(),kwargs={})
	thr.deamon=True
	thr.start()
	with HTTPServer(("localhost",8000),Client) as httpd:
		print("HTTP server started on port 8000!")
		httpd.serve_forever()
