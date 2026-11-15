
/* ================= projection ================= */
const px=l=>(l+180)/360;
const py=l=>{const s=Math.sin(l*Math.PI/180);return .5-Math.log((1+s)/(1-s))/(4*Math.PI);};
const cv=document.getElementById('cv'), ctx=cv.getContext('2d',{alpha:false});
let W=0,H=0,DPR=1;
const view={cx:.5,cy:.5,z:1};
const sx=x=>(x-view.cx)*view.z+W/2, sy=y=>(y-view.cy)*view.z+H/2;
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const $=s=>document.getElementById(s);

/* ================= data ================= */
const LINES=PACK.lines, STN=PACK.stations, FUT=PACK.future, BASE=PACK.base, CT=PACK.counts;
const LMAP=Object.fromEntries(LINES.map(l=>[l.id,l]));
const SMAP=Object.fromEntries(STN.map(s=>[s.n,s]));
const SYSNAME={dmrc:'Delhi Metro Rail Corporation',nmrc:'Noida Metro Rail Corporation',
  hmrtc:'Haryana Mass Rapid Transport Corporation',ncrtc:'NCR Transport Corporation'};
const SYSLAB={dmrc:'The Delhi Metro',nmrc:'Noida Metro',hmrtc:'Rapid Metro Gurugram',
  ncrtc:'Namo Bharat - Regional Rail, Not Delhi Metro'};
function proj(g){const o=new Array(g.length);for(let i=0;i<g.length;i++)o[i]=[px(g[i][0]),py(g[i][1])];return o;}
for(const l of LINES) l.P=l.segs.map(proj);
for(const s of STN) s.P=[px(s.ll[0]),py(s.ll[1])];
for(const c of FUT){ c.PZ=proj(c.zone); for(const s of c.st) s.P=[px(s.ll[0]),py(s.ll[1])]; }
for(const b of BASE.bd) b.P=b.r.map(proj);
for(const w of BASE.water) w.P=proj(w.g);
for(const r of BASE.roads) r.P=proj(r.g);
for(const r of BASE.rail) r.P=proj(r.g);
for(const p of BASE.places) p.P=[px(p.ll[0]),py(p.ll[1])];
for(const s of STN) s.ix = s.l.length>1 || !!(PACK.branchIx&&PACK.branchIx[s.n]);
FUT.forEach((f,i)=>{ f.id='f'+i; });
STN.forEach((s,i)=>{ s.ph=(i*0.6180339887)%1; });
const FMAP=Object.fromEntries(FUT.map(f=>[f.id,f]));

/* Stations one walk apart that carry different names. Without these the route finder
   would send a reader the long way round a change they make every day. */
const LINK=[['Sarai Kale Khan','Sarai Kale Khan - Nizamuddin'],
            ['New Ashok Nagar RRTS','New Ashok Nagar'],
            ['Anand Vihar RRTS','Anand Vihar'],
            ['Noida Sector 51','Noida Sector 52'],
            ['New Delhi','New Delhi Airport Express Terminal']].filter(x=>SMAP[x[0]]&&SMAP[x[1]]);

/* ================= theme ================= */
let C={};
function readTheme(){
  const cs=getComputedStyle(document.documentElement), g=n=>cs.getPropertyValue(n).trim();
  C={bg:g('--bg'),land:g('--land'),water:g('--water'),road:g('--road'),road2:g('--road2'),
     rail:g('--rail'),bd:g('--bd'),ink:g('--ink'),mut:g('--mut'),dim:g('--dim'),ca:g('--ca'),
     panel:g('--panel'),ix:g('--ix')||g('--ca'),glow:+g('--glow')||0};
}
function markTheme(){
  const t=document.documentElement.getAttribute('data-theme')||'dark';
  document.querySelectorAll('#themes button').forEach(b=>b.classList.toggle('on',b.dataset.t===t));
  readTheme(); STATIC.key=null;
}

/* ================= view ================= */
let FIT=null, drawerOpen=true;
/* every drawn thing, so panning can reach Meerut and Greater Noida but no further */
const NETB=(function(){
  let x0=1,y0=1,x1=0,y1=0;
  const eat=p=>{ if(p[0]<x0)x0=p[0]; if(p[0]>x1)x1=p[0]; if(p[1]<y0)y0=p[1]; if(p[1]>y1)y1=p[1]; };
  for(const l of LINES) for(const g of l.P) for(const p of g) eat(p);
  for(const f of FUT) for(const p of f.PZ) eat(p);
  const mx=(x1-x0)*0.05, my=(y1-y0)*0.05;
  return {w:x0-mx,e:x1+mx,n:y0-my,s:y1+my};
})();
let ZMIN=90000;
function homeBounds(){
  /* frame the network, not the district outline: the NCT box reaches Narela, where
     no line goes, and would leave the metro sitting low and small in the frame */
  let x0=1,y0=1,x1=0,y1=0;
  for(const l of LINES){ if(l.sys!=='dmrc') continue;
    for(const g of l.P) for(const p of g){
      if(p[0]<x0)x0=p[0]; if(p[0]>x1)x1=p[0]; if(p[1]<y0)y0=p[1]; if(p[1]>y1)y1=p[1]; } }
  const mx=(x1-x0)*0.06, my=(y1-y0)*0.06;
  return {w:x0-mx,e:x1+mx,n:y0-my,s:y1+my};
}
function padding(){
  const wide=window.innerWidth>1000;
  return wide?{l:24,r:(drawerOpen?356:82),t:56,b:44}:{l:14,r:14,t:52,b:26};
}
function fit(b){
  b=b||FIT||(FIT=homeBounds());
  const pad=padding();
  const aw=Math.max(120,W-pad.l-pad.r), ah=Math.max(120,H-pad.t-pad.b);
  view.z=Math.min(aw/Math.max(1e-6,b.e-b.w), ah/Math.max(1e-6,b.s-b.n))*0.96;
  view.cx=(b.w+b.e)/2 + ((pad.r-pad.l)/2)/view.z;
  view.cy=(b.n+b.s)/2 + ((pad.b-pad.t)/2)/view.z;
  clampView();
}
function resize(){
  DPR=Math.min(2,window.devicePixelRatio||1);
  W=cv.clientWidth; H=cv.clientHeight;
  cv.width=Math.round(W*DPR); cv.height=Math.round(H*DPR);
  ctx.setTransform(DPR,0,0,DPR,0,0);
  /* the floor is whatever shows the whole network — you cannot zoom out past it */
  ZMIN=Math.min(W/Math.max(1e-6,NETB.e-NETB.w), H/Math.max(1e-6,NETB.s-NETB.n))*0.98;
  STATIC.key=null;
}
/* Two rules keep the reader on the network. Zoom cannot go wider than the whole
   drawn system, and the centre is held so the frame always sits over it — pan to
   the edge and it stops, instead of drifting into empty sheet. */
function clampView(){
  view.z=Math.max(ZMIN,Math.min(48000000,view.z));
  const hw=W/2/view.z, hh=H/2/view.z, pad=padding();
  const ex=Math.max(pad.l,pad.r)/view.z, ey=Math.max(pad.t,pad.b)/view.z;
  const w0=NETB.w-ex, w1=NETB.e+ex, n0=NETB.n-ey, n1=NETB.s+ey;
  const loX=w0+hw, hiX=w1-hw;
  view.cx = loX>hiX ? (w0+w1)/2 : Math.min(hiX,Math.max(loX,view.cx));
  const loY=n0+hh, hiY=n1-hh;
  view.cy = loY>hiY ? (n0+n1)/2 : Math.min(hiY,Math.max(loY,view.cy));
  STATIC.key=null;
}

/* ================= the static layer ================= */
/* The network is cached, but the paths it was built from are kept so the live
   layer can stroke them again each frame without rebuilding any geometry. */
let LPATH=[], RPATH=[], FLOWW=2;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const STATIC={key:null,cv:document.createElement('canvas'),ctx:null};
STATIC.ctx=STATIC.cv.getContext('2d');
function path1(c,g,close){
  if(g.length<2) return;
  c.moveTo(sx(g[0][0]),sy(g[0][1]));
  for(let i=1;i<g.length;i++) c.lineTo(sx(g[i][0]),sy(g[i][1]));
  if(close) c.closePath();
}
function keyOf(){
  return [Math.round(view.cx*1e7),Math.round(view.cy*1e7),Math.round(view.z),W,H,
          document.documentElement.getAttribute('data-theme'),[...SELL].sort().join(','),[...SELF].sort().join(','),showFut?1:0,
          ROUTE?ROUTE.key:''].join('|');
}
function renderStatic(){
  const c=STATIC.ctx;
  STATIC.cv.width=Math.round(W*DPR); STATIC.cv.height=Math.round(H*DPR);
  c.setTransform(DPR,0,0,DPR,0,0);
  c.fillStyle=C.bg; c.fillRect(0,0,W,H);
  /* widths are quoted at the opening view; the raw zoom number runs to 10^7 on a
     city map, so multiplying stroke widths by it directly is useless */
  const z=view.z, S=Math.max(.5,Math.min(9,Math.pow(z/470000,.42)));

  /* --- the city underneath --- */
  c.beginPath();
  for(const b of BASE.bd){ if(b.lvl!=='4') continue; for(const g of b.P) path1(c,g,true); }
  c.fillStyle=C.land; c.fill('evenodd');
  c.beginPath();
  for(const b of BASE.bd){ if(b.lvl!=='5'||/Delhi/i.test(b.n)) continue; for(const g of b.P) path1(c,g,true); }
  c.lineWidth=.7*S; c.globalAlpha=.4; c.strokeStyle=C.bd; c.stroke(); c.globalAlpha=1;
  c.beginPath();
  for(const b of BASE.bd){ if(b.lvl!=='4') continue; for(const g of b.P) path1(c,g,true); }
  c.lineWidth=1.15*S; c.strokeStyle=C.bd; c.stroke();
  if(z>1100000){
    c.beginPath();
    for(const b of BASE.bd){ if(b.lvl!=='5'||!/Delhi/i.test(b.n)) continue; for(const g of b.P) path1(c,g,true); }
    c.lineWidth=.6*S; c.globalAlpha=.5; c.strokeStyle=C.bd; c.stroke(); c.globalAlpha=1;
  }
  c.lineCap='round'; c.lineJoin='round';
  c.beginPath(); for(const w of BASE.water) if(w.t==='canal') path1(c,w.P,false);
  c.lineWidth=.75*S; c.strokeStyle=C.water; c.globalAlpha=.55; c.stroke(); c.globalAlpha=1;
  c.beginPath(); for(const w of BASE.water) if(w.t==='river') path1(c,w.P,false);
  c.lineWidth=2.1*S; c.strokeStyle=C.water; c.stroke();

  const near=Math.min(1,Math.max(0,(Math.log(z)-Math.log(400000))/Math.log(30)));
  c.globalAlpha=.55+.45*near;
  if(z>900000){ c.beginPath(); for(const r of BASE.roads) if(r.c===1) path1(c,r.P,false);
    c.lineWidth=.5*S; c.strokeStyle=C.road2; c.stroke(); }
  if(z>330000){ c.beginPath(); for(const r of BASE.roads) if(r.c===2) path1(c,r.P,false);
    c.lineWidth=.6*S; c.strokeStyle=C.road; c.stroke(); }
  c.beginPath(); for(const r of BASE.roads) if(r.c===3) path1(c,r.P,false);
  c.lineWidth=1.05*S; c.strokeStyle=C.road; c.stroke();
  c.globalAlpha=1;
  if(z>420000){ c.beginPath(); for(const r of BASE.rail) path1(c,r.P,false);
    c.lineWidth=.5*S; c.strokeStyle=C.rail; c.stroke(); }

  /* --- what is being built --- */
  if(showFut&&!ROUTE) for(const f of FUT){
    const on=SELF.has(f.id), off=anySel()&&!on;
    c.save();
    c.setLineDash([6*S,5*S]); c.lineWidth=(on?2.2:(f.ph==='4'?1.5:1.2))*S;
    c.strokeStyle=on?C.ca:(f.ph==='4'?'#7C8AA0':'#5A6678');
    c.globalAlpha=off?.16:(on?1:(f.ph==='4'?.8:.55));
    c.beginPath(); path1(c,f.PZ,true); c.stroke();
    if(on&&C.glow){
      c.globalCompositeOperation='lighter'; c.setLineDash([]);
      c.lineWidth=9*S; c.globalAlpha=.10; c.stroke();
      c.globalCompositeOperation='source-over';
    }
    c.restore();
  }

  /* --- the metro --- */
  const lw=k=>Math.max(1.4,Math.min(26,2.9*S*k));
  const paths=LINES.map(l=>{const p=new Path2D();
    for(const g of l.P){ if(g.length<2) continue;
      p.moveTo(sx(g[0][0]),sy(g[0][1]));
      for(let i=1;i<g.length;i++) p.lineTo(sx(g[i][0]),sy(g[i][1])); }
    return p;});
  const lit=id=>!ROUTE&&!futOnly()&&onL(id);
  /* A dashed stroke has to walk every vertex, so the travelling lights ride a
     thinned copy of the same geometry — invisible at this scale, and it buys back
     the frame rate the effect costs. */
  const step = z<900000 ? 4 : z<3000000 ? 3 : 2;
  LPATH=[];
  for(let i=0;i<LINES.length;i++){
    const l=LINES[i]; if(!lit(l.id)) continue;
    const p=new Path2D();
    for(const g of l.P){
      if(g.length<2) continue;
      p.moveTo(sx(g[0][0]),sy(g[0][1]));
      for(let k=step;k<g.length;k+=step) p.lineTo(sx(g[k][0]),sy(g[k][1]));
      const e=g[g.length-1]; p.lineTo(sx(e[0]),sy(e[1]));
    }
    LPATH.push({p:p,id:l.id,c:l.c});
  }
  FLOWW=lw(1);
  c.lineCap='round'; c.lineJoin='round';
  if(C.glow){
    /* neon in additive passes: a wide cool halo, a tighter hot one, then the colour
       core and a near-white filament, so crossings burn brighter than the tubes */
    c.globalCompositeOperation='lighter';
    for(const pass of [[13,.055],[6.5,.085],[3.0,.13]]){
      c.lineWidth=lw(pass[0]);
      for(let i=0;i<LINES.length;i++){
        if(!lit(LINES[i].id)) continue;
        c.strokeStyle=LINES[i].c; c.globalAlpha=pass[1]; c.stroke(paths[i]);
      }
    }
    c.globalCompositeOperation='source-over'; c.globalAlpha=1;
  }
  for(let i=0;i<LINES.length;i++){
    c.lineWidth=lw(1); c.strokeStyle=LINES[i].c;
    c.globalAlpha=lit(LINES[i].id)?1:(futOnly()?.12:(ROUTE?.17:.14)); c.stroke(paths[i]);
  }
  if(C.glow){
    c.globalCompositeOperation='lighter';
    for(let i=0;i<LINES.length;i++){
      if(!lit(LINES[i].id)) continue;
      c.lineWidth=Math.max(.6,lw(1)*0.30); c.strokeStyle='#ffffff'; c.globalAlpha=.30; c.stroke(paths[i]);
    }
    c.globalCompositeOperation='source-over';
  }
  c.globalAlpha=1;
  RPATH=[];
  /* the found journey, traced over a network turned down to a whisper */
  if(ROUTE){
    const legPath=leg=>{ const p=new Path2D();
      for(let i=0;i<leg.stops.length;i++){ const s=SMAP[leg.stops[i]];
        if(i) p.lineTo(sx(s.P[0]),sy(s.P[1])); else p.moveTo(sx(s.P[0]),sy(s.P[1])); }
      return p; };
    const paths2=ROUTE.legs.map(legPath);
    RPATH=ROUTE.legs.map((leg,i)=>({p:paths2[i],c:leg.line?LMAP[leg.line].c:C.ix}));
    if(C.glow){
      c.globalCompositeOperation='lighter';
      for(const pass of [[11,.07],[5.5,.10],[2.6,.15]]){
        c.lineWidth=lw(pass[0]);
        for(let i=0;i<ROUTE.legs.length;i++){
          const leg=ROUTE.legs[i];
          c.strokeStyle=leg.line?LMAP[leg.line].c:C.ix; c.globalAlpha=pass[1]; c.stroke(paths2[i]);
        }
      }
      c.globalCompositeOperation='source-over'; c.globalAlpha=1;
    }
    for(let i=0;i<ROUTE.legs.length;i++){
      const leg=ROUTE.legs[i];
      if(!leg.line) c.setLineDash([4*S,4*S]);
      c.lineWidth=lw(1.7); c.strokeStyle=leg.line?LMAP[leg.line].c:C.ix; c.globalAlpha=1; c.stroke(paths2[i]);
      c.setLineDash([]);
    }
    if(C.glow){
      c.globalCompositeOperation='lighter';
      for(let i=0;i<ROUTE.legs.length;i++){
        c.lineWidth=Math.max(.6,lw(1.7)*0.28); c.strokeStyle='#ffffff'; c.globalAlpha=.34; c.stroke(paths2[i]);
      }
      c.globalCompositeOperation='source-over'; c.globalAlpha=1;
    }
  }
  STATIC.key=keyOf();
}

/* ================= live layer ================= */
let selStn=null, hover=null, ROUTE=null, showFut=true;
/* Selection is a set, not one line at a time. A reader who wants the Blue Line and
   the Pink Line on screen together is asking a real question — where do they meet,
   how far apart do they run, what does the east of the city look like without the
   rest of the network on top of it — and one-at-a-time cannot answer it. Cards
   toggle in and out; the map, the labels, the running orders, the interchange list
   and the share text all follow whatever is in the set. */
const SELL=new Set(), SELF=new Set();
const anySel =()=>SELL.size>0||SELF.size>0;
const futOnly=()=>SELF.size>0&&SELL.size===0;
const onL=id=>SELL.size===0||SELL.has(id);
const onS=s=>SELL.size===0||s.l.some(id=>SELL.has(id));
function stationRadius(){ const z=view.z;
  return z>9000000?8.5:z>4500000?7:z>2200000?5.8:z>1100000?4.8:z>620000?4:z>330000?3.2:z>190000?2.5:1.9; }
