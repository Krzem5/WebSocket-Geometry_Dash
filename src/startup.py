from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import ntpath
import os
import pickle
import requests
import subprocess
import threading
import time



SCOPES=["https://mail.google.com/"]



def setup():
	cdata=None
	if (ntpath.exists("token.tk")):
		with open("token.tk","rb") as t:
			cdata=pickle.load(t)
	if (not cdata or not cdata.valid):
		if (cdata and cdata.expired and cdata.refresh_token):
			cdata.refresh(Request())
		else:
			flw=InstalledAppFlow.from_client_secrets_file("creds.json",SCOPES)
			cdata=flw.run_local_server(port=0)
		with open("token.tk","wb") as t:
			pickle.dump(cdata,t)
	gmail=build("gmail","v1",credentials=cdata)
	return gmail



def start_http(url,wsurl,curl,cwsurl):
	import HTTPServer as s
	s.start(url,wsurl,curl,cwsurl)



def start_ws():
	import WSServer as s
	# s.start()



with open(r"C:\Users\MAKS\.ngrok2\ngrok.yml","w") as f:
	f.write("""authtoken: 1PHS4iuKaEWckPw4MiCJUS6sbq2_2EBTmdr7bjoURDTW1mE2X
web_addr: localhost:4444
tunnels:
  gd_c_http:
    inspect: false
    proto: http
    addr: 8002
  gd_c_ws:
    inspect: false
    proto: http
    addr: 8003
  gd_http:
    inspect: false
    proto: http
    addr: 8000
  gd_ws:
    inspect: false
    proto: http
    addr: 8001""")
NGROK_PID=subprocess.Popen(["ngrok.exe","start","gd_http","gd_ws"]).pid
time.sleep(2)
with open(r"C:\Users\MAKS\.ngrok2\ngrok.yml","w") as f:
	f.write("""authtoken: 1PKd8A3fV1Iv1fTbrxLaaXDLkuy_5Da7AR37CANasVNsd9Yvk
web_addr: localhost:4445
tunnels:
  gd_c_http:
    inspect: false
    proto: http
    addr: 8002
  gd_c_ws:
    inspect: false
    proto: http
    addr: 8003
  gd_http:
    inspect: false
    proto: http
    addr: 8000
  gd_ws:
    inspect: false
    proto: http
    addr: 8001""")
NGROK_PID2=subprocess.Popen(["ngrok.exe","start","gd_c_http","gd_c_ws"]).pid
time.sleep(2)
_dt=None
while (True):
	_dt=requests.get("http://localhost:4444/api/tunnels").json()
	if (len(_dt["tunnels"])>=4):
		break
_dt2=None
while (True):
	_dt2=requests.get("http://localhost:4445/api/tunnels").json()
	if (len(_dt2["tunnels"])>=4):
		break
HTTP_URL=""
WS_URL=""
C_HTTP_URL=""
C_WS_URL=""
for t in _dt["tunnels"]:
	if (t["name"]=="gd_http"):
		HTTP_URL=t["public_url"].replace("https","http")+"/"
	elif (t["name"]=="gd_ws"):
		WS_URL=t["public_url"].replace("https","ws")+"/"
for t in _dt2["tunnels"]:
	if (t["name"]=="gd_c_http"):
		C_HTTP_URL=t["public_url"].replace("https","http")+"/"
	elif (t["name"]=="gd_c_ws"):
		C_WS_URL=t["public_url"].replace("https","ws")+"/"
msg=MIMEText(f"Game:\n{HTTP_URL}\n\n\nConsole:\n{C_HTTP_URL}")
msg["to"]="aleks.black42@gmail.com"
msg["from"]=""
msg["subject"]="App Creds"
setup().users().messages().send(userId="me",body={"raw":base64.urlsafe_b64encode(msg.as_bytes()).decode()}).execute()
os.system(f"start chrome \"{HTTP_URL}\"")
os.system(f"start chrome \"{C_HTTP_URL}\"")
thr=threading.Thread(target=start_http,args=(HTTP_URL,WS_URL,C_HTTP_URL,C_WS_URL),kwargs={})
thr.deamon=True
thr.start()
thr=threading.Thread(target=start_ws,args=(),kwargs={})
thr.deamon=True
thr.start()



# os.system(f"C:\\Windows\\System32\\taskkill.exe /PID {os.getpid()} /F&&C:\\Windows\\System32\\taskkill.exe /PID {NGROK_PID} /F")