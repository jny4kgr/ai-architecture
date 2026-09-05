import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "../tmp/pdfs/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const ROOT = "/Users/Jun/Documents/AI Architecture";
const SRC = `${ROOT}/output/client_presentation`;
const OUT = `${ROOT}/Sales Presentation Materials`;
const FONT = "Arial Unicode MS";
const C = { bg:"#1B1B19", panel:"#272724", panel2:"#31302C", bone:"#EEEAE2", taupe:"#A98F73", mute:"#A9A59E", white:"#FFFFFF", ink:"#181816", pale:"#E5E0D7", moss:"#77796D" };

async function bytes(path){const b=await fs.readFile(path);return b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);}
async function writeBlob(path,blob){await fs.writeFile(path,new Uint8Array(await blob.arrayBuffer()));}
function rect(s,x,y,w,h,fill,line="none",lw=0){return s.shapes.add({geometry:"rect",position:{left:x,top:y,width:w,height:h},fill,line:{style:"solid",fill:line,width:lw}});}
function circle(s,x,y,d,fill,line="none",lw=0){return s.shapes.add({geometry:"ellipse",position:{left:x,top:y,width:d,height:d},fill,line:{style:"solid",fill:line,width:lw}});}
function tb(s,text,x,y,w,h,size=22,o={}){const z=s.shapes.add({geometry:"textbox",position:{left:x,top:y,width:w,height:h},fill:"none",line:{style:"solid",fill:"none",width:0}});z.text=text;z.text.style={fontSize:size,typeface:FONT,color:o.color||C.bone,bold:!!o.bold,alignment:o.align||"left",verticalAlignment:o.valign||"top"};return z;}
function rule(s,x,y,w,fill=C.taupe,h=2){return rect(s,x,y,w,h,fill);}
function footer(s,n,label="ASAKA HAMAZAKI 3-CHOME / 2"){tb(s,label,44,678,500,18,11,{color:C.mute});tb(s,String(n).padStart(2,"0"),1185,676,50,18,11,{color:C.mute,align:"right"});}
function head(s,kicker,title,n){tb(s,kicker.toUpperCase(),44,34,680,22,13,{bold:true,color:C.taupe});tb(s,title,44,66,1120,52,34,{bold:true});rule(s,44,126,1192,C.panel2,1);footer(s,n);}
async function img(s,path,pos,fit="cover",crop=undefined,alt=""){return s.images.add({blob:await bytes(path),contentType:path.endsWith(".jpg")?"image/jpeg":"image/png",alt,fit,position:pos,...(crop?{crop}:{})});}
function connector(s,x1,y1,x2,y2){const dx=x2-x1,dy=y2-y1;const len=Math.sqrt(dx*dx+dy*dy),ang=Math.atan2(dy,dx)*180/Math.PI;const r=rect(s,x1,y1,len,2,C.taupe);r.rotation=ang;}
function callout(s,num,title,body,x,y,w=310){tb(s,`0${num}  ${title}`,x,y-2,w,28,20,{bold:true});tb(s,body,x,y+31,w,58,15,{color:C.mute});}

const p=Presentation.create({slideSize:{width:1280,height:720}});

// 1 cover
{
 const s=p.slides.add();s.background.fill=C.bg;
 await img(s,`${OUT}/assets/exterior_hero_v2.png`,{left:515,top:0,width:765,height:720},"cover",{left:0.03,top:0,right:0.02,bottom:0},"外観完成イメージ");
 rect(s,0,0,620,720,C.bg); rect(s,515,0,190,720,{color:C.bg,transparency:35});
 tb(s,"PRIVATE RESIDENCE",44,44,420,24,14,{bold:true,color:C.taupe});
 tb(s,"朝霞市浜崎三丁目\n二号棟",44,188,500,142,52,{bold:true});
 tb(s,"都市の利便と、静かな家時間。\n三層に整えた、端正な住まい。",44,390,445,78,23,{color:C.pale});
 rule(s,44,515,400,C.taupe,2);tb(s,"NEW HOME PRESENTATION  /  2026",44,540,420,24,13,{color:C.mute});
 tb(s,"完成イメージ",1060,680,170,18,11,{color:C.white,align:"right"});
}

// 2 highlights
{
 const s=p.slides.add();s.background.fill=C.bg;head(s,"three values","この家の魅力、3点",2);
 const data=[
  ["01","17帖の2階LDK","視線の抜けと採光を得やすい2階に、料理・食事・団らんをひとつに集約。"],
  ["02","収納を受け止める1階","6帖納戸、玄関収納、階段下収納。外で使う物も、日用品も整理しやすく。"],
  ["03","三層を使い分ける","1階は帰宅、2階は家族、3階は休息。生活の場面が自然に切り替わります。"]];
 for(let i=0;i<3;i++){const x=44+i*402;tb(s,data[i][0],x,180,80,42,32,{bold:true,color:C.taupe});rule(s,x,240,340,C.panel2,2);tb(s,data[i][1],x,275,340,58,27,{bold:true});tb(s,data[i][2],x,357,340,115,17,{color:C.mute});}
 tb(s,"BUILT-IN GARAGE  /  3 STOREYS  /  2F FAMILY LIVING",44,604,900,25,14,{bold:true,color:C.taupe});
}