function drawStations(){
  const z=view.z, r=stationRadius(), T=performance.now();
  /* Zoomed in, the tubes get fat. A station mark sized only by zoom disappears
     inside its own line, so both marks are also floored against the line width. */
  const S=Math.max(.5,Math.min(9,Math.pow(z/470000,.42))), LW=Math.max(1.4,Math.min(26,2.9*S));
  const IR=Math.max(r*1.62, LW*0.80), PR=Math.max(r, LW*0.34);
  if(showFut && !ROUTE && (SELF.size||z>320000)) for(const f of FUT){
    const on=SELF.has(f.id), off=anySel()&&!on;
    if(off) continue;
    for(const s of f.st){
      const X=sx(s.P[0]),Y=sy(s.P[1]);
      if(X<-20||Y<-20||X>W+20||Y>H+20) continue;
      if(on&&C.glow){
        ctx.globalCompositeOperation='lighter';
        ctx.beginPath(); ctx.arc(X,Y,r*2.6,0,7); ctx.fillStyle=C.ca; ctx.globalAlpha=.16; ctx.fill();
        ctx.globalCompositeOperation='source-over'; ctx.globalAlpha=1;
      }
      ctx.beginPath(); ctx.arc(X,Y,r*(on?0.95:0.72),0,7); ctx.fillStyle=C.bg; ctx.fill();
      ctx.lineWidth=on?Math.max(1.6,r*0.5):1.3; ctx.setLineDash(on?[]:[2,2]);
      ctx.strokeStyle=on?C.ca:(f.ph==='4'?'#8C9AB0':'#66738A'); ctx.stroke(); ctx.setLineDash([]);
    }
  }
  const onlyIx = z<300000 && !SELL.size && !ROUTE;
  for(const s of STN){
    const X=sx(s.P[0]),Y=sy(s.P[1]);
    if(X<-20||Y<-20||X>W+20||Y>H+20) continue;
    const inR = ROUTE && ROUTE.stops.has(s.n);
    if(futOnly() && !s.ix) continue;
    if(!onS(s)) continue;
    if(ROUTE && !inR && !s.ix) continue;
    if(onlyIx && !s.ix) continue;
    const on = s===selStn, hv = s===hover;
    const col=s.ix?C.ix:(LMAP[s.l[0]]?LMAP[s.l[0]].c:C.mut);
    if(C.glow&&(!ROUTE||inR)){
      ctx.globalCompositeOperation='lighter';
      ctx.beginPath(); ctx.arc(X,Y,s.ix?IR*2.3:PR*2.6,0,7);
      ctx.fillStyle=s.ix?C.ix:col; ctx.globalAlpha=s.ix?.15:.10; ctx.fill();
      ctx.globalCompositeOperation='source-over'; ctx.globalAlpha=1;
    }
    ctx.globalAlpha=(ROUTE&&!inR)?.3:(futOnly()?.4:1);
    if(s.ix){
      /* An interchange is where the network actually does something, so it gets the
         loudest mark on the map: a ring split into the colours of the lines that meet
         there, a white filament core, and a halo that breathes outward on a stagger. */
      if(C.glow && !REDUCED && !futOnly() && (!ROUTE||inR)){
        const ph=(T/2400+s.ph)%1, ease=1-Math.pow(1-ph,2);
        const rr=IR*1.05+ease*IR*2.4, fade=1-ph;
        ctx.globalCompositeOperation='lighter';
        /* the ring that travels out */
        ctx.beginPath(); ctx.arc(X,Y,rr,0,7);
        ctx.lineWidth=Math.max(1.2,IR*0.34*fade+1); ctx.strokeStyle=C.ix;
        ctx.globalAlpha=fade*0.62; ctx.stroke();
        /* and a soft bloom that stays put and breathes */
        const br=0.55+0.45*Math.sin((T/1500+s.ph*6.28));
        ctx.beginPath(); ctx.arc(X,Y,IR*1.5,0,7);
        ctx.fillStyle=C.ix; ctx.globalAlpha=0.05+0.07*br; ctx.fill();
        ctx.globalCompositeOperation='source-over'; ctx.globalAlpha=1;
      }
      ctx.beginPath(); ctx.arc(X,Y,IR,0,7); ctx.fillStyle=C.bg; ctx.fill();
      const seg=s.l.length, step=Math.PI*2/seg, gap=seg>1?Math.min(.30,step*0.14):0;
      ctx.lineWidth=Math.max(1.8,IR*0.36); ctx.lineCap='butt';
      for(let i=0;i<seg;i++){
        const l=LMAP[s.l[i]];
        ctx.beginPath();
        ctx.arc(X,Y,IR,-Math.PI/2+i*step+gap/2,-Math.PI/2+(i+1)*step-gap/2);
        ctx.strokeStyle=l?l.c:C.ix; ctx.stroke();
      }
      ctx.lineCap='round';
      if(C.glow){
        ctx.globalCompositeOperation='lighter';
        ctx.beginPath(); ctx.arc(X,Y,IR,0,7);
        ctx.lineWidth=Math.max(.7,IR*0.13); ctx.strokeStyle=C.ix; ctx.globalAlpha=.55; ctx.stroke();
        ctx.globalCompositeOperation='source-over'; ctx.globalAlpha=1;
      }
      ctx.beginPath(); ctx.arc(X,Y,IR*0.40,0,7); ctx.fillStyle=C.glow?'#fff':C.ink; ctx.fill();
    }else{
      ctx.beginPath(); ctx.arc(X,Y,PR,0,7); ctx.fillStyle=C.bg; ctx.fill();
      ctx.lineWidth=Math.max(1.5,PR*0.64); ctx.strokeStyle=col; ctx.stroke();
    }
    ctx.globalAlpha=1;
    if(on||hv||(ROUTE&&(s.n===ROUTE.from||s.n===ROUTE.to))){
      ctx.beginPath(); ctx.arc(X,Y,(s.ix?IR:PR)*1.9,0,7);
      ctx.lineWidth=Math.max(1.8,PR*0.3); ctx.strokeStyle=C.ix; ctx.globalAlpha=on?.95:.6; ctx.stroke(); ctx.globalAlpha=1;
    }
  }
}
function drawPlaces(placed){
  const z=view.z, min = z>620000?3:(z>330000?4:5), narrow=W<900;
  ctx.textBaseline='middle'; ctx.textAlign='center';
  const pool=BASE.places.filter(p=>p.r===9?z>900000:p.r>=min).sort((a,b)=>b.r-a.r);
  for(const p of pool){
    const X=sx(p.P[0]),Y=sy(p.P[1]);
    if(X<50||X>W-50||Y<34||Y>H-34) continue;
    const big=p.r>=4, mark=p.r===9;
    ctx.font=(mark?'600 ':(big?'700 ':'600 '))+(narrow?(big?10:9):(big?12:10.5))+"px 'Sora',system-ui,sans-serif";
    const w=ctx.measureText(p.n).width, box=[X-w/2-5,Y-8,X+w/2+5,Y+8];
    let clash=false;
    for(const b of placed){ if(box[0]<b[2]&&box[2]>b[0]&&box[1]<b[3]&&box[3]>b[1]){clash=true;break;} }
    if(clash) continue;
    placed.push(box);
    if(mark){ ctx.beginPath(); ctx.arc(X,Y-11,2.1,0,7); ctx.fillStyle=C.dim; ctx.fill(); }
    ctx.lineWidth=3.4; ctx.strokeStyle=C.bg; ctx.strokeText(p.n,X,Y);
    ctx.fillStyle=big?C.mut:C.dim; ctx.globalAlpha=ROUTE?.45:(mark?.95:(big?.85:.7));
    ctx.fillText(p.n,X,Y); ctx.globalAlpha=1;
  }
  ctx.textAlign='left';
}
function drawLabels(){
  const z=view.z, placed=[];
  if(z<300000&&!ROUTE&&!anySel()){ drawPlaces(placed); return; }
  const min = z>800000?0 : z>430000?1 : 2;
  const cap = z>1600000?120 : z>800000?76 : 46;
  const narrow=W<900;
  ctx.font=(narrow?'600 9.5px':'600 11px')+" 'Sora',system-ui,sans-serif";
  ctx.textBaseline='middle';
  drawPlaces(placed);
  const pool=futOnly()?[]:STN.filter(s=>onS(s)&&(!ROUTE||ROUTE.stops.has(s.n)))
    .sort((a,b)=>(b.ix-a.ix)||(b.l.length-a.l.length));
  for(const s of pool){
    if(!ROUTE && s.l.length<min && !s.ix) continue;
    const X=sx(s.P[0]),Y=sy(s.P[1]);
    if(X<44||X>W-44||Y<26||Y>H-26) continue;
    const w=ctx.measureText(s.n).width, box=[X+8,Y-8,X+13+w,Y+8];
    let clash=false;
    for(const b of placed){ if(box[0]<b[2]&&box[2]>b[0]&&box[1]<b[3]&&box[3]>b[1]){clash=true;break;} }
    if(clash) continue;
    placed.push(box);
    ctx.lineWidth=3.2; ctx.strokeStyle=C.bg; ctx.strokeText(s.n,X+9,Y);
    ctx.fillStyle=s.ix?C.ink:C.mut; ctx.fillText(s.n,X+9,Y);
    if(placed.length>=cap) break;
  }
  if(showFut && !ROUTE && (SELF.size||z>1300000)){
    ctx.font=(narrow?'600 9.5px':'600 10.5px')+" 'Sora',system-ui,sans-serif";
    for(const f of FUT){ if(SELF.size&&!SELF.has(f.id)) continue; for(const s of f.st){
      const X=sx(s.P[0]),Y=sy(s.P[1]);
      if(X<44||X>W-44||Y<26||Y>H-26) continue;
      const w=ctx.measureText(s.n).width, box=[X+8,Y-7,X+13+w,Y+7];
      let clash=false;
      for(const b of placed){ if(box[0]<b[2]&&box[2]>b[0]&&box[1]<b[3]&&box[3]>b[1]){clash=true;break;} }
      if(clash) continue;
      placed.push(box);
      ctx.lineWidth=3; ctx.strokeStyle=C.bg; ctx.strokeText(s.n,X+9,Y);
      ctx.fillStyle=SELF.has(f.id)?C.ink:C.dim; ctx.fillText(s.n,X+9,Y);
    } }
  }
}
/* Something moving through the tubes. A dash pattern with long gaps, stroked over
   the lines each frame with the offset creeping backwards, reads as a run of lights
   travelling the corridor. Additive on the dark theme so the tube brightens under
   each one rather than being painted over; on the paper themes it is a pale streak
   instead, because adding light to white does nothing. */
