var wr,cnv,ctx,ic=0;
var PLAYERS={},BOARD=null,WS_URL="",MOUSEPOS={x:0,y:0},MOUSEDOWN=false,STATUS=[0],LERP_COUNTER=-1,GAME_ID="";



function init(){
	wr=document.getElementsByClassName("wr")[0];
	cnv=document.getElementsByClassName("cnv")[0];
	cnv.width=window.innerWidth;
	cnv.height=window.innerHeight;
	ctx=cnv.getContext("2d");
	_load_font("./font/sniglet.ttf");
	_load_font("./font/snigletB.ttf");
	fetch("WS_URL").then((r)=>r.text()).then(function(url){
		WS_URL=url;
		ic++;
		if (ic==3){
			_socket_init();
			draw();
		}
	});
}



function _socket_init(){
	window.SOCKET=null;
	function join(){
		var old_r;
		SOCKET=new WebSocket(WS_URL);
		SOCKET.onopen=function(){
			STATUS=[1,0]
			cnv.classList.add("h");
		}
		SOCKET.onclose=function(){
			STATUS=[0];
			BOARD=null;
			PLAYERS={};
			LERP_COUNTER=-1;
			cnv.classList.remove("h");
			join();
		}
		SOCKET.onmessage=function(e){
			try{
				if (e.data=="null"){
					return;
				}
				e={type:e.data.substring(0,2),data:e.data.substring(2)};
				_={
					gs:function(dt){
						PLAYERS.l=[];
						dt=dt.split(":");
						STATUS[1]=parseInt(dt[1]);
						for (var pdt of dt[0].split(";")){
							pdt=pdt.split(",");
							PLAYERS.l.push({cl:pdt[0],x:parseFloat(pdt[1]),y:parseFloat(pdt[2]),fp:parseInt(pdt[3])});
						}
					},
					gb:function(dt){
						dt=dt.split(":");
						GAME_ID=dt[0];
						BOARD={b:[],ts:0,bc:parseInt(dt[1]),ox:0,oxr:0,oy:0};
						for (var cl of dt[2].split(",")){
							var c=[];
							for (var k of cl.split(".")){
								c.push(parseInt(k));
							}
							BOARD.b.push(c);
						}
					},
					pd:function(dt){
						dt=dt.split(":");
						PLAYERS.dt={cl:dt[0],sz:parseInt(dt[1]),pszr:parseFloat(dt[2]),piszr:parseFloat(dt[3]),isz:parseInt(dt[4]),idsz:parseInt(dt[5])};
					},
					gc:function(dt){
						STATUS=[2,parseInt(dt)];
						if (parseInt(dt)==0){
							STATUS=[3];
						}
					},
					gu:function(dt){
						PLAYERS.l=[];
						dt=dt.split(":");
						BOARD.oxr=parseFloat(dt[0]);
						for (var pdt of dt[1].split(";")){
							pdt=pdt.split(",");
							PLAYERS.l.push({cl:pdt[0],x:parseFloat(pdt[1]),y:parseFloat(pdt[2]),fp:parseInt(pdt[3])});
						}
					},
					st:function(dt){
						dt=dt.split(":");
						setTimeout(function(){
							LERP_COUNTER=0;
						},500);
						STATUS=[6,{w:dt[0].split("."),l:dt[1].split(",")}];
						STATUS[1].l.forEach((a,b,c)=>c[b]=a.split("."));
					},
					dc:function(dt){
						SOCKET.close();
					}
				}[e.type](e.data);
			}
			catch (e){
				console.warn(e);
			}
		}
		SOCKET.onerror=function(e){
			e.stopImmediatePropagation();
			e.stopPropagation();
			e.preventDefault();
			console.clear();
		}
	}
	join();
}



function _load_font(fn){
	fetch(fn).then((r)=>r.arrayBuffer()).then(function(f){
		var nm=fn.substring(fn.lastIndexOf("/")+1).split("\.")[0]
		document.fonts.add(new window.FontFace(nm.split(".")[0][0].toUpperCase()+nm.split(".")[0].substring(1).toLowerCase(),f));
		ic++;
		if (ic==3){
			_socket_init();
			draw();
		}
	});
}



window.onkeydown=function(e){
	if (STATUS[0]==3&&e.keyCode==32){
		SOCKET.send("jp");
	}
}



window.ontouchstart=function(e){
	if (STATUS[0]==3){
		SOCKET.send("jp");
	}
}



window.oncontextmenu=function(e){
	return false;
}



window.onresize=function(){
	cnv.width=window.innerWidth;
	cnv.height=window.innerHeight;
}



window.requestAnimationFrame=window.requestAnimationFrame||window.mozRequestAnimationFrame||window.webkitRequestAnimationFrame||window.msRequestAnimationFrame;
window.AudioContext=window.AudioContext||window.webkitAudioContext;



document.addEventListener("DOMContentLoaded",init,false);