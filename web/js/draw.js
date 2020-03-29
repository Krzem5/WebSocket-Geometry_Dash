function draw(){
	requestAnimationFrame(draw)
	ctx.fillStyle="#ffffff";
	ctx.fillRect(0,0,cnv.width,cnv.height);
	if (STATUS[0]==0){
		ctx.fillStyle="#0a0a0a";
		ctx.textAlign="center";
		ctx.textBaseline="middle";
		ctx.font="55px SnigletB";
		ctx.fillText("Connecting...",cnv.width/2,cnv.height/2-40);
		ctx.fillStyle="#696969";
		ctx.font="25px SnigletB";
		ctx.fillText("Please Wait",cnv.width/2,cnv.height/2+10);
		return;
	}
	if (BOARD==null||PLAYERS.dt==null||PLAYERS.l==null){
		return;
	}
	BOARD.ts=parseInt(cnv.height/BOARD.bc);
	BOARD.ox=BOARD.oxr*BOARD.ts;
	BOARD.oy=parseInt((cnv.height-BOARD.ts*BOARD.bc)/2);
	PLAYERS.dt.psz=BOARD.ts*PLAYERS.dt.pszr;
	PLAYERS.dt.pisz=PLAYERS.dt.psz*PLAYERS.dt.piszr;
	var x=0;
	var y=0;
	for (var c of BOARD.b){
		for (var k of c){
			switch (k){
				case 0: default:
					break;
				case 1:
					ctx.fillStyle="#555555";
					ctx.fillRect(parseInt(BOARD.ts*x-BOARD.ox),parseInt(BOARD.ts*y+BOARD.oy),BOARD.ts,BOARD.ts);
			}
			y++;
		}
		x++;
		y=0;
	}
	for (var p of PLAYERS.l){
		var x=p.x*BOARD.ts;
		var y=p.y*BOARD.ts;
		ctx.fillStyle=`#${p.cl}`;
		ctx.fillRect(x-PLAYERS.dt.psz/2-BOARD.ox,y-PLAYERS.dt.psz/2+BOARD.oy,PLAYERS.dt.pisz,PLAYERS.dt.psz);
		ctx.fillRect(x+PLAYERS.dt.psz/2-PLAYERS.dt.pisz-BOARD.ox,y-PLAYERS.dt.psz/2+BOARD.oy,PLAYERS.dt.pisz,PLAYERS.dt.psz);
		if (p.fp==0){
			ctx.fillRect(x-PLAYERS.dt.psz/2-BOARD.ox,y-PLAYERS.dt.psz/2+BOARD.oy,PLAYERS.dt.psz,PLAYERS.dt.pisz);
		}
		else{
			ctx.fillRect(x-PLAYERS.dt.psz/2-BOARD.ox,y+PLAYERS.dt.psz/2-PLAYERS.dt.pisz+BOARD.oy,PLAYERS.dt.psz,PLAYERS.dt.pisz);
		}
	}
	ctx.fillStyle=`#${PLAYERS.dt.cl}${LERP_COUNTER==-1?"":hex(parseInt(255-LERP_COUNTER*255))}`;
	ctx.fillRect(0,PLAYERS.dt.sz,PLAYERS.dt.sz,cnv.height-PLAYERS.dt.sz);
	ctx.fillRect(cnv.width-PLAYERS.dt.sz,PLAYERS.dt.sz,cnv.width,cnv.height-PLAYERS.dt.sz);
	ctx.fillRect(0,0,cnv.width,PLAYERS.dt.sz);
	ctx.fillRect(0,cnv.height-PLAYERS.dt.sz,cnv.width,cnv.height);
	if (LERP_COUNTER==-1){
		var x=cnv.width-PLAYERS.dt.sz-PLAYERS.dt.isz-PLAYERS.dt.idsz;
		for (var p of PLAYERS.l){
			ctx.fillStyle=`#${p.cl}`;
			ctx.fillRect(x,PLAYERS.dt.sz+PLAYERS.dt.idsz,PLAYERS.dt.isz,PLAYERS.dt.isz);
			x-=PLAYERS.dt.isz+PLAYERS.dt.idsz;
		}
	}
	else{
		ctx.fillStyle="#"+STATUS[1].w[0];
		var sx=map(LERP_COUNTER,0,1,cnv.width-PLAYERS.dt.sz-PLAYERS.dt.isz-PLAYERS.dt.idsz,0);
		var sy=map(LERP_COUNTER,0,1,PLAYERS.dt.sz+PLAYERS.dt.idsz,0);
		var bx=map(LERP_COUNTER,0,1,cnv.width-PLAYERS.dt.sz-PLAYERS.dt.idsz,cnv.width);
		var by=map(LERP_COUNTER,0,1,PLAYERS.dt.sz+PLAYERS.dt.isz+PLAYERS.dt.idsz,cnv.height);
		ctx.fillRect(sx,sy,bx-sx,by-sy);
		ctx.fillStyle=`#aaaaaa${hex(parseInt(map(LERP_COUNTER,0,1,0,120)))}`;
		ctx.fillRect(sx,sy,bx-sx,by-sy);
		if (STATUS[0]==6){
			ctx.fillStyle="#"+STATUS[1].w[0];
			ctx.textAlign="center";
			ctx.textBaseline="middle";
			ctx.font=`${parseInt(map(LERP_COUNTER,0,1,0,100))}px SnigletB`;
			ctx.fillText(STATUS[1].w[1],cnv.width/2,cnv.height/2-40);
			ctx.font=`${parseInt(map(LERP_COUNTER,0,1,0,25))}px SnigletB`;
			var y=cnv.height/2+20;
			for (var cl of STATUS[1].l){
				ctx.fillStyle="#"+cl[0];
				ctx.fillText(cl[1],cnv.width/2,y);
				y+=40;
			}
		}
		if (LERP_COUNTER<1){
			LERP_COUNTER=Math.min(LERP_COUNTER+0.025,1);
		}
	}
	if (STATUS[0]==1){
		ctx.fillStyle="#aaaaaa80";
		ctx.fillRect(0,0,cnv.width,cnv.height);
		ctx.fillStyle="#0a0a0a";
		ctx.textAlign="center";
		ctx.textBaseline="middle";
		ctx.font="55px SnigletB";
		ctx.fillText("Waiting for players...",cnv.width/2,cnv.height/2-40);
		ctx.fillStyle="#696969";
		ctx.font="25px SnigletB";
		ctx.fillText(`Players: ${PLAYERS.l.length}/${STATUS[1]}`,cnv.width/2,cnv.height/2+10);
	}
	if (STATUS[0]==2){
		ctx.fillStyle="#aaaaaa80";
		ctx.fillRect(0,0,cnv.width,cnv.height);
		ctx.fillStyle="#0a0a0a";
		ctx.textAlign="center";
		ctx.textBaseline="middle";
		ctx.font="100px SnigletB";
		ctx.fillText(STATUS[1],cnv.width/2,cnv.height/2-40);
	}
	ctx.fillStyle="#000000";
	ctx.textAlign="left";
	ctx.textBaseline="top";
	ctx.font="20px Sniglet";
	ctx.fillText(GAME_ID,5,5);
}
function to_rgba(c){
	if (c.length==7){
		return c;
	}
	return "rgba("+parseInt(c.slice(1,3),16)+","+parseInt(c.slice(3,5),16)+","+parseInt(c.slice(5,7),16)+","+parseInt(c.slice(7,9),16)/255+")";
}
function color(r,g,b,a){
	function _c(args,s1,s2,s3,s4){
		function _cmp(a,s){
			return ((s==1&&a!=undefined)||(s==0&&a==undefined));
		}
		return (_cmp(args[0],s1)==true&&_cmp(args[1],s2)==true&&_cmp(args[2],s3)==true&&_cmp(args[3],s4)==true);
	}
	function _h(v){
		if (v.toString(16).length==2){
			return v.toString(16);
		}
		else{
			return "0"+v.toString(16);
		}
	}
	if (_c([r,g,b,a],1,1,0,0)==true&&r.toString()===r){
		a=g+0;
		g=parseInt(r.substring(3,5),16);
		b=parseInt(r.substring(5,7),16);
		r=parseInt(r.substring(1,3),16);
	}
	if (_c([r,g,b,a],1,0,0,0)==true){
		if (typeof r==String){
			return r;
		}
		else{
			return "#"+_h(r)+_h(r)+_h(r);
		}
	}
	if (_c([r,g,b,a],1,1,0,0)==true){
		return "rgba("+r+","+r+","+r+","+g/100+")";
	}
	if (_c([r,g,b,a],1,1,1,0)==true){
		return "#"+_h(r)+_h(g)+_h(b);
	}
	if (_c([r,g,b,a],1,1,1,1)==true){
		return "rgba("+r+","+g+","+b+","+a/100+")";
	}
	return null;
}
function hex(v){
	if (v<=0){
		return "00";
	}
	if (v.toString(16).length==2){
		return v.toString(16);
	}
	else{
		return "0"+v.toString(16);
	}
}
function map(v,aa,ab,ba,bb){
	return (v-aa)/(ab-aa)*(bb-ba)+ba;
}