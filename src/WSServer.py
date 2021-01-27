from PIL import Image
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import os
import random
import threading
import time



SOCKETS=[]
C_SOCKETS=[]
GAMES=[]
MIN_GAME_PLAYERS=2
MAX_GAME_PLAYERS=6
GAME_START_TIMEOUT=5# 20
SCREEN_BLOCKS=20
SCREEN_COLOR_SIZE=20
PLAYER_SIZE_RATIO=1
PLAYER_INNER_SIZE_RATIO=0.2
ALL_PLAYER_KICK_TIMEOUT=30
GAME_SPEED=0.008
GAME_GRAVITY=0.015
ICON_SIZE=30
ICON_SEP_DIST=10
COLORS=["cc3333","33cc33","3333cc","dddd11","33dddd","dd33dd"]
COLOR_NAMES={"cc3333":"Red","33cc33":"Green","3333cc":"Blue","dddd11":"Yellow","33dddd":"Aqua","dd33dd":"Magenta"}
PACKETS={
	"game_setup":"gs%s:%i",
	"game_board":"gb%i:%i:%s",
	"client_player_data":"pd%s:%i:%f:%f:%i:%i",
	"game_countdown":"gc%i",
	"start":"gc0",
	"game_update":"gu%f:%s",
	"statistics":"st%s.%s:%s",
	"disconnect":"dc",
	"c_data":"dt%s"
}



class World:
	def __init__(self,GAME,fn):
		self.GAME=GAME
		self.BOARD,self.SPAWNS,self.BOXES=self._gen(fn)



	def _gen(self,fn):
		img=Image.open(fn)
		dt=img.load()
		w=img.width
		h=img.height
		img.close()
		b=""
		sp=[]
		bl=[]
		for x in range(0,w):
			for y in range(0,h):
				if (dt[(x,y)][0]==1):
					sp+=[[x+0.5,y+0.5]]
					b+="0."
				else:
					if (max(dt[(x,y)][0]-1,0)>0):
						bl+=[[x,y,1,1,None]]
					b+=f"{max(dt[(x,y)][0]-1,0)}."
			b=b[:-1]+","
		return b[:-1],sp,bl



class Game:
	def __init__(self):
		a=False
		for i in range(0,len(GAMES)-1):
			if (GAMES[i]==None):
				GAMES[i]=self
				a=True
				break
		if (a==False):
			GAMES.append(self)
		self.ID=GAMES.index(self)
		self.STATE=0
		self.PLAYERS=[]
		self.TOTAL_PLAYERS=0
		self.WORLD=World(self,self._rand_f())
		self.SOCKETS=[]
		self.COLORS=COLORS[:]
		self.PL_L=""
		self.SPAWNS=self.WORLD.SPAWNS[:]
		self.X=0
		self.WC=""
		self.done=True
		random.shuffle(self.COLORS)
		random.shuffle(self.SPAWNS)



	def add_player(self,p):
		while (not hasattr(self,"done") or self.done!=True):
			pass
		self.PLAYERS.append(p)
		self.SOCKETS.append(p)
		self.TOTAL_PLAYERS+=1
		p.sendMessage(PACKETS["game_board"]%(self.ID,SCREEN_BLOCKS,self.WORLD.BOARD))
		p.sendMessage(PACKETS["client_player_data"]%(p.color,SCREEN_COLOR_SIZE,PLAYER_SIZE_RATIO,PLAYER_INNER_SIZE_RATIO,ICON_SIZE,ICON_SEP_DIST))
		self.sendall(PACKETS["game_setup"]%(self.player_string(),MAX_GAME_PLAYERS))
		if (self.STATE==0 and self.TOTAL_PLAYERS>=MIN_GAME_PLAYERS):
			self.STATE=1
			self.delay_start()
		if (self.TOTAL_PLAYERS==MAX_GAME_PLAYERS):
			self.STATE=2
			self.start()



	def next_color(self):
		while (not hasattr(self,"done") or self.done!=True):
			pass
		c=self.COLORS[0]
		self.COLORS.remove(c)
		return c



	def next_spawn(self):
		while (not hasattr(self,"done") or self.done!=True):
			pass
		s=self.SPAWNS[0]
		self.SPAWNS.remove(s)
		return s[0],s[1]



	def delay_start(self):
		def _dl(gm):
			time.sleep(GAME_START_TIMEOUT)
			gm.start()
		thr=threading.Thread(target=_dl,args=(self,),kwargs={})
		thr.deamon=True
		thr.start()



	def start(self):
		if (self.STATE>=3 or self.TOTAL_PLAYERS<MIN_GAME_PLAYERS):
			return
		self.STATE=3
		self.sendall(PACKETS["game_countdown"]%(3))
		time.sleep(1)
		self.sendall(PACKETS["game_countdown"]%(2))
		time.sleep(1)
		self.sendall(PACKETS["game_countdown"]%(1))
		time.sleep(1)
		self.STATE=4
		self.sendall(PACKETS["start"])
		while (len(self.PLAYERS)>1):
			self.update()
			time.sleep(0.001)
		self.STATE=5
		if (len(self.SOCKETS)==0):
			GAMES[self.ID]=None
		if (self.WC==""):
			self.WC=self.PLAYERS[0].color+""
		self.sendall(PACKETS["statistics"]%(self.WC,COLOR_NAMES[self.WC],self.PL_L[1:]))
		time.sleep(ALL_PLAYER_KICK_TIMEOUT)
		self.STATE=6
		if (self in GAMES):
			GAMES[self.ID]=None
		if (len(self.SOCKETS)>0):
			for s in self.SOCKETS:
				s.sendMessage(PACKETS["disconnect"])



	def update(self):
		bl=self.WORLD.BOXES[:]
		self.X+=GAME_SPEED
		for k in self.PLAYERS:
			bl+=[[k.x-PLAYER_SIZE_RATIO/2,k.y-PLAYER_SIZE_RATIO/2,PLAYER_SIZE_RATIO,PLAYER_SIZE_RATIO,k.color]]
		for k in self.PLAYERS:
			k.update(bl)
		self.sendall(PACKETS["game_update"]%(self.X,self.player_string()))



	def remove_player(self,p):
		while (not hasattr(self,"done") or self.done!=True):
			pass
		if (self.STATE==4 and len(self.PLAYERS)>1):
			self.PL_L=f",{p.color}.{COLOR_NAMES[p.color]}"+self.PL_L
		elif (self.STATE==4):
			self.WC=self.PLAYERS[0].color+""
		if (self.STATE==1 and self.TOTAL_PLAYERS-1<MIN_GAME_PLAYERS):
			self.STATE=0
			self.delay_start()
		self.TOTAL_PLAYERS-=1
		if (self.TOTAL_PLAYERS==0):
			GAMES[self.ID]=None
		self.PLAYERS.remove(p)
		self.sendall(PACKETS["game_update"]%(self.X,self.player_string()))



	def player_string(self):
		s=""
		for k in self.PLAYERS:
			s+=f"{k.color},{k.x},{k.y},{k.flip};"
		return s[:-1]



	def _rand_f(self):
		l=[]
		for f in os.listdir("./boards/"):
			if (f.endswith(".png")):
				l+=[f]
		random.shuffle(l)
		return "./boards/"+l[0]



	def sendall(self,msg):
		for k in self.SOCKETS:
			k.sendMessage(msg);



