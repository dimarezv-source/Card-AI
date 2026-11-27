from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import urllib.request, textwrap

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"product-cards"/"originals"/"tenzor"
OUT=ROOT/"product-cards"/"infographic"
OUT.mkdir(parents=True,exist_ok=True)
W,H=1500,2000
ORANGE=(255,112,24); DARK=(28,29,31); MUTED=(100,102,105); WHITE=(255,255,255); PALE=(255,242,230)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(size,bold=False): return ImageFont.truetype(BOLD if bold else FONT,size)
def rounded(draw,xy,r,fill,outline=None,width=1): draw.rounded_rectangle(xy,radius=r,fill=fill,outline=outline,width=width)
def fit(im,box):
    return ImageOps.contain(im.convert("RGB"),box)
def load_product():
    files=sorted([p for p in SRC.glob("*") if p.suffix.lower() in (".png",".jpg",".jpeg",".webp")])
    imgs=[]
    for p in files:
        try:
            im=Image.open(p).convert("RGBA")
            if im.width>100 and im.height>100: imgs.append((p,im))
        except Exception: pass
    return imgs
def base(kicker,title,sub=None):
    im=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,28),fill=ORANGE)
    d.text((90,78),kicker.upper(),font=font(30,True),fill=ORANGE)
    d.multiline_text((90,145),title,font=font(76,True),fill=DARK,spacing=12)
    if sub: d.multiline_text((95,360),sub,font=font(34),fill=MUTED,spacing=10)
    d.rounded_rectangle((90,H-125,360,H-105),radius=10,fill=ORANGE)
    d.text((W-330,H-145),"ПРЕСС ДЛЯ УПАКОВОК",font=font(22,True),fill=MUTED)
    return im,d
def paste_contain(canvas,im,box):
    x,y,w,h=box; fitted=fit(im,(w,h)); canvas.paste(fitted,(x+(w-fitted.width)//2,y+(h-fitted.height)//2))
def paste_cover(canvas,im,box):
    x,y,w,h=box
    fitted=ImageOps.fit(im.convert("RGB"),(w,h),method=Image.Resampling.LANCZOS)
    canvas.paste(fitted,(x,y))
def get_cat(url,name):
    p=OUT/name
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"CardAI-infographic/1.0"})
        with urllib.request.urlopen(req,timeout=25) as r: p.write_bytes(r.read())
        return Image.open(p).convert("RGB")
    except Exception as e:
        print("Cat photo unavailable:",name,e)
        return None
def save(im,n): im.save(OUT/f"{n:02d}.jpg",quality=94,optimize=True)
products=load_product()
if not products: raise SystemExit("No product source images found")
hero=products[0][1]
cat1=get_cat("https://commons.wikimedia.org/wiki/Special:FilePath/Cat_eating_wet_plant-based_cat_food.jpg","cat_wet_food.jpg")
cat2=get_cat("https://commons.wikimedia.org/wiki/Special:FilePath/Amazing_cat_eating.jpg","cat_eating.jpg")
(OUT/"sources.txt").write_text(
    "Товарные фотографии: исходники заказчика из product-cards/originals/tenzor/.\\n"
    "Фото кошки 1: Jay KapLon, Cat eating wet plant-based cat food.jpg, CC BY 4.0, https://creativecommons.org/licenses/by/4.0/\\n"
    "Фото кошки 2: Usamanadda, Amazing cat eating.jpg, CC0 1.0, https://creativecommons.org/publicdomain/zero/1.0/\\n"
    "Кошачьи фото — иллюстрации категории; они не показывают фактическое использование данного пресса.\\n",
    encoding="utf-8")
