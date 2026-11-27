from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"product-cards"/"originals"/"tenzor"
OUT=ROOT/"product-cards"/"infographic"
OUT.mkdir(parents=True,exist_ok=True)
W,H=1500,2000
O=(255,104,24); K=(22,23,25); C=(249,245,237); WH=(255,255,255); L=(218,244,76); G=(105,105,105)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def F(n,b=True):return ImageFont.truetype(B if b else R,n)
def cv(c=C):return Image.new("RGB",(W,H),c)
def tx(d,xy,s,n=40,c=K,b=True,sp=4):d.multiline_text(xy,s,font=F(n,b),fill=c,spacing=sp)
def rr(d,xy,r,c):d.rounded_rectangle(xy,radius=r,fill=c)
def cover(im,src,box):
    if src is None:return
    x,y,w,h=box;q=ImageOps.fit(src.convert("RGB"),(w,h),method=Image.Resampling.LANCZOS);im.paste(q,(x,y))
def fit(im,src,box):
    if src is None:return
    x,y,w,h=box;q=ImageOps.contain(src.convert("RGB"),(w,h),method=Image.Resampling.LANCZOS);im.paste(q,(x+(w-q.width)//2,y+(h-q.height)//2))
def pill(d,xy,s,bg=O,fg=WH,n=21):
    rr(d,xy,22,bg);d.text((xy[0]+20,xy[1]+12),s,font=F(n),fill=fg)
def prod(im,hero,box,ang=0):
    x,y,w,h=box;q=ImageOps.contain(hero,(w,h),method=Image.Resampling.LANCZOS)
    if ang:q=q.rotate(ang,expand=True,resample=Image.Resampling.BICUBIC)
    im.paste(q,(x+(w-q.width)//2,y+(h-q.height)//2))
def foot(d,n,dark=False):
    col=(210,210,210) if dark else G
    d.text((76,1915),"ПРЕСС ДЛЯ МЯГКИХ УПАКОВОК",font=F(19),fill=col)
    d.text((1360,1910),f"{n:02d}/08",font=F(22),fill=O)
def pouch(d,x,y,w=230,h=420):
    d.polygon([(x+20,y),(x+w-20,y),(x+w-5,y+h-25),(x+w//2,y+h),(x+5,y+h-25)],fill=(242,235,222),outline=(165,151,133),width=4)
    d.line((x+25,y+38,x+w-25,y+38),fill=(165,151,133),width=5)
    rr(d,(x+30,y+100,x+w-30,y+240),16,WH)
    d.text((x+55,y+145),"КОРМ",font=F(25),fill=O)
def save(im,n):im.save(OUT/f"{n:02d}.jpg",quality=96,optimize=True)
arr=[]
for p in sorted(SRC.glob("*")):
    if p.suffix.lower() in (".png",".jpg",".jpeg",".webp"):
        try:arr.append(Image.open(p).convert("RGB"))
        except:pass
if not arr:raise SystemExit("No product images")
hero=arr[0]
def fetch(url,name):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=25) as r:Path("/tmp/"+name).write_bytes(r.read())
        return Image.open("/tmp/"+name).convert("RGB")
    except Exception as e:print("Photo unavailable",name,e);return None
cat1=fetch("https://images.pexels.com/photos/13317322/pexels-photo-13317322.jpeg","catA.jpg")
cat2=fetch("https://images.pexels.com/photos/5822458/pexels-photo-5822458.jpeg","catB.jpg")
(OUT/"sources.txt").write_text(
"Изделие: исходные фото заказчика из product-cards/originals/tenzor/.\n"
"Кошка 1: Claudia Schmalz, Pexels 13317322: https://www.pexels.com/photo/close-up-shot-of-a-cat-eating-13317322/\n"
"Кошка 2: Romina BM, Pexels 5822458: https://www.pexels.com/photo/close-up-shot-of-a-cat-5822458/\n"
"Лицензия Pexels: https://www.pexels.com/license/ . Фото кошек — лайфстайл-контекст, не документальная демонстрация работы изделия.\n"
"Пакетик на слайде 5 нарисован схематично. Размеры взяты из исходного изображения заказчика.\n",encoding="utf-8")

# 01 / campaign key visual
im=cv(K);d=ImageDraw.Draw(im);d.rectangle((0,0,1500,26),fill=O);d.ellipse((970,190,1660,880),fill=O)
pill(d,(80,80,480,145),"УМНЫЙ ПОМОЩНИК ДЛЯ ДОМА",L, K,19)
tx(d,(75,235),"НИ КАПЛИ\nМИМО.",132,WH,True,0)
d.text((86,565),"АККУРАТНО ИЗВЛЕКАЙТЕ СОДЕРЖИМОЕ",font=F(24),fill=(220,220,220))
rr(d,(70,690,1430,1430),52,C);prod(im,hero,(110,760,1280,590),-5)
pill(d,(95,1510,580,1580),"ДЛЯ МЯГКИХ УПАКОВОК")
tx(d,(90,1660),"МАЛЕНЬКАЯ ВЕЩЬ.\nЗАМЕТНО БОЛЬШЕ УДОБСТВА.",43,WH,True,5)
foot(d,1,True);save(im,1)

# 02 / pet lifestyle, full-bleed emotional photo, product clearly isolated
im=cv(K);d=ImageDraw.Draw(im)
if cat1:cover(im,cat1,(0,0,1500,1100))
d.rectangle((0,1060,1500,2000),fill=K);d.polygon([(0,0),(140,0),(0,360)],fill=O)
pill(d,(75,1140,420,1205),"ДЛЯ ПИТОМЦА",L,K,22)
tx(d,(75,1290),"СЧАСТЛИВЫЙ\nМУР — ЛУЧШАЯ\nНАГРАДА.",63,WH,True,0)
rr(d,(850,1190,1420,1760),38,C);prod(im,hero,(885,1240,500,370),-4)
d.text((890,1660),"ПРЕСС ДЛЯ МЯГКИХ ПАКЕТИКОВ",font=F(19),fill=K)
d.text((78,1790),"Лайфстайл-фото; изделие показано отдельно.",font=F(18,False),fill=(195,195,195))
foot(d,2,True);save(im,2)

# 03 / asymmetric second cat creative
im=cv(O);d=ImageDraw.Draw(im)
if cat2:cover(im,cat2,(660,0,840,1200))
d.polygon([(0,0),(790,0),(650,1200),(0,1400)],fill=K)
pill(d,(75,90,430,155),"ВЛАЖНЫЙ КОРМ",L,K,22)
tx(d,(75,270),"ПОРЦИЯ\nС ЛЮБОВЬЮ.",82,WH,True,0)
tx(d,(82,525),"Помощник для мягких\nпакетиков с кормом",29,(220,220,220),False,8)
rr(d,(70,810,610,1190),35,C);prod(im,hero,(105,845,470,300),-3)
d.text((85,1245),"РЕАЛЬНОЕ ИЗДЕЛИЕ",font=F(21),fill=K)
tx(d,(78,1360),"МЕНЬШЕ\nОСТАТКОВ.\nБОЛЬШЕ\nУДОБСТВА.",59,K,True,0)
d.text((78,1790),"Фото кошки — эмоциональный контекст, не демонстрация использования.",font=F(16),fill=K)
foot(d,3);save(im,3)

# 04 / use-case editorial menu
im=cv(C);d=ImageDraw.Draw(im);d.rectangle((0,0,1500,24),fill=O)
pill(d,(78,75,470,140),"ОДИН ПРЕСС — РАЗНЫЕ ЗАДАЧИ")
tx(d,(75,220),"ЧТО МОЖНО\nВЫДАВИТЬ?",88,K,True,0)
rows=[("01","ВЛАЖНЫЙ КОРМ","мягкие пакетики"),("02","ЗУБНАЯ ПАСТА","подходящие тюбики"),("03","СОУСЫ","майонез • кетчуп")]
for i,(num,title,sub) in enumerate(rows):
    y=635+i*300;d.line((80,y,1420,y),fill=(205,198,188),width=3)
    d.text((88,y+38),num,font=F(34),fill=O);d.text((245,y+25),title,font=F(48),fill=K)
    d.text((250,y+100),sub,font=F(26,False),fill=G);d.text((1300,y+25),"+",font=F(58),fill=O)
rr(d,(80,1570,1420,1810),35,K);prod(im,hero,(115,1590,500,195))
tx(d,(700,1635),"КОМПАКТНЫЙ\nПОМОЩНИК НА КАЖДЫЙ ДЕНЬ",31,WH,True,4)
foot(d,4);save(im,4)

# 05 / graphic still-life explainer
im=cv((241,236,225));d=ImageDraw.Draw(im)
pill(d,(78,75,420,140),"ПРОСТОЙ ПРИНЦИП")
tx(d,(75,220),"УПАКОВКА.\nПРЕСС. ГОТОВО.",76,K,True,0)
rr(d,(70,640,1430,1540),48,WH);pouch(d,190,810,260,470)
d.text((180,1330),"МЯГКИЙ ПАКЕТИК",font=F(22),fill=K)
d.text((535,980),"+",font=F(100),fill=O);prod(im,hero,(730,790,590,440),-7)
d.text((810,1270),"ПРЕСС ДЛЯ УПАКОВОК",font=F(22),fill=K)
d.line((510,1450,1000,1450),fill=O,width=8);d.polygon([(1000,1450),(955,1425),(955,1475)],fill=O)
tx(d,(80,1640),"Схема предметов, не пошаговая инструкция.",24,G,False,6)
foot(d,5);save(im,5)

# 06 / macro detail grid
im=cv(K);d=ImageDraw.Draw(im)
pill(d,(78,75,390,140),"РАССМОТРИМ БЛИЖЕ",L,K,21)
tx(d,(75,220),"ФОРМА,\nКОТОРАЯ РАБОТАЕТ.",72,WH,True,0)
rr(d,(70,560,1430,1120),38,C);fit(im,hero,(100,585,1300,510))
rgb=hero
for i,(label,crop) in enumerate([("ПРОДОЛЬНЫЙ ПАЗ",rgb.crop((330,125,1270,330))),("ОТВЕРСТИЯ И КРАЯ",rgb.crop((1120,35,1530,420)))]):
    x=75+i*690;rr(d,(x,1200,x+650,1660),30,(47,49,51));fit(im,crop,(x+25,1230,600,310))
    d.text((x+28,1580),label,font=F(22),fill=L)
foot(d,6,True);save(im,6)

# 07 / precise dimensions poster
im=cv(C);d=ImageDraw.Draw(im)
pill(d,(78,75,410,140),"ТОЧНЫЕ ГАБАРИТЫ")
tx(d,(75,215),"МИНИ-ФОРМАТ.\nЛЁГКИЙ ВЕС.",78,K,True,0)
rr(d,(75,540,1425,1100),42,WH);prod(im,hero,(130,570,1240,500))
d.line((160,1145,1340,1145),fill=O,width=6);d.polygon([(160,1145),(190,1128),(190,1162)],fill=O);d.polygon([(1340,1145),(1310,1128),(1310,1162)],fill=O)
d.text((610,1165),"14,5 СМ",font=F(33),fill=O)
for i,(v,lbl) in enumerate([("3 см","ВЫСОТА"),("6 мм","ТОЛЩИНА"),("13 г","ВЕС"),("9,5 × 2 мм","ВЫРЕЗ")]):
    x=80+(i%2)*690;y=1300+(i//2)*245;rr(d,(x,y,x+650,y+190),26,K)
    d.text((x+28,y+25),v,font=F(54),fill=L);d.text((x+330,y+88),lbl,font=F(22),fill=WH)
foot(d,7);save(im,7)

# 08 / final campaign poster
im=cv(O);d=ImageDraw.Draw(im);d.ellipse((880,170,1640,930),fill=L)
pill(d,(78,80,460,145),"МАЛЕНЬКАЯ ПОЛЕЗНАЯ ВЕЩЬ",K,WH,19)
tx(d,(70,250),"БЕЗ БОРЬБЫ\nС УПАКОВКОЙ.",94,K,True,0)
rr(d,(70,780,1430,1450),48,C);prod(im,hero,(140,835,1220,530),-4)
tx(d,(82,1540),"ПРЕСС ДЛЯ МЯГКИХ УПАКОВОК",43,K,True,0)
d.text((86,1640),"Влажный корм • паста • майонез • кетчуп",font=F(27),fill=K)
rr(d,(80,1740,1420,1830),22,K);d.text((120,1762),"КОМПАКТНЫЙ АКСЕССУАР ДЛЯ ЕЖЕДНЕВНЫХ ЗАДАЧ",font=F(23),fill=WH)
foot(d,8);save(im,8)
print("Generated 8 redesigned slides")