// 3 exterior
{
 const s=p.slides.add();s.background.fill=C.bg;await img(s,`${OUT}/assets/exterior_hero_v2.png`,{left:0,top:0,width:850,height:720},"cover",undefined,"外観完成イメージ");rect(s,760,0,520,720,C.bg);
 tb(s,"EXTERIOR",910,52,250,24,14,{bold:true,color:C.taupe});tb(s,"陰影で魅せる、\nグレーの立面。",910,132,320,112,38,{bold:true});
 tb(s,"リープMGグレーを軸に、白と木目を控えめに重ねた外装。ブラックのサッシと屋根が輪郭を整えます。",910,292,300,110,18,{color:C.mute});
 rule(s,910,440,270,C.taupe);tb(s,"MAIN",910,468,70,20,12,{color:C.taupe});tb(s,"リープMGグレー",995,464,220,27,18,{bold:true});tb(s,"ACCENT",910,518,70,20,12,{color:C.taupe});tb(s,"ヴィンテージウッド",995,514,220,27,18,{bold:true});
 tb(s,"※図面・仕様を基に作成した完成イメージ",910,650,290,18,11,{color:C.mute});footer(s,3);
}

// 4 LDK
{
 const s=p.slides.add();s.background.fill=C.bg;await img(s,`${OUT}/assets/ldk_hero_v2.png`,{left:430,top:0,width:850,height:720},"cover",undefined,"LDK完成イメージ");rect(s,0,0,510,720,C.bg);rect(s,430,0,150,720,{color:C.bg,transparency:28});
 tb(s,"SECOND FLOOR",44,50,300,22,13,{bold:true,color:C.taupe});tb(s,"17帖。\n家族の時間を\n明るくつなぐ。",44,132,420,190,42,{bold:true});
 tb(s,"フラット対面キッチンを中心に、リビング・ダイニングと水まわりを同じ階へ。家事の移動を短く整えます。",44,378,350,110,18,{color:C.mute});
 tb(s,"17.0 J",44,560,180,45,34,{bold:true,color:C.taupe});tb(s,"LIVING / DINING / KITCHEN",44,610,300,22,12,{color:C.mute});footer(s,4);
}

// 5 annotated 1F
{
 const s=p.slides.add();s.background.fill=C.bg;head(s,"floor plan 01","1階｜収納と帰宅動線",5);
 await img(s,`${SRC}/pdf_pages/page-03.jpg`,{left:44,top:155,width:710,height:485},"contain",undefined,"1階平面図");
 circle(s,600,325,30,C.taupe);tb(s,"1",600,330,30,18,13,{bold:true,color:C.ink,align:"center"});
 circle(s,530,440,30,C.taupe);tb(s,"2",530,445,30,18,13,{bold:true,color:C.ink,align:"center"});
 circle(s,285,465,30,C.taupe);tb(s,"3",285,470,30,18,13,{bold:true,color:C.ink,align:"center"});
 callout(s,1,"6帖納戸","季節物や趣味用品まで受け止める、独立した収納空間。",830,170,360);
 callout(s,2,"帰宅動線","ガレージから玄関、収納、階段へ。持ち物を整理して上階へ。",830,325,360);
 callout(s,3,"階段下収納","日用品や掃除道具の定位置を確保。生活空間へ物を持ち込みにくく。",830,480,360);
}

// 6 annotated 2F
{
 const s=p.slides.add();s.background.fill=C.bg;head(s,"floor plan 02","2階｜採光と家事動線",6);
 await img(s,`${SRC}/pdf_pages/page-04.jpg`,{left:44,top:155,width:710,height:485},"contain",undefined,"2階平面図");
 circle(s,285,250,30,C.taupe);tb(s,"1",285,255,30,18,13,{bold:true,color:C.ink,align:"center"});
 circle(s,520,377,30,C.taupe);tb(s,"2",520,382,30,18,13,{bold:true,color:C.ink,align:"center"});
 circle(s,625,240,30,C.taupe);tb(s,"3",625,245,30,18,13,{bold:true,color:C.ink,align:"center"});
 callout(s,1,"採光の中心","バルコニー側の開口からLDKへ光を取り込む計画。",830,170,360);
 callout(s,2,"家事を一層で完結","キッチン、洗面、浴室を同じ階にまとめ、上下移動を抑制。",830,325,360);
 callout(s,3,"フラット対面","料理中もリビング・ダイニングを見渡しやすい配置。",830,480,360);
}

