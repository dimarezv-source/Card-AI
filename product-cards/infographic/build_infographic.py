from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"product-cards"/"originals"/"tenzor"
OUT=ROOT/"product-cards"/"infographic"
OUT.mkdir(parents=True,exist_ok=True)
for stale in ("cat_domestic_eating.jpg","cat_amazing_eating.jpg","cat_wet_food.jpg","cat_eating.jpg"):
    old=OUT/stale
    if old.exists(): old.unlink()
W,H=1500,2000
ORANGE=(255,112,24); DARK=(27,29,32); MID=(91,96,102); WHITE=(255,255,255)
PALE=(255,244,235); LIGHT=(247,247,245); LINE=(230,229,226)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(sz,b=False): return ImageFont.truetype(BOLD if b else FONT,sz)
def rr(d,xy,r,fill,outline=None,width=1): d.rounded_rectangle(xy,radius=r,fill=fill,outline=outline,width=width)
def shadow(canvas,xy,r=36,fill=WHITE):
    x1,y1,x2,y2=xy
    layer=Image.new("RGBA",canvas.size,(0,0,0,0)); ld=ImageDraw.Draw(layer)
    ld.rounded_rectangle((x1+8,y1+14,x2+8,y2+14),radius=r,fill=(20,20,20,35))
    layer=layer.filter(ImageFilter.GaussianBlur(18)); canvas.alpha_composite(layer)
    ImageDraw.Draw(canvas).rounded_rectangle(xy,radius=r,fill=fill)
def contain(canvas,im,box):
    x,y,w,h=box
    if im is None: return
    q=ImageOps.contain(im.convert("RGB"),(w,h),method=Image.Resampling.LANCZOS)
    canvas.paste(q,(x+(w-q.width)//2,y+(h-q.height)//2))
def cover(canvas,im,box):
    if im is None: return
    x,y,w,h=box
    q=ImageOps.fit(im.convert("RGB"),(w,h),method=Image.Resampling.LANCZOS)
    canvas.paste(q,(x,y))
def load_product():
    out=[]
    for p in sorted(SRC.glob("*")):
        if p.suffix.lower() not in (".png",".jpg",".jpeg",".webp"): continue
        try:
            q=Image.open(p).convert("RGBA")
            if q.width>100 and q.height>100: out.append((p,q))
        except Exception: pass
    return out
def fetch(url,name):
    asset_dir=Path("/tmp/card-ai-assets")
    asset_dir.mkdir(parents=True,exist_ok=True)
    p=asset_dir/name
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"CardAI-infographic/1.0"})
        with urllib.request.urlopen(req,timeout=30) as r: p.write_bytes(r.read())
        return Image.open(p).convert("RGB")
    except Exception as e:
        print("External image unavailable",name,e)
        return None
def header(im,kicker,title,sub=None,num=None):
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,22),fill=ORANGE)
    d.text((92,76),kicker.upper(),font=f(27,True),fill=ORANGE)
    d.multiline_text((88,130),title,font=f(76,True),fill=DARK,spacing=8)
    if sub: d.multiline_text((94,330),sub,font=f(31),fill=MID,spacing=9)
    d.line((92,430,1408,430),fill=LINE,width=2)
    d.text((92,1900),"ПРЕСС ДЛЯ МЯГКИХ УПАКОВОК",font=f(21,True),fill=MID)
    if num: d.text((1350,1898),f"{num:02d}/08",font=f(22,True),fill=ORANGE)
    return d
def footer_tag(d,text,y=1770):
    rr(d,(92,y,1408,y+78),22,DARK)
    d.text((126,y+21),text,font=f(26,True),fill=WHITE)
def pouch(d,x,y,w=190,h=260):
    # Neutral illustrative soft pouch; deliberately unbranded.
    pts=[(x+18,y),(x+w-18,y),(x+w-5,y+h-25),(x+w//2,y+h),(x+5,y+h-25)]
    d.polygon(pts,fill=(244,238,226),outline=(194,180,158))
    d.line((x+22,y+34,x+w-22,y+34),fill=(194,180,158),width=5)
    d.rounded_rectangle((x+34,y+72,x+w-34,y+172),radius=18,fill=(255,255,255),outline=(225,215,200),width=3)
    d.text((x+48,y+105),"КОРМ",font=f(22,True),fill=(117,104,89))
    d.ellipse((x+w//2-13,y+h-20,x+w//2+13,y+h+6),fill=(172,104,61))
def product_card(im,hero,box,label="РЕАЛЬНЫЙ ВИД ИЗДЕЛИЯ"):
    x,y,w,h=box
    shadow(im,(x,y,x+w,y+h),30,WHITE)
    contain(im,hero,(x+22,y+22,w-44,h-105))
    d=ImageDraw.Draw(im); d.text((x+28,y+h-64),label,font=f(20,True),fill=ORANGE)
def save(im,n):
    im.convert("RGB").save(OUT/f"{n:02d}.jpg",quality=95,optimize=True)
products=load_product()
if not products: raise SystemExit("No product source images found")
hero=products[0][1]
cat1=fetch("https://images.pexels.com/photos/13317322/pexels-photo-13317322.jpeg","cat_domestic_eating.jpg")
cat2=fetch("https://images.pexels.com/photos/5822458/pexels-photo-5822458.jpeg","cat_amazing_eating.jpg")
# Record provenance and usage limits.
(OUT/"sources.txt").write_text(
"Изделие: исходные фотографии заказчика из product-cards/originals/tenzor/.\n"
"Кошка на слайде 2: Claudia Schmalz, Pexels photo 13317322, бесплатная лицензия Pexels: https://www.pexels.com/photo/close-up-shot-of-a-cat-eating-13317322/\n"
"Кошка на слайде 3: Romina BM, Pexels photo 5822458, бесплатная лицензия Pexels: https://www.pexels.com/photo/close-up-shot-of-a-cat-5822458/\n"
"Фотографии взяты из Pexels и опубликованы под бесплатной лицензией Pexels; актуальные условия: https://www.pexels.com/license/\n"
"Фотографии кошек — лайфстайл-иллюстрации. Они не показывают фактическое использование именно этого пресса. Пакетик на инфографике — схематичная иллюстрация без бренда.\n",
encoding="utf-8")
# 1 — clean hero, restrained infographic.
im=Image.new("RGBA",(W,H),WHITE); d=header(im,"ПРАКТИЧНЫЙ АКСЕССУАР","ИЗВЛЕКАЙТЕ\nСОДЕРЖИМОЕ УДОБНЕЕ","Для мягких упаковок и тюбиков",1)
shadow(im,(70,500,1430,1640),42,LIGHT); contain(im,hero,(115,555,1270,920))
rr(d,(105,1490,1395,1610),28,ORANGE)
d.text((155,1527),"ПОМОГАЕТ СОБРАТЬ ОСТАТКИ ИЗ УПАКОВКИ",font=f(31,True),fill=WHITE)
save(im,1)
# 2 — cat lifestyle, real product and a clear use-case cue.
im=Image.new("RGBA",(W,H),WHITE); d=header(im,"ДЛЯ ПИТОМЦА","ВЛАЖНЫЙ КОРМ\nБЕЗ ЛИШНИХ ОСТАТКОВ","Удобный помощник при подготовке порции",2)
shadow(im,(70,485,1430,1665),40,PALE)
if cat1: cover(im,cat1,(105,525,1290,760))
shadow(im,(105,1320,1395,1640),28,WHITE)
contain(im,hero,(145,1360,820,220))
d.text((1010,1380),"ПРЕСС ДЛЯ",font=f(25,True),fill=ORANGE)
d.text((1010,1420),"МЯГКИХ",font=f(29,True),fill=DARK)
d.text((1010,1460),"УПАКОВОК",font=f(29,True),fill=DARK)
d.text((1010,1530),"СХЕМА МЯГКОГО ПАКЕТИКА",font=f(18,True),fill=MID)
footer_tag(d,"ПОДГОТОВЬТЕ ПОРЦИЮ — ПОРАДОВАТЬ ПИТОМЦА",1715)
save(im,2)
# 3 — second cat lifestyle; use-case composition with a stronger product focal point.
im=Image.new("RGBA",(W,H),WHITE); d=header(im,"УДОБСТВО ДЛЯ ДОМА","ПОДГОТОВКА КОРМА\nБЕЗ СЛОЖНОСТЕЙ","Для подходящих мягких пакетиков",3)
shadow(im,(70,485,1430,1665),40,LIGHT)
if cat2: cover(im,cat2,(105,525,650,1030))
shadow(im,(800,560,1395,1640),32,WHITE)
d.text((855,650),"РЕАЛЬНОЕ ИЗДЕЛИЕ",font=f(24,True),fill=ORANGE)
contain(im,hero,(835,760,525,260))
d.text((855,1080),"ПОМОГАЕТ ИЗВЛЕЧЬ",font=f(25,True),fill=DARK)
d.text((855,1125),"СОДЕРЖИМОЕ ИЗ",font=f(25,True),fill=DARK)
d.text((855,1170),"МЯГКОЙ УПАКОВКИ",font=f(25,True),fill=DARK)
pouch(d,975,1280,145,205)
d.text((855,1515),"Пакетик показан схематично",font=f(18),fill=MID)
footer_tag(d,"ЛАЙФСТАЙЛ-ФОТО + РЕАЛЬНЫЙ ПРЕСС",1715)
save(im,3)

# 4 — toothpaste
im=Image.new("RGBA",(W,H),WHITE); d=header(im,"ДЛЯ ДОМАШНИХ МЕЛОЧЕЙ","ЗУБНАЯ ПАСТА\nДО ПОСЛЕДНЕГО","Помогает выдавливать содержимое из тюбика",4)
shadow(im,(70,500,1430,1645),40,PALE); contain(im,hero,(120,570,1260,850))
# illustrative tube
rr(d,(210,1370,1260,1510),34,WHITE,outline=(224,214,202),width=3)
d.text((270,1412),"ТЮБИК",font=f(32,True),fill=MID)
d.text((900,1412),"АККУРАТНЕЕ ИСПОЛЬЗОВАТЬ ОСТАТКИ",font=f(25,True),fill=ORANGE)
save(im,4)
# 5 — sauces
im=Image.new("RGBA",(W,H),WHITE); d=header(im,"ЕЩЁ ОДИН СЦЕНАРИЙ","МАЙОНЕЗ И КЕТЧУП","Для подходящих мягких упаковок",5)
shadow(im,(70,500,1430,1645),40,LIGHT); contain(im,products[-1][1] if len(products)>1 else hero,(120,560,1260,880))
for x,label in [(180,"МАЙОНЕЗ"),(790,"КЕТЧУП")]:
    rr(d,(x,1430,x+520,1555),28,WHITE,outline=LINE,width=3)
    d.text((x+40,1466),label,font=f(31,True),fill=ORANGE)
save(im,5)
# 6 — real product detail crops, arranged for stronger visual hierarchy.
im=Image.new("RGBA",(W,H),WHITE); d=header(im,"БЛИЖЕ К ДЕТАЛЯМ","КОНСТРУКЦИЯ\nВ КРУПНОМ ПЛАНЕ","Реальная форма и рабочие элементы изделия",6)
rgb=hero.convert("RGB")
shadow(im,(70,500,1430,990),34,PALE)
contain(im,rgb,(110,545,1280,390))
detail_items=[
    ("ПРОДОЛЬНЫЙ ПАЗ",rgb.crop((330,125,1270,330))),
    ("ОТВЕРСТИЯ И КРАЯ",rgb.crop((1120,35,1530,420)))
]
for i,(label,part) in enumerate(detail_items):
    x=70+i*680
    shadow(im,(x,1040,x+640,1605),30,WHITE)
    contain(im,part,(x+28,1100,584,340))
    d.text((x+32,1490),label,font=f(25,True),fill=DARK)
footer_tag(d,"ДЕТАЛИ ПОКАЗАНЫ ПО ФОТО РЕАЛЬНОГО ИЗДЕЛИЯ",1665)
save(im,6)

# 7 — dimensions, explicit source data
im=Image.new("RGBA",(W,H),WHITE); d=header(im,"ГАБАРИТЫ И ВЕС","КОМПАКТНЫЙ\nФОРМАТ","Размеры перенесены с исходного изображения товара",7)
shadow(im,(70,510,1430,1710),40,PALE); contain(im,hero,(130,560,1240,540))
specs=[("14,5 см","длина"),("3 см","высота"),("6 мм","толщина"),("13 г","вес")]
for i,(v,l) in enumerate(specs):
    x=105+(i%2)*680; y=1160+(i//2)*205
    rr(d,(x,y,x+610,y+160),26,WHITE,outline=LINE,width=2)
    d.text((x+32,y+22),v,font=f(50,True),fill=ORANGE)
    d.text((x+340,y+61),l.upper(),font=f(25,True),fill=DARK)
d.text((125,1600),"ВЫРЕЗ: 9,5 × 2 ММ",font=f(28,True),fill=DARK)
save(im,7)
# 8 — concise final benefit panel
im=Image.new("RGBA",(W,H),WHITE); d=header(im,"ОДИН АКСЕССУАР — РАЗНЫЕ ЗАДАЧИ","УДОБНО В БЫТУ","Влажный корм • паста • майонез • кетчуп",8)
rr(d,(70,500,1430,1660),44,ORANGE)
contain(im,hero,(135,570,1230,800))
d.text((150,1440),"ДЛЯ МЯГКИХ УПАКОВОК И ТЮБИКОВ",font=f(36,True),fill=WHITE)
d.text((150,1510),"Компактный размер • небольшой вес",font=f(28),fill=WHITE)
save(im,8)
print(f"Generated {len(list(OUT.glob('*.jpg')))} slides in {OUT}")