function drawFlow(){
  if(REDUCED || futOnly()) return;
  const list = ROUTE ? RPATH : LPATH;
  if(!list.length) return;
  const S=Math.max(.5,Math.min(9,Math.pow(view.z/470000,.42)));
  const dash=Math.max(8,16*S), gap=Math.max(78,158*S), period=dash+gap;
  const off=-((performance.now()/1000)*Math.max(34,58*S))%period;
  /* One pass, not two: a dashed stroke is the expensive part of the frame, and a
     single wide white one over the coloured tube already bleeds colour at its
     edges. Two passes cost about seven frames a second and looked no better. */
  ctx.save();
  ctx.lineCap='round'; ctx.lineJoin='round';
  ctx.setLineDash([dash,gap]); ctx.lineDashOffset=off;
  if(C.glow){
    ctx.globalCompositeOperation='lighter';
    ctx.strokeStyle='#ffffff'; ctx.globalAlpha=.24;
    ctx.lineWidth=Math.max(1.5,FLOWW*0.78);
  }else{
    /* on paper, a bright streak rather than added light, and gentler still,
       so it reads as a highlight travelling and never as a gap in the line */
    ctx.strokeStyle='#ffffff'; ctx.globalAlpha=.30;
    ctx.lineWidth=Math.max(1.2,FLOWW*0.42);
  }
  for(const it of list) ctx.stroke(it.p);
  ctx.setLineDash([]); ctx.restore(); ctx.globalAlpha=1;
  ctx.globalCompositeOperation='source-over';
}
function draw(){
  if(STATIC.key!==keyOf()) renderStatic();
  ctx.setTransform(1,0,0,1,0,0); ctx.drawImage(STATIC.cv,0,0);
  ctx.setTransform(DPR,0,0,DPR,0,0);
  drawFlow(); drawStations(); drawLabels();
}

/* ================= interaction ================= */
let dragging=false,lastX=0,lastY=0,moved=0;
function rel(e){const r=cv.getBoundingClientRect();return {x:e.clientX-r.left,y:e.clientY-r.top};}
/* A finger dragging down the page must scroll it, so touch never drags the map —
   two fingers do that. A finger that lands and lifts without travelling is still a
   tap, and still picks a station. */
let tapX=0,tapY=0,tapT=false;
cv.addEventListener('pointerdown',e=>{
  if(e.pointerType==='touch'){ tapT=true; tapX=e.clientX; tapY=e.clientY; return; }
  tapT=false; dragging=true;moved=0;lastX=e.clientX;lastY=e.clientY;
  cv.setPointerCapture(e.pointerId);cv.classList.add('drag');});
cv.addEventListener('pointermove',e=>{
  if(dragging){
    const dx=e.clientX-lastX,dy=e.clientY-lastY; moved+=Math.abs(dx)+Math.abs(dy);
    view.cx-=dx/view.z; view.cy-=dy/view.z; lastX=e.clientX; lastY=e.clientY; clampView();
  } else hitTest(e.clientX,e.clientY);
});
cv.addEventListener('pointerup',e=>{
  if(e.pointerType==='touch'){
    if(tapT && Math.hypot(e.clientX-tapX,e.clientY-tapY)<9) select(nearest(e.clientX,e.clientY,26)||null);
    tapT=false; return;
  }
  dragging=false; cv.classList.remove('drag');
  if(moved>=5) return;
  select(nearest(e.clientX,e.clientY,20)||null);
});
cv.addEventListener('pointerleave',()=>{hover=null;$('tip').style.display='none';});
function zoomAt(X,Y,f){
  const wx=(X-W/2)/view.z+view.cx, wy=(Y-H/2)/view.z+view.cy;
  view.z*=f; clampView();
  view.cx=wx-(X-W/2)/view.z; view.cy=wy-(Y-H/2)/view.z;
}
/* A full-bleed map that eats the wheel traps a first-time reader halfway down the
   page. So a plain wheel scrolls the page as it should, and zooming asks for the
   modifier — the same bargain an embedded map makes. A trackpad pinch arrives with
   ctrlKey set, so pinch-to-zoom still works without anyone being told. */
let hintT=null;
function flashHint(){
  const h=$('shint'); h.classList.add('on');
  clearTimeout(hintT); hintT=setTimeout(()=>h.classList.remove('on'),1500);
}
cv.addEventListener('wheel',e=>{
  if(!(e.ctrlKey||e.metaKey)){ if(Math.abs(e.deltaY)>2) flashHint(); return; }
  e.preventDefault(); const p=rel(e); zoomAt(p.x,p.y,Math.exp(-e.deltaY*0.0016));
},{passive:false});
cv.addEventListener('dblclick',e=>{ const p=rel(e); zoomAt(p.x,p.y,2.1); });
let pinch=null;
cv.addEventListener('touchstart',e=>{if(e.touches.length===2){const a=e.touches[0],b=e.touches[1];
  const r=cv.getBoundingClientRect();
  pinch={d:Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY),
         x:(a.clientX+b.clientX)/2-r.left,y:(a.clientY+b.clientY)/2-r.top,
         cx:(a.clientX+b.clientX)/2,cy:(a.clientY+b.clientY)/2};}},{passive:true});
cv.addEventListener('touchmove',e=>{
  if(e.touches.length===2&&pinch){const a=e.touches[0],b=e.touches[1];
    const d=Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY);
    const cx=(a.clientX+b.clientX)/2, cy=(a.clientY+b.clientY)/2;
    view.cx-=(cx-pinch.cx)/view.z; view.cy-=(cy-pinch.cy)/view.z;   /* two fingers also drag */
    zoomAt(pinch.x,pinch.y,d/pinch.d);
    pinch.d=d; pinch.cx=cx; pinch.cy=cy; e.preventDefault();}},{passive:false});
cv.addEventListener('touchend',()=>{pinch=null;},{passive:true});

function nearest(cX,cY,tol){
  const r=cv.getBoundingClientRect(), X=cX-r.left, Y=cY-r.top;
  let best=null,bd=tol;
  for(const s of STN){
    if(!onS(s)) continue;
    const d=Math.hypot(sx(s.P[0])-X,sy(s.P[1])-Y);
    if(d<bd){bd=d;best=s;}
  }
  if(best) return best;
  for(const f of FUT) for(const s of f.st){
    const d=Math.hypot(sx(s.P[0])-X,sy(s.P[1])-Y);
    if(d<bd){bd=d;best={future:f,n:s.n,ll:s.ll,P:s.P};}
  }
  return best;
}
function hitTest(cX,cY){
  const s=nearest(cX,cY,17); hover=s&&!s.future?s:null;
  const tip=$('tip');
  if(!s){tip.style.display='none';return;}
  const lines=s.future?[s.future.nm+' · Phase '+s.future.ph]:s.l.map(id=>LMAP[id].nm);
  tip.innerHTML='<div>'+esc(s.n)+'</div><div class="t2">'+lines.map(esc).join(' · ')+
    (s.future?'':(s.ix?' <span style="color:var(--ca)">· Interchange</span>':''))+'</div>';
  tip.style.display='block';
  tip.style.left=Math.min(innerWidth-tip.offsetWidth-10,cX+14)+'px';
  tip.style.top=Math.max(6,cY-tip.offsetHeight-12)+'px';
}
let anim=null;
function animate(cx,cy,z){
  const s={cx:view.cx,cy:view.cy,z:view.z},t0=performance.now(),D=620;
  anim=()=>{const k=Math.min(1,(performance.now()-t0)/D),e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;
    view.cx=s.cx+(cx-s.cx)*e; view.cy=s.cy+(cy-s.cy)*e;
    view.z=Math.exp(Math.log(s.z)+(Math.log(z)-Math.log(s.z))*e);
    clampView(); if(k>=1) anim=null;};
}
function fitPts(pts,tight){
  if(!pts.length) return;
  let x0=1,y0=1,x1=0,y1=0;
  for(const p of pts){ if(p[0]<x0)x0=p[0]; if(p[0]>x1)x1=p[0]; if(p[1]<y0)y0=p[1]; if(p[1]>y1)y1=p[1]; }
  const pad=padding();
  const aw=Math.max(120,W-pad.l-pad.r), ah=Math.max(120,H-pad.t-pad.b);
  const tz=Math.max(ZMIN,Math.min(48000000,Math.min(aw/Math.max(1e-6,x1-x0), ah/Math.max(1e-6,y1-y0))*(tight?.86:.92)));
  animate((x0+x1)/2+((pad.r-pad.l)/2)/tz,(y0+y1)/2+((pad.b-pad.t)/2)/tz,tz);
}