// 7 annotated 3F
{
 const s=p.slides.add();s.background.fill=C.bg;head(s,"floor plan 03","3階｜個室・収納・光",7);
 await img(s,`${SRC}/pdf_pages/page-05.jpg`,{left:44,top:155,width:710,height:485},"contain",undefined,"3階平面図");
 circle(s,250,330,30,C.taupe);tb(s,"1",250,335,30,18,13,{bold:true,color:C.ink,align:"center"});
 circle(s,520,255,30,C.taupe);tb(s,"2",520,260,30,18,13,{bold:true,color:C.ink,align:"center"});
 circle(s,610,420,30,C.taupe);tb(s,"3",610,425,30,18,13,{bold:true,color:C.ink,align:"center"});
 callout(s,1,"3つの個室","6帖・5帖・4.5帖。家族それぞれの時間を確保。",830,170,360);
 callout(s,2,"各室収納","居室ごとに収納を設け、床面をすっきり使いやすく。",830,325,360);
 callout(s,3,"2面バルコニー","外への抜けを複数方向に設け、採光と通風に配慮。",830,480,360);
}

// 8 kitchen and bath
{
 const s=p.slides.add();s.background.fill=C.bg;head(s,"equipment 01","キッチンと浴室を、写真で確かめる",8);
 await img(s,`${OUT}/assets/manufacturers/cleanup_flat_kitchen.jpg`,{left:44,top:162,width:570,height:330},"contain",undefined,"クリナップ公式フラット対面参考画像");
 await img(s,`${OUT}/assets/manufacturers/toto_sazana.jpg`,{left:666,top:162,width:570,height:330},"cover",undefined,"TOTOサザナ公式画像");
 tb(s,"KITCHEN",44,520,130,20,12,{bold:true,color:C.taupe});tb(s,"クリナップ KT｜フラット対面",44,548,540,30,22,{bold:true});tb(s,"ダークウッド扉 × ライトグレー天板（仕様書記載）",44,586,540,28,15,{color:C.mute});
 tb(s,"BATHROOM",666,520,150,20,12,{bold:true,color:C.taupe});tb(s,"TOTO サザナ｜1616",666,548,540,30,22,{bold:true});tb(s,"浴室換気暖房乾燥機・追焚き・ランドリーパイプ",666,586,540,28,15,{color:C.mute});
 tb(s,"※キッチン画像はクリナップ公式のフラット対面レイアウト参考。実際の商品・色柄は仕様書および現物サンプルを優先します。",44,642,1160,24,11,{color:C.mute});
}

// 9 washroom and entrance
{
 const s=p.slides.add();s.background.fill=C.bg;head(s,"equipment 02","毎日の所作を整える、洗面と玄関",9);
 await img(s,`${OUT}/assets/manufacturers/toto_octave_lite.jpg`,{left:44,top:162,width:570,height:330},"cover",undefined,"TOTOオクターブLite公式画像");
 await img(s,`${OUT}/assets/manufacturers/lixil_giesta2.jpg`,{left:666,top:162,width:570,height:330},"cover",undefined,"LIXILジエスタ2公式画像");
 tb(s,"WASHROOM",44,520,140,20,12,{bold:true,color:C.taupe});tb(s,"TOTO オクターブLite",44,548,540,30,22,{bold:true});tb(s,"三面鏡収納・お掃除ラクラク水栓・LED照明",44,586,540,28,15,{color:C.mute});
 tb(s,"ENTRANCE",666,520,130,20,12,{bold:true,color:C.taupe});tb(s,"LIXIL ジエスタ2",666,548,540,30,22,{bold:true});tb(s,"断熱玄関ドア・電池錠・シリンダー一体型ハンドル",666,586,540,28,15,{color:C.mute});
 tb(s,"※掲載写真はメーカー公式の代表イメージ。実際の品番・色・仕様は仕様書を優先します。",44,642,1160,24,11,{color:C.mute});
}

// 10 location
{
 const s=p.slides.add();s.background.fill=C.bg;head(s,"location","2駅2路線と、日常の施設が身近に",10);
 const cols=[
  ["交通","朝霞台駅｜東武東上線\n北朝霞駅｜JR武蔵野線","徒歩分数は販売資料で要確認"],
  ["買い物","スーパーみらべる 北朝霞店\n浜崎エリアの生活利便施設","各施設までの距離は要確認"],
  ["学校","朝霞第七小学校\n朝霞第二中学校","朝霞市公式の通学区域に基づく"]];
 for(let i=0;i<3;i++){const x=44+i*402;rect(s,x,175,360,370,i===1?C.panel2:C.panel);tb(s,cols[i][0],x+28,202,300,26,15,{bold:true,color:C.taupe});rule(s,x+28,248,304,C.taupe,1);tb(s,cols[i][1],x+28,290,304,110,23,{bold:true});tb(s,cols[i][2],x+28,455,304,48,13,{color:C.mute});}
 tb(s,"所在地｜埼玉県朝霞市浜崎3丁目17-56",44,585,800,28,20,{bold:true});tb(s,"※所要時間・距離・営業状況は現地および最新情報をご確認ください。",44,630,900,22,12,{color:C.mute});
}