class Client(WebSocket):
	def handleMessage(self):
		self.sendMessage("null")
		thr=threading.Thread(target=self.process_message,args=(),kwargs={})
		thr.deamon=True
		thr.start()



	def handleConnected(self):
		self.sendMessage("null")
		thr=threading.Thread(target=self.setup,args=(),kwargs={})
		thr.deamon=True
		thr.start()



	def handleClose(self):
		global SOCKETS
		if (hasattr(self,"game")):
			self.game.SOCKETS.remove(self)
			self.game.remove_player(self)
		SOCKETS.remove(self)



	def setup(self):
		global SOCKETS
		SOCKETS+=[self]
		for g in GAMES:
			if (g==None):
				continue
			if (g.STATE==0 or g.STATE==1):
				self.game=g
		if (not hasattr(self,"game")):
			self.game=Game()
		self.x,self.y=self.game.next_spawn()
		self.flip=0
		self.color=self.game.next_color()
		self.game.add_player(self)



	def update(self,bl):
		self.x+=GAME_SPEED
		self.y+=(GAME_GRAVITY if self.flip==0 else -GAME_GRAVITY)
		for b in bl:
			if (b[4]==self.color):
				continue
			self._collide(b)
		if (self.x+PLAYER_SIZE_RATIO/2<self.game.X or self.y+PLAYER_SIZE_RATIO/2<0 or self.y-PLAYER_SIZE_RATIO/2>SCREEN_BLOCKS-1):
			self.game.remove_player(self)



	def process_message(self):
		msg=self.data
		if (self.game.STATE!=4):
			return
		if (msg=="jp"):
			self.flip=1-self.flip



	def _collide(self,box):
		ny=self.y+0
		if (box[1]<self.y+PLAYER_SIZE_RATIO/2 and self.y-PLAYER_SIZE_RATIO/2<box[1]+box[3]):
			if (self.x<box[0] and self.x+PLAYER_SIZE_RATIO/2>box[0]):
				self.x=box[0]-PLAYER_SIZE_RATIO/2
		if (box[0]<self.x+PLAYER_SIZE_RATIO/2 and self.x-PLAYER_SIZE_RATIO/2<box[0]+box[2]):
			if (self.y>box[1]+box[3] and self.y-PLAYER_SIZE_RATIO/2<box[1]+box[3]):
				ny=box[1]+box[3]+PLAYER_SIZE_RATIO/2
			if (self.y<box[1] and self.y+PLAYER_SIZE_RATIO/2>box[1]):
				ny=box[1]-PLAYER_SIZE_RATIO/2
		self.y=ny



class CClient(WebSocket):
	def handleMessage(self):
		self.sendMessage("null")
		thr=threading.Thread(target=self.process_message,args=(),kwargs={})
		thr.deamon=True
		thr.start()



	def handleConnected(self):
		self.sendMessage("null")
		global C_SOCKETS
		C_SOCKETS.append(self)



	def handleClose(self):
		global C_SOCKETS
		C_SOCKETS.remove(self)



	def send(self):
		gs=""
		for g in GAMES:
			if (not hasattr(g,"done") or g.done!=True):
				continue
			ps=""
			if (len(g.PLAYERS)==1 and g.STATE>=4):
				ps="."
			else:
				for p in g.PLAYERS:
					ps+=f"{p.color}-{COLOR_NAMES[p.color]}."
			ss=""
			for s in g.SOCKETS:
				ss+=f"{s.color}-{COLOR_NAMES[s.color]}."
			wc=(g.WC if g.WC!="" else (g.PLAYERS[0].color if len(g.PLAYERS)>0 else None))
			pls=("null."*(len(g.PLAYERS)) if len(g.PLAYERS)>1 or g.STATE<4 or wc==None else f"{wc}-{COLOR_NAMES[wc]}.")
			for s in g.PL_L[1:].split(","):
				if (s==""):
					continue
				pls+=s.replace(".","-")+"."
			gs+=f"{g.ID},{g.STATE},{ps[:-1]},{ss[:-1]},{pls[:-1]};"
		self.sendMessage(PACKETS["c_data"]%(gs[:-1]))



	def process_message(self):
		msg=self.data
		print("Message: "+msg)




#============================
#         TO SERVER
#============================
# jp -> Player jump packet



#============================
#        FROM SERVER
#============================
# gs[PLAYERS]:[MAX_PLAYERS] -> Game setup packet
# gb[GAME_BOARD_DATA] -> Game board packet
# pd[COLOR]:[BORDER_SIZE]:[PLAYER_SIZE]:[PLAYER_INNER_SIZE] -> Player init data packet
# gc[TIMESTAMP] -> Game countdown packet
# st -> Start packet
# gu[GAME_X_POS]:[PLAYER_DATA] -> Game update packet
# pr[PLAYER_COLOR] -> Player death packet



def start_c():
	server=SimpleWebSocketServer("localhost",8003,CClient)
	print("WebSocket has started on port 8003!")
	server.serveforever()



def start_c_loop():
	while (True):
		for c in C_SOCKETS:
			c.send()
		time.sleep(1/15)



def start():
	thr=threading.Thread(target=start_c,args=(),kwargs={})
	thr.deamon=True
	thr.start()
	thr=threading.Thread(target=start_c_loop,args=(),kwargs={})
	thr.deamon=True
	thr.start()
	server=SimpleWebSocketServer("localhost",8001,Client)
	print("WebSocket has started on port 8001!")
	server.serveforever()



if (__name__=="__main__"):
	start()