/* ================= the station callout ================= */
function select(s){
  selStn=s&&!s.future?s:null;
  const d=$('callout');
  if(!s){ d.classList.remove('on'); return; }
  d.classList.add('on');
  if(s.future){
    $('ck').textContent='Under Construction · Phase '+s.future.ph;
    $('cn').textContent=s.n;
    $('clines').innerHTML='<div><i style="background:'+(s.future.ph==='4'?'#8C9AB0':'#66738A')+'"></i>'
      +esc(s.future.nm)+(s.future.lab?' · '+esc(s.future.lab):'')+'</div>';
    $('cnote').textContent='Station position from DMRC’s own KML for this corridor. The dashed outline is DMRC’s published influence zone, not a track centreline — the alignment runs inside it.';
    d.querySelector('.cbtns').style.display='none';
  }else{
    const bx=PACK.branchIx&&PACK.branchIx[s.n];
    $('ck').textContent=s.ix?'Interchange Station':'Station';
    $('cn').textContent=s.n;
    $('clines').innerHTML=s.l.map(id=>{const l=LMAP[id];
      return '<div><i style="background:'+l.c+'"></i>'+esc(l.nm)+'</div>';}).join('');
    const sys=[...new Set(s.l.map(id=>LMAP[id].sys))];
    $('cnote').textContent = bx ? bx :
      (sys.length>1?'A change between two operators: '+sys.map(x=>SYSNAME[x]).join(' and ')+'.':'');
    d.querySelector('.cbtns').style.display='flex';
  }
}
$('cx').onclick=()=>select(null);
document.querySelector('.callout .cbtns').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b||!selStn) return;
  (b.dataset.set==='a'?$('fromI'):$('toI')).value=selStn.n;
  openDrawer(true); syncGo();
});

/* ================= the line menu ================= */
const SYSORDER=['dmrc','nmrc','hmrtc','ncrtc'];
function lineCard(l){
  const seq=l.seq, n=new Set([].concat(seq,l.branch||[])).size;
  return '<button class="lcard'+(SELL.has(l.id)?' on':'')+'" data-line="'+esc(l.id)+'" aria-pressed="'
    +(SELL.has(l.id)?'true':'false')+'" style="--lc:'+l.c+'">'
    +'<span class="cbar"></span><span class="tx"><span class="nm">'+esc(l.nm)+'</span>'
    +'<span class="en">'+esc(seq[0])+' → '+esc(seq[seq.length-1])+'</span></span>'
    +'<span class="ct">'+n+'</span></button>';
}
function futCard(f){
  return '<button class="lcard'+(SELF.has(f.id)?' on':'')+'" data-fut="'+esc(f.id)+'" aria-pressed="'
    +(SELF.has(f.id)?'true':'false')+'" '
    +'style="--lc:'+(f.ph==='4'?'#8C9AB0':'#66738A')+'">'
    +'<span class="cbar dash"></span><span class="tx"><span class="nm">'+esc(f.nm)+'</span>'
    +'<span class="en">'+esc(f.lab||('Phase '+f.ph))+(f.part?' · Existing Stations Not Counted':'')+'</span></span>'
    +'<span class="ct">'+f.st.length+'</span></button>';
}
function renderMenu(){
  let h='';
  for(const sy of SYSORDER){
    const ls=LINES.filter(l=>l.sys===sy); if(!ls.length) continue;
    const note = sy==='dmrc'
      ? CT.dmrcSlots+' Line-Stations · '+CT.dmrcStations+' Distinct Buildings · '+CT.dmrcKm+' Km'
      : (ls[0].note||SYSNAME[sy]);
    h+='<div class="sysrow"><b>'+esc(SYSLAB[sy])+'</b><em>'+esc(note)+'</em></div>'
      +'<div class="grid">'+ls.map(lineCard).join('')+'</div>';
  }
  for(const ph of ['4','5']){
    const fs=FUT.filter(f=>f.ph===ph); if(!fs.length) continue;
    h+='<div class="sysrow"><b>Under Construction · Phase '+ph+'</b><em>'
      +fs.length+' Corridors · '+fs.reduce((a,f)=>a+f.st.length,0)+' Stations · DMRC Official KML</em></div>'
      +'<div class="grid">'+fs.map(futCard).join('')+'</div>';
  }
  $('menu').innerHTML=h;
  const picks=picked(), k=picks.length;
  $('clr').hidden=!k;
  $('menusub').textContent = !k
    ? LINES.length+' Lines And '+FUT.length+' Corridors Under Construction. Click As Many As You Like — They Stack.'
    : k===1 ? picks[0][1]+' — Running Order Below'
    : k+' Selected — Running Orders Below. Click A Card Again To Drop It.';
  $('showing').innerHTML = !k ? 'All Lines'
    : k===1 ? '<i class="sw" style="background:'+picks[0][0]+'"></i>'+esc(picks[0][1])
    : picks.slice(0,6).map(q=>'<i class="sw" style="background:'+q[0]+'"></i>').join('')
      +(k>6?'+'+(k-6)+' ':'')+k+' Lines';
}
/* everything currently chosen, in menu order, as [colour, name] */
function picked(){
  const out=[];
  for(const l of LINES) if(SELL.has(l.id)) out.push([l.c,l.nm]);
  for(const f of FUT) if(SELF.has(f.id)) out.push([f.ph==='4'?'#8C9AB0':'#66738A',f.nm]);
  return out;
}
function stopBtn(n,lid){
  const s=SMAP[n]; if(!s) return '';
  const others=s.l.filter(id=>id!==lid).map(id=>LMAP[id].nm.replace(/ Line$/,''));
  const bx=PACK.branchIx&&PACK.branchIx[n];
  return '<button class="stop'+(s.ix?' int':'')+'" data-n="'+esc(n)+'">'
    +'<span class="pin"><i></i></span><span class="t">'+esc(n)
    +(others.length?'<small>'+others.map(esc).join(' · ')+'</small>':(bx?'<small>Branch Junction</small>':''))
    +'</span>'+(s.ix?'<span class="x">INT</span>':'')+'</button>';
}
function stripBox(sc,title,meta,body){
  return '<div class="strip" style="--sc:'+sc+'">'
    +'<div class="sh"><div class="cbar"></div><h3>'+esc(title)+'</h3><div class="meta">'+meta+'</div></div>'
    +'<div class="stops">'+body+'</div></div>';
}
function lineStrip(l){
  const all=[...new Set([].concat(l.seq,l.branch||[]))];
  const ix=all.filter(x=>SMAP[x]&&SMAP[x].ix).length;
  let b=l.seq.map(x=>stopBtn(x,l.id)).join('');
  if(l.branch) b+='<div class="brhead">Branch · '+esc(l.branch[0])+' → '
    +esc(l.branch[l.branch.length-1])+'</div>'+l.branch.map(x=>stopBtn(x,l.id)).join('');
  return stripBox(l.c,l.nm,all.length+' Stations · '+ix+' Interchanges<br>'+esc(l.own),b);
}
function futStrip(f){
  const col=f.ph==='4'?'#8C9AB0':'#66738A';
  const b=f.st.map(x=>'<button class="stop" disabled style="cursor:default">'
    +'<span class="pin"><i style="border-style:dashed"></i></span>'
    +'<span class="t">'+esc(x.n)+'</span></button>').join('')
    +(f.part?'<div class="brhead">DMRC\u2019s KML for this corridor also lists '
      +'stations that are already open. Those are drawn on the network above, not repeated here.</div>':'');
  return stripBox(col,f.nm,f.st.length+' Stations Still To Open · Phase '+f.ph+'<br>'
    +esc(f.lab||('DMRC Phase '+f.ph))+(f.part?' · part of this corridor is already running':''),b);
}
function renderStrip(){
  let h='';
  for(const l of LINES) if(SELL.has(l.id)) h+=lineStrip(l);
  for(const f of FUT) if(SELF.has(f.id)) h+=futStrip(f);
  $('strips').innerHTML=h;
  renderMeet();
}
/* With two or more lines up, the question stops being "where does this line go" and
   becomes "where do these lines touch". That answer is not on the map at a glance —
   an interchange looks the same whether it serves your two lines or two others — so
   it is spelled out. Lines that never meet get told so, which is its own answer. */
function renderMeet(){
  const el=$('meet');
  if(SELL.size<2){ el.hidden=true; el.innerHTML=''; return; }
  el.hidden=false;
  const rows=[];
  for(const s of STN){
    const k=s.l.filter(id=>SELL.has(id));
    if(k.length>1) rows.push([s,k]);
  }
  rows.sort((a,b)=>(b[1].length-a[1].length)||a[0].n.localeCompare(b[0].n));
  const names=[...SELL].map(id=>LMAP[id].nm.replace(/ Line$/,''));
  let h='<div class="meethd"><b>Where They Meet</b><em>'
    +(rows.length ? rows.length+(rows.length===1?' Station Serves':' Stations Serve')+' More Than One Of The '
        +SELL.size+' Lines You Have Picked'
      : 'Nothing Shared Between '+esc(names.join(', ')))+'</em></div>';
  h += rows.length
    ? '<div class="meetg">'+rows.map(r=>'<button class="mtile" data-n="'+esc(r[0].n)+'">'
        +'<span class="sws">'+r[1].map(id=>'<i style="background:'+LMAP[id].c+'"></i>').join('')+'</span>'
        +'<span class="mn">'+esc(r[0].n)+'</span>'
        +'<span class="ml">'+r[1].map(id=>esc(LMAP[id].nm.replace(/ Line$/,''))).join(' · ')+'</span>'
        +'</button>').join('')+'</div>'
    : '<div class="meetnone">These lines never touch. Any journey from one to the other has to change '
      +'somewhere on a third line — put that line up too and the join will show.</div>';
  el.innerHTML=h;
}
function flyTo(name){
  const s=SMAP[name]; if(!s) return;
  select(s); animate(s.P[0],s.P[1],Math.max(view.z,3200000));
  document.querySelector('.stage').scrollIntoView({block:'center'});
}
/* the frame is fitted to everything chosen, so adding a second line pulls the view
   out to hold both rather than snapping away from the one already being read */