// 11 overview
{
 const s=p.slides.add();s.background.fill=C.bg;head(s,"property facts","物件概要を、1ページに",11);
 const facts=[
  ["販売価格","要確認"],["敷地面積","82.64 ㎡"],["延べ床面積","120.47 ㎡"],["容積率対象","99.36 ㎡"],
  ["構造・階数","木造・地上3階建て"],["間取り","3LDK相当＋6帖納戸＋車庫"],["駐車","ビルトインガレージ"],["完成予定","要確認"]];
 for(let i=0;i<8;i++){const col=i%2,row=Math.floor(i/2),x=44+col*602,y=164+row*108;tb(s,facts[i][0],x,y,175,24,13,{bold:true,color:C.taupe});tb(s,facts[i][1],x+182,y-4,390,34,25,{bold:true});rule(s,x,y+58,560,C.panel2,1);}
 tb(s,"所在地｜埼玉県朝霞市浜崎3丁目17-56　　図面基準日｜2026年7月9日",44,604,1130,24,14,{color:C.mute});
 tb(s,"※面積は配置図記載値。延べ床面積には車庫部分を含みます。価格・完成予定は販売担当者へご確認ください。",44,637,1130,24,11,{color:C.mute});
}

// 12 contact and guide
{
 const s=p.slides.add();s.background.fill=C.bg;head(s,"information","お問い合わせ・現地ご案内",12);
 tb(s,"現地案内図（概略）",44,160,450,30,22,{bold:true});rect(s,44,210,690,390,C.panel);
 // schematic map
 rule(s,94,390,590,C.moss,14);rule(s,390,245,14,C.moss,315);circle(s,152,345,18,C.taupe);circle(s,228,425,18,C.taupe);circle(s,448,310,18,C.taupe);circle(s,575,455,30,C.taupe);
 tb(s,"朝霞台駅\n東武東上線",105,285,130,48,15,{bold:true});tb(s,"北朝霞駅\nJR武蔵野線",175,455,150,48,15,{bold:true});tb(s,"朝霞第七小",420,258,150,24,15,{bold:true});tb(s,"現地\n浜崎3丁目17-56",530,500,170,48,16,{bold:true});tb(s,"スーパーみらべる\n北朝霞店",435,430,150,48,14,{color:C.mute});
 tb(s,"※位置関係を示す概略図です。正確な経路は地図アプリ等でご確認ください。",44,615,690,24,11,{color:C.mute});
 tb(s,"CONTACT",810,165,250,22,13,{bold:true,color:C.taupe});tb(s,"販売窓口",810,220,160,24,15,{color:C.mute});tb(s,"要確認",810,250,360,42,31,{bold:true});rule(s,810,315,390,C.panel2,1);
 tb(s,"TEL",810,350,100,24,15,{color:C.mute});tb(s,"要確認",940,346,260,32,23,{bold:true});tb(s,"担当",810,410,100,24,15,{color:C.mute});tb(s,"要確認",940,406,260,32,23,{bold:true});
 tb(s,"ご内覧・資金計画・仕様確認など、\nお気軽に販売担当者へお申し付けください。",810,500,390,72,20,{bold:true});
 tb(s,"本資料は図面・仕様書を基に作成した提案資料です。図面と現況が異なる場合は現況を優先します。",810,614,390,38,11,{color:C.mute});
}

await fs.mkdir(`${OUT}/qa`,{recursive:true});
for(const [i,s] of p.slides.items.entries()){await writeBlob(`${OUT}/qa/slide-${String(i+1).padStart(2,"0")}.png`,await p.export({slide:s,format:"png",scale:1}));await fs.writeFile(`${OUT}/qa/slide-${String(i+1).padStart(2,"0")}.layout.json`,await(await s.export({format:"layout"})).text());}
await writeBlob(`${OUT}/qa/montage.webp`,await p.export({format:"webp",montage:true,scale:1}));
const pptx=await PresentationFile.exportPptx(p);await pptx.save(`${OUT}/朝霞市浜崎3丁目_2号棟_邸宅提案資料_シック版.pptx`);
console.log(await p.inspect({kind:"slide,textbox,image",maxChars:8000}).then(x=>x.ndjson));