# 01 hero
im,d=base("Практичное решение","ВЫДАВИТЬ ДО\nПОСЛЕДНЕЙ КАПЛИ","Удобный помощник для извлечения содержимого из упаковок")
rounded(d,(70,520,1430,1670),44,(250,248,245))
paste_contain(im,hero,(110,590,1280,950))
rounded(d,(100,1510,1400,1640),28,ORANGE)
d.text((155,1548),"МЕНЬШЕ ОСТАТКОВ ВНУТРИ УПАКОВКИ",font=font(34,True),fill=WHITE)
save(im,1)
# 02 wet food
im,d=base("Для заботы о питомце","ВЛАЖНЫЙ КОРМ —\nУДОБНО ДО КОНЦА","Помогает извлечь корм из мягкого пакетика")
rounded(d,(70,520,1430,1680),44,PALE)
if cat1: paste_cover(im,cat1,(105,585,700,930))
rounded(d,(845,650,1375,1430),28,WHITE)
paste_contain(im,hero,(865,760,490,560))
d.text((875,1370),"ПРЕСС",font=font(28,True),fill=ORANGE)
d.text((120,1560),"СЦЕНАРИЙ ДЛЯ ВЛАЖНОГО КОРМА",font=font(29,True),fill=DARK)
save(im,2)
# 03 additional view / details
im,d=base("Продуманный инструмент","ПРОСТОЙ ПРИНЦИП\nИСПОЛЬЗОВАНИЯ","Конструкция помогает выдавливать содержимое из упаковки")
rounded(d,(70,520,1430,1680),44,(250,248,245))
if cat2: paste_cover(im,cat2,(105,585,700,930))
rounded(d,(845,650,1375,1430),28,WHITE)
paste_contain(im,products[min(1,len(products)-1)][1],(865,760,490,560))
d.text((875,1370),"ПРЕСС",font=font(28,True),fill=ORANGE)
d.text((120,1560),"КОГДА ПОРА ПОРАДОВАТЬ ПИТОМЦА",font=font(29,True),fill=DARK)
save(im,3)
# 04 toothpaste
im,d=base("Не только для корма","ЗУБНАЯ ПАСТА","Подходит для выдавливания содержимого из тюбиков")
rounded(d,(70,520,1430,1680),44,PALE); paste_contain(im,hero,(120,610,1260,900))
d.text((120,1500),"ДОСТУП К ОСТАТКАМ ВНУТРИ ТЮБИКА",font=font(30,True),fill=DARK); save(im,4)
# 05 sauces
im,d=base("Универсальный помощник","МАЙОНЕЗ • КЕТЧУП","Можно использовать с подходящими мягкими упаковками")
rounded(d,(70,520,1430,1680),44,(250,248,245)); paste_contain(im,products[-1][1] if len(products)>1 else hero,(120,610,1260,900))
d.text((120,1500),"ОДИН ИНСТРУМЕНТ — РАЗНЫЕ СЦЕНАРИИ",font=font(30,True),fill=DARK); save(im,5)
# 06 product views
im,d=base("Внимание к деталям","КОНСТРУКЦИЯ\nВ КРУПНОМ ПЛАНЕ","Реальная форма изделия — без изменения пропорций")
for i,(_,p) in enumerate(products[:3]):
    x=70+i*480; rounded(d,(x,520,x+440,1480),30,PALE); paste_contain(im,p,(x+20,580,400,820))
d.text((100,1550),"ФОТО ИЗДЕЛИЯ ИЗ ИСХОДНЫХ МАТЕРИАЛОВ",font=font(30,True),fill=DARK); save(im,6)
# 07 how to use
im,d=base("Размеры и вес","КОМПАКТНЫЙ\nФОРМАТ","Параметры перенесены с исходного изображения товара.")
rounded(d,(70,590,1430,1680),44,PALE)
paste_contain(im,hero,(110,660,1280,520))
specs=[("14,5 см","длина"),("3 см","высота"),("6 мм","толщина"),("13 г","вес")]
for i,(value,label) in enumerate(specs):
    x=100+(i%2)*680; y=1240+(i//2)*180
    rounded(d,(x,y,x+620,y+145),24,WHITE)
    d.text((x+28,y+18),value,font=font(48,True),fill=ORANGE)
    d.text((x+340,y+48),label.upper(),font=font(25,True),fill=DARK)
d.text((110,1620),"ВЫРЕЗ: 9,5 × 2 ММ",font=font(28,True),fill=DARK); save(im,7)
# 08 summary
im,d=base("Для повседневных задач","УДОБНО ИЗВЛЕКАТЬ\nСОДЕРЖИМОЕ","Влажный корм • зубная паста • майонез • кетчуп")
rounded(d,(70,540,1430,1680),44,ORANGE); paste_contain(im,hero,(120,610,1260,900))
d.text((130,1510),"ПРАКТИЧНЫЙ АКСЕССУАР ДЛЯ ДОМА",font=font(34,True),fill=WHITE); save(im,8)
print(f"Generated {len(list(OUT.glob('*.jpg')))} slides in {OUT}")