function fitSel(){
  if(!anySel()) return fit();
  const pts=[];
  for(const l of LINES) if(SELL.has(l.id)) for(const g of l.P) for(const q of g) pts.push(q);
  for(const f of FUT) if(SELF.has(f.id)) for(const q of f.PZ) pts.push(q);
  fitPts(pts);
}
function afterPick(){
  renderRoute(); STATIC.key=null; renderMenu(); renderStrip(); fitSel();
}
$('menu').addEventListener('click',e=>{
  const b=e.target.closest('.lcard'); if(!b) return;
  ROUTE=null; select(null);
  if(b.dataset.fut){
    const id=b.dataset.fut;
    SELF.has(id) ? SELF.delete(id) : SELF.add(id);
    if(SELF.size){ showFut=true; $('futBtn').classList.add('on'); }
  }else{
    const id=b.dataset.line;
    SELL.has(id) ? SELL.delete(id) : SELL.add(id);
  }
  afterPick();
});
$('clr').onclick=()=>{ SELL.clear(); SELF.clear(); STATIC.key=null; renderMenu(); renderStrip(); fit(); };
$('futBtn').onclick=function(){
  showFut=!showFut; this.classList.toggle('on',showFut);
  if(!showFut&&SELF.size){ SELF.clear(); renderMenu(); renderStrip(); fitSel(); }
  STATIC.key=null;
};
for(const id of ['strips','meet']) $(id).addEventListener('click',e=>{
  const b=e.target.closest('.stop,.mtile'); if(!b||!b.dataset.n) return;
  flyTo(b.dataset.n);
});

/* ================= the route finder ================= */
/* A graph over (station, line) nodes: riding one stop is an edge, changing line at a
   station is an edge with a penalty, and a named walk between two differently-named
   stations is an edge too. Dijkstra over that returns a route a Delhi commuter would
   recognise, rather than the one with the fewest kilometres. */
const R2=Math.PI/180;
function km(a,b){
  const dx=(b.ll[0]-a.ll[0])*Math.cos((a.ll[1]+b.ll[1])/2*R2)*111.32, dy=(b.ll[1]-a.ll[1])*110.57;
  return Math.hypot(dx,dy);
}
const ADJ={};
function edge(a,b,line){
  if(!SMAP[a]||!SMAP[b]||a===b) return;
  const d=km(SMAP[a],SMAP[b]);
  (ADJ[a]=ADJ[a]||[]).push({to:b,line:line,km:d});
  (ADJ[b]=ADJ[b]||[]).push({to:a,line:line,km:d});
}
for(const l of LINES)
  for(const br of [l.seq,l.branch]) if(br)
    for(let i=1;i<br.length;i++) edge(br[i-1],br[i],l.id);
for(const p of LINK) edge(p[0],p[1],null);
const CHANGE=4.2;   /* a change of platform, priced in the kilometres it is worth */
const WALK=2.4;     /* a named walk between two stations, likewise */
function route(from,to){
  if(!SMAP[from]||!SMAP[to]||from===to) return null;
  const key=(s,l)=>s+'\u0001'+(l||'');
  const dist={}, prev={}, seen={}, Q=[];
  const push=(k,d,p)=>{ if(dist[k]!==undefined&&dist[k]<=d) return; dist[k]=d; prev[k]=p; Q.push([d,k]); };
  for(const e of (ADJ[from]||[])) push(key(from,e.line),0,null);
  let endK=null;
  while(Q.length){
    Q.sort((a,b)=>a[0]-b[0]);
    const top=Q.shift(), d=top[0], k=top[1];
    if(seen[k]||d>dist[k]) continue;
    seen[k]=1;
    const i=k.indexOf('\u0001'), s=k.slice(0,i), lid=k.slice(i+1)||null;
    if(s===to){ endK=k; break; }
    for(const e of (ADJ[s]||[])){
      const pen = e.line===lid ? 0 : ((e.line===null||lid===null) ? WALK : CHANGE);
      push(key(e.to,e.line), d+e.km+pen, k);
    }
  }
  if(!endK) return null;
  const path=[];
  for(let k=endK;k;k=prev[k]){ const i=k.indexOf('\u0001');
    path.push({s:k.slice(0,i),l:k.slice(i+1)||null}); }
  path.reverse();
  const legs=[]; let cur=null, dkm=0;
  for(let i=0;i<path.length;i++){
    const p=path[i];
    if(i) dkm+=km(SMAP[path[i-1].s],SMAP[p.s]);
    if(!cur||cur.line!==p.l){ cur={line:p.l,stops:[]}; if(i) cur.stops.push(path[i-1].s); legs.push(cur); }
    if(cur.stops[cur.stops.length-1]!==p.s) cur.stops.push(p.s);
  }
  const clean=legs.filter(l=>l.stops.length>1);
  const stops=new Set();
  for(const l of clean) for(const s of l.stops) stops.add(s);
  const hops=clean.reduce((a,l)=>a+(l.line?l.stops.length-1:0),0);
  return {from:from,to:to,legs:clean,stops:stops,hops:hops,changes:Math.max(0,clean.length-1),
          km:dkm,lines:new Set(clean.map(l=>l.line).filter(Boolean)),key:from+'>'+to};
}
const HINT='<div class="hint">Pick two stations, or click any station on the map and use '
  +'<b>Set As From</b> / <b>Set As To</b>. The route is worked out over the real network — every line, '
  +'every interchange, including the ones between operators.</div>';
function renderRoute(){
  const el=$('rout');
  if(!ROUTE){ el.innerHTML=HINT; return; }
  const R=ROUTE;
  /* the time is arithmetic, and is labelled as arithmetic. DMRC publishes no live
     feed and no bulk current timetable, so nothing here is a schedule. */
  const mins=Math.round(R.hops*2.1 + R.changes*5 + 2);
  let h='<div class="rsum"><div class="big">'+R.hops+' Stop'+(R.hops===1?'':'s')
    +' · '+R.changes+' Change'+(R.changes===1?'':'s')+'</div>'
    +'<div class="sub">'+R.km.toFixed(1)+' km along the tracks, '+esc(R.from)+' to '+esc(R.to)+'.</div>'
    +'<div class="est">Roughly <b>'+mins+' minutes</b> — an estimate, not a timetable: 2.1 minutes a '
    +'stop and 5 minutes an interchange. DMRC publishes no live feed, so no tool can give you the real figure.</div></div>';
  for(const leg of R.legs){
    const l=leg.line?LMAP[leg.line]:null;
    const a=leg.stops[0], b=leg.stops[leg.stops.length-1];
    if(!l){
      h+='<div class="leg"><div class="lb" style="background:var(--ca)"></div><div class="lt">Change Systems'
        +'<small>'+esc(a)+' → '+esc(b)+' · A Linked Walk Between Two Networks</small></div></div>';
      continue;
    }
    h+='<div class="leg"><div class="lb" style="background:'+l.c+'"></div><div class="lt">'+esc(l.nm)
      +'<small><em>'+(leg.stops.length-1)+' Stops</em> · '+esc(a)+' → '+esc(b)+'</small></div></div>';
  }
  h+='<div class="hint" style="margin-top:2px">Distance is measured between the real station positions on '
    +'this map, not read off a schematic.</div>';
  el.innerHTML=h;
}
function pips(s){ return '<span class="pips">'+s.l.map(id=>'<i style="background:'+LMAP[id].c+'"></i>').join('')+'</span>'; }
function wirePick(inp,sug){
  const I=$(inp), S=$(sug);
  I.addEventListener('input',()=>{
    const q=I.value.toLowerCase().trim();
    if(!q){S.classList.remove('on');syncGo();return;}
    const hits=STN.filter(s=>s.n.toLowerCase().indexOf(q)>=0)
      .sort((a,b)=>a.n.toLowerCase().indexOf(q)-b.n.toLowerCase().indexOf(q)).slice(0,40);
    S.innerHTML=hits.length?hits.map(s=>'<button data-n="'+esc(s.n)+'">'+pips(s)+esc(s.n)+'</button>').join('')
      :'<button style="color:var(--dim)">No station matches that</button>';
    S.classList.add('on'); syncGo();
  });
  S.addEventListener('mousedown',e=>{const b=e.target.closest('button[data-n]'); if(!b) return;
    e.preventDefault(); I.value=b.dataset.n; S.classList.remove('on'); syncGo();});
  I.addEventListener('blur',()=>setTimeout(()=>S.classList.remove('on'),150));
  I.addEventListener('focus',()=>{ if(I.value) I.dispatchEvent(new Event('input')); });
  I.addEventListener('keydown',e=>{ if(e.key==='Enter'&&!$('go').disabled){S.classList.remove('on');$('go').click();} });
}
wirePick('fromI','fromS'); wirePick('toI','toS');
function syncGo(){
  const a=SMAP[$('fromI').value.trim()], b=SMAP[$('toI').value.trim()];
  $('go').disabled=!(a&&b&&a!==b);
}
$('swap').onclick=()=>{const a=$('fromI').value; $('fromI').value=$('toI').value; $('toI').value=a; syncGo();};
$('go').onclick=()=>{
  const R=route($('fromI').value.trim(),$('toI').value.trim());
  ROUTE=R; SELL.clear(); SELF.clear(); select(null); STATIC.key=null; renderMenu(); renderStrip(); renderRoute();
  if(R) fitPts([...R.stops].map(n=>SMAP[n].P),true);
};
function openDrawer(on){
  drawerOpen=on;
  $('drawer').classList.toggle('shut',!on);
  $('caret').textContent=on?'‹':'›';
}
$('dh').onclick=()=>openDrawer(!drawerOpen);

/* ================= share ================= */
/* Opens X's compose window with the text prefilled — the reader still writes and
   posts it themselves. If they have planned a journey, that journey is the post. */
const PAGE_URL='https://politypolicy.com/DelhiMetro.html';
function shareText(){
  if(ROUTE){
    const legs=ROUTE.legs.filter(l=>l.line).map(l=>LMAP[l.line].nm.replace(/ Line$/,''));
    return ROUTE.from+' to '+ROUTE.to+' on the Delhi Metro: '+ROUTE.hops+' stops, '
      +ROUTE.changes+' change'+(ROUTE.changes===1?'':'s')+', '+ROUTE.km.toFixed(1)+' km'
      +(legs.length?' via '+legs.join(', '):'')+'. Drawn where the network actually is, not the diagram.';
  }
  if(SELL.size===1){
    const l=LMAP[[...SELL][0]];
    return 'The '+l.nm+' of the Delhi Metro, drawn where it actually is — '
      +new Set([].concat(l.seq,l.branch||[])).size+' stations on the real map of Delhi.';
  }
  if(SELL.size>1){
    const ls=LINES.filter(l=>SELL.has(l.id));
    const nm=ls.map(l=>l.nm.replace(/ Line$/,''));
    const st=new Set(); for(const l of ls) for(const x of [].concat(l.seq,l.branch||[])) st.add(x);
    const met=STN.filter(s=>s.l.filter(id=>SELL.has(id)).length>1).length;
    return 'The '+nm.slice(0,-1).join(', ')+' and '+nm[nm.length-1]+' lines of the Delhi Metro on one map, '
      +'drawn where they actually are: '+st.size+' stations, '+met+' place'+(met===1?'':'s')+' they meet.';
  }
  return 'India\u2019s best metro system, drawn where it actually is: '+CT.dmrcSlots+' line-stations, '
    +CT.dmrcKm+' km, and 81,87,674 journeys on its busiest ever day.';
}
$('shareBtn').onclick=()=>{
  const u='https://x.com/intent/post?text='+encodeURIComponent(shareText())
        +'&url='+encodeURIComponent(PAGE_URL)+'&via=Tushar15';
  window.open(u,'_blank','noopener,noreferrer');
};

/* ================= chrome ================= */
const THEMES=['light','dark','news'];
function setTheme(t){
  document.documentElement.setAttribute('data-theme',t);
  try{localStorage.setItem('pp-theme',t);}catch(_){}
  markTheme();
}
$('themes').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b) return;
  /* narrow screens show only the active button, so a tap on it means "next" */
  const collapsed=getComputedStyle($('themes').querySelector('button:not(.on)')||b).display==='none';
  if(collapsed && b.classList.contains('on')){
    const now=document.documentElement.getAttribute('data-theme')||'dark';
    return setTheme(THEMES[(THEMES.indexOf(now)+1)%THEMES.length]);
  }
  setTheme(b.dataset.t);
});
$('zin').onclick=()=>zoomAt(W/2,H/2,1.7);
$('zout').onclick=()=>zoomAt(W/2,H/2,1/1.7);
$('zfit').onclick=()=>{ SELL.clear(); SELF.clear(); ROUTE=null; select(null); renderMenu(); renderStrip(); renderRoute();
  FIT=null; STATIC.key=null; fit(); };
function openSheet(on){ $('sheet').classList.toggle('on',on); $('sheetbg').classList.toggle('on',on); }
$('srcBtn').onclick=()=>openSheet(true);
$('sheetClose').onclick=()=>openSheet(false);
$('sheetbg').onclick=()=>openSheet(false);
addEventListener('keydown',e=>{if(e.key==='Escape'){openSheet(false);select(null);}});

/* ================= copy ================= */
const nFut=FUT.reduce((a,f)=>a+f.st.length,0);
/* the counters borrow the network's own colours — the map is the palette.
   Stations leads with DMRC's own 271; the 245 distinct buildings sit under it,
   because both are true and the difference is what an interchange is. */
$('tally').innerHTML=[
  [CT.dmrcSlots,'Stations',LMAP['3'].c],[Math.round(CT.dmrcKm)+' km','Of Line',LMAP['1'].c],
  [CT.dmrcInterchanges,'Interchanges','var(--ix)'],[CT.dmrcLines,'DMRC Lines',LMAP['5'].c],
  [nFut,'Stations Being Built','var(--mut)']
].map(x=>'<div class="tl" style="--tc:'+x[2]+'"><b>'+x[0]+'</b><span>'+x[1]+'</span></div>').join('');

/* Route length is the one measure on which the comparison is exact, so it is the
   one drawn. The figures are each system's own published route length. */
const VS=[['Delhi Metro',374,'me'],['London Underground',402,''],['New York Subway',399,''],
          ['Tokyo Subway',304,'']];
const vmax=Math.max(...VS.map(v=>v[1]));
$('vs').innerHTML='<div class="vsh">Route Length, Against The Networks It Is Measured Beside</div>'
 +VS.map(v=>'<div class="vsrow '+v[2]+'" style="--vc:'+(v[2]?'var(--ca)':'var(--dim)')+'">'
   +'<span class="nm">'+esc(v[0])+'</span>'
   +'<span class="track"><span class="fill" style="width:'+(v[1]/vmax*100).toFixed(1)+'%"></span></span>'
   +'<span class="km">'+v[1]+' km</span></div>').join('')
 +'<div class="vsnote">Each figure is that system\u2019s own published route length, metro only \u2014 '
 +'<b>London</b> without the Elizabeth line or the Overground, <b>Tokyo</b> as Tokyo Metro and Toei '
 +'combined, <b>Delhi</b> as DMRC without the Aqua Line, Rapid Metro or Namo Bharat. New York runs far '
 +'more track than route within that length, and Tokyo carries more passengers.</div>';

$('src').innerHTML='<b>Sources.</b> Line geometry, station positions and running order: '
 +'© OpenStreetMap contributors, ODbL 1.0 — station order taken from the route relations’ ordered '
 +'stop lists, not inferred from distance. Corridors under construction: Delhi Metro Rail Corporation’s own '
 +'KML (influencezone.delhimetrorail.com). Network totals cross-checked against DMRC’s published network '
 +'table and Wikipedia’s line-by-line table, which agree to the station. Compiled August 2026 — '
 +'networks change, and this is a snapshot.';

const rows=LINES.map(l=>{
  const n=new Set([].concat(l.seq,l.branch||[])).size;
  return '<tr><td><i class="sw" style="background:'+l.c+'"></i>'+esc(l.nm)+'</td><td class="n">'+n+'</td>'
   +'<td style="color:var(--dim);font-size:11.5px">'+esc(l.own)+'</td></tr>';}).join('');
$('mtxt').innerHTML=
'<p><b>The map in the station is a diagram.</b> It spaces stations evenly, bends every line to 45 degrees and '
+'makes the outer reaches fit a poster. That is exactly right for finding your platform and useless for '
+'understanding the city. This is the same network drawn where it actually is, over Delhi’s own geography.</p>'

+'<p><b>How many stations there are, and why two numbers are both correct.</b> DMRC’s own network table '
+'counts <b>'+CT.dmrcSlots+'</b> — the sum of each line’s station list, so an interchange is counted '
+'once on every line that serves it. Count the physical buildings instead and you get <b>'+CT.dmrcStations
+'</b>, because '+CT.dmrcInterchanges+' of them are shared. Both figures appear in official material; this page '
+'uses '+CT.dmrcStations+' where it means places and '+CT.dmrcSlots+' where it means line-stations, and says '
+'which. Route length is <b>'+CT.dmrcKm+' km</b>. DMRC counts <b>'+CT.dmrcLines+' lines</b> against the '
+CT.dmrcCorridors+' colours drawn here, because the Blue Line’s Vaishali branch is separately numbered '
+'Line 4 — which is also why Yamuna Bank counts as an interchange.</p>'

+'<table><tr><th>Line</th><th style="text-align:right">Stations</th><th>Owner</th></tr>'+rows+'</table>'

+'<p><b>Namo Bharat is not a Delhi Metro line.</b> It is regional rail: a different operator (NCRTC), a '
+'different service, different fares, and its own stations even where one shares a name with a metro station. '
+'It is drawn here because a Delhi commuter can use it, and it is kept in its own group, its own colour, and '
+'out of every Delhi Metro total on this page. The Aqua Line in Noida is owned by NMRC and Rapid Metro '
+'Gurugram by HMRTC; DMRC runs the trains on both, but neither is Delhi Metro track and neither is counted as '
+'such here.</p>'

+'<p><b>Where the shapes come from.</b> Line geometry and station coordinates are OpenStreetMap’s, under '
+'the ODbL. The order of stations along each line, and which line each station belongs to, come from the '
+'ordered stop lists inside OSM’s route relations — not from measuring which track a station sits '
+'nearest, which is how an earlier draft of this map ended up putting Meerut on the Red Line.</p>'

+'<p><b>What is being built.</b> '+nFut+' stations across '+FUT.length+' corridors, from DMRC’s own '
+'published KML for Phase 4 and Phase 5. Those files give station coordinates and an <i>influence zone</i> '
+'— the corridor envelope DMRC publishes for land planning. The dashed outline is that envelope, not a '
+'track centreline: the alignment runs inside it. Sections that opened on 8 March 2026 have been moved out of '
+'this set and into the network proper.</p>'

+'<p><b>What this does not do.</b> No live train positions and no timetable. Delhi Metro publishes no realtime '
+'feed, and the only bulk source of inter-station timings is a static GTFS export last refreshed in August '
+'2023 — older than three of the corridors on this map. The journey estimate in the planner is arithmetic '
+'on stops and changes, and is labelled as such wherever it appears. Rather than dress an out-of-date '
+'timetable as current, this tool gives you the network: where the lines go, where they meet, and how to get '
+'across.</p>'

+'<p style="font-size:11px;color:var(--dim)">Metro and base geography: © OpenStreetMap contributors, ODbL '
+'1.0. Phase 4 and Phase 5 alignments: Delhi Metro Rail Corporation, influencezone.delhimetrorail.com. Counts '
+'cross-checked against DMRC’s network table and Wikipedia’s line table, August 2026.</p>';

$('zkey').textContent = /Mac|iPhone|iPad/.test(navigator.platform||'') ? '\u2318' : 'Ctrl';

/* ================= the derived numbers ================= */
/* Everything in this slab is either DMRC's own published figure or arithmetic on
   this page's own data, and the note says which is which. Nothing is modelled.
   The one number a reader would expect and will not find is an average wait: DMRC
   publishes headway section by section and no network average, so none is invented. */
const NX=[
  ['7.3','km<sup>2</sup>','Of Delhi Per Station'],
  ['2 <i>min</i> 18 <i>sec</i>','','Between One Train And The Next, Busiest Stretch'],
  ['4,508','','Train Trips A Day'],
  ['14','%','Of Station Pairs Need No Change At All'],
  ['5','','The Most Changes You Will Ever Need'],
  ['550','m','The Shortest Gap Between Two Stations']
];
$('nxgrid').innerHTML=NX.map(x=>'<div class="nxc"><b>'+x[0]+(x[1]?' <i>'+x[1]+'</i>':'')
  +'</b><span>'+x[2]+'</span></div>').join('');
$('nxnote').innerHTML=
  '<b>The 83%, and how it is worked out.</b> Take every metro station on this map except Namo Bharat '
 +'&mdash; the '+CT.dmrcStations+' Delhi Metro stations plus the Aqua Line and Rapid Metro Gurugram, both of '
 +'which DMRC runs the trains on, minus Sikanderpur which is already counted. That is <b>276</b> stations, '
 +'so 276 &times; 275 &divide; 2 = <b>37,950</b> pairs of them &mdash; pairs, not permutations, because a '
 +'trip from A to B is the same trip as B to A. Every pair went through the planner on this page and the '
 +'changes were counted: <b>13.6% need none at all</b>, 41.5% need one, 27.5% need two, 12.4% need three, '
 +'4.2% need four and 300 pairs need five, the worst being Alpha 1 in Greater Noida to Shivaji Stadium. '
 +'That is <b>82.7% within two changes</b>. On the Delhi Metro alone it is 94.3%; the Aqua Line hangs off '
 +'the far end of Greater Noida, so bringing it in pulls the figure down by eleven points, which is itself '
 +'worth knowing.'
 +'<span class="warn"><b>What that 83% does not say.</b> It counts <i>station pairs</i>, weighting Dhansa '
 +'Bus Stand to Shiv Vihar exactly the same as Rajiv Chowk to Kashmere Gate. It describes the shape of the '
 +'network, not the journeys people actually make &mdash; those pile onto a few corridors, and DMRC '
 +'publishes no origin-and-destination data to weight it with. Read it as: the network is built so that '
 +'almost nowhere is more than two changes from anywhere. Not as: 83% of passengers change twice or less. '
 +'Re-running it with the change penalty set anywhere from 2 to 8 km-equivalents moves the answer only a '
 +'few points, so it is a fact about the network rather than about the setting.</span>'
 +'<span class="warn"><b>Two minutes eighteen seconds is the gap between trains.</b> On DMRC\u2019s busiest '
 +'stretch \u2014 the Yellow Line through the middle of the city \u2014 one train follows the last that '
 +'closely at peak. When the metro opened in 2002 the gap was seven minutes. It is not an average wait and '
 +'not a network figure: DMRC publishes headway <i>section by section</i>, from 2 min 18 sec on that stretch '
 +'to 10 minutes on the Airport Express and 12 on the Grey Line, and no network-wide average at all. Any '
 +'single figure would have to be weighted by how many people ride each section, which DMRC does not '
 +'publish either, so there is no average wait on this page.</span>'
 +'<span class="warn"><b>Where each number comes from.</b> The 1.43 km gap, the 70.2 km ride, the change '
 +'counts and the 7.3 km&sup2; are arithmetic on this page&rsquo;s own data. The last of those uses the '
 +'<b>202 of 276 stations</b> that fall inside the National Capital Territory, which is 1,483 km&sup2;; the '
 +'rest are in Gurugram, Noida, Greater Noida, Faridabad, Ghaziabad and Bahadurgarh. As a check, the area of '
 +'the Delhi boundary drawn on this map works out at 1,477 km&sup2;, within half a percent of the published '
 +'figure. The <b>2 min 18 sec</b> and the <b>4,508 train trips a day</b> are DMRC\u2019s own, from its '
 +'statements of August 2026 and 15 March 2026 &mdash; both press releases, not the Annual Report, which '
 +'carries no operating figures at all.</span>';

/* ================= ridership ================= */
/* Every figure here is DMRC's own, and every one of them counts a journey once per
   LINE, not once per passenger. DMRC changed to that basis in 2019; it inflated the
   published number by roughly half. The band says so rather than quietly banking it. */
const FF=[
  {y:'2018-19', v:4.544, src:'MoHUA'},
  {y:'2019-20', v:5.065, src:'MoHUA'},
  {y:'2020-21', v:1.710, src:'MoHUA', covid:true},
  {y:'2021-22', v:2.477, src:'MoHUA', covid:true},
  {y:'2022-23', v:4.63,  src:'DMRC Annual Report 2023-24'},
  {y:'2023-24', v:5.83,  src:'DMRC Annual Report 2023-24'},
  {y:'2024-25', v:6.31,  src:'DMRC Annual Report 2024-25'}
];
(function(){
  const max=Math.max(...FF.map(d=>d.v));
  $('ffbars').innerHTML=FF.map(d=>
    '<div class="ffb'+(d.covid?' covid':'')+'">'
    +'<div class="v">'+d.v.toFixed(2)+'</div>'
    +'<div class="bar" style="height:'+(d.v/max*100).toFixed(1)+'%"></div>'
    +'<div class="y">'+d.y+'</div></div>').join('');
  /* DMRC publishes no station-wise bulletin, so this is reported data, labelled as such. */
  const ST=[['Botanical Garden','Blue Line \u00b7 Magenta Line','2.7 lakh'],
            ['Kashmere Gate','Red \u00b7 Yellow \u00b7 Violet','2.6 lakh'],
            ['Rajiv Chowk','Blue Line \u00b7 Yellow Line','2.1 lakh']];
  $('ffstations').innerHTML=ST.map((s,i)=>
    '<div class="ffs"><span class="rk">'+(i+1)+'</span>'
    +'<span class="nm">'+esc(s[0])+'<small>'+s[1]+'</small></span>'
    +'<span class="fg">'+s[2]+'</span></div>').join('');
  $('ffnote').innerHTML=
    'Millions of journeys a day. <b>2020-21 and 2021-22 are dashed</b> because the pandemic closed the '
   +'network for months, and the government averaged those two years over operating days rather than over '
   +'the full year \u2014 they are not comparable to the bars either side of them, so they are not drawn '
   +'as though they were.'
   +'<span class="warn"><b>One number, counted DMRC\u2019s way.</b> DMRC counts a journey once for every '
   +'<i>line</i> you use, not once for every passenger. Ride Rithala to Botanical Garden and you change '
   +'twice, so you are three journeys, not one. DMRC moved to this basis in 2019 and it lifted the '
   +'published figure by roughly half overnight; it has not published a one-passenger-one-journey number '
   +'since. Every figure on this page is on DMRC\u2019s basis, which is why none of them is set against '
   +'London, New York or Tokyo \u2014 those three count differently, and the comparison would flatter '
   +'Delhi for no good reason.</span>'
   +'<span class="warn"><b>On the station figures.</b> DMRC publishes no station-wise footfall bulletin. '
   +'These three are DMRC data reported by <i>The Times of India</i> in July 2026, rounded to the nearest '
   +'ten thousand, and the reporting does not say whether a \u201cfootfall\u201d is an entry, an exit or '
   +'both. They are here because the ranking itself is news \u2014 Botanical Garden has been ahead of '
   +'Rajiv Chowk every month since March 2026 \u2014 but they are somebody else\u2019s count, not DMRC\u2019s '
   +'own publication, and they are the softest numbers on this page.</span>';
})();

/* ================= boot ================= */
/* the theme is already set before first paint by the bootstrap in <head> */
if(innerWidth<=1000) openDrawer(false);
addEventListener('resize',()=>{ resize(); if(!ROUTE&&!anySel()) fit(); });
resize(); markTheme(); fit(); renderMenu(); renderStrip(); renderRoute();
(function frame(){ if(anim) anim(); draw(); requestAnimationFrame(frame); })();

