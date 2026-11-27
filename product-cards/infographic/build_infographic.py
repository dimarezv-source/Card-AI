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
def save(im,n): im.save(OUT/f"{n:02d}.jpg",quality=94,optimize=True)
products=load_product()
if not products: raise SystemExit("No product source images found")
hero=products[0][1]
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
paste_contain(im,hero,(110,610,1280,920))
d.text((120,1510),"АККУРАТНОЕ ИЗВЛЕЧЕНИЕ СОДЕРЖИМОГО",font=font(31,True),fill=DARK)
save(im,2)
# 03 additional view / details
im,d=base("Продуманный инструмент","ПРОСТОЙ ПРИНЦИП\nИСПОЛЬЗОВАНИЯ","Конструкция помогает выдавливать содержимое из упаковки")
rounded(d,(70,520,1430,1680),44,(250,248,245))
paste_contain(im,products[min(1,len(products)-1)][1],(110,590,1280,950))
d.text((120,1510),"ПОНЯТНОЕ ПРИМЕНЕНИЕ БЕЗ СЛОЖНЫХ ДЕЙСТВИЙ",font=font(28,True),fill=DARK)
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
im,d=base("Быстро и понятно","КАК ПОЛЬЗОВАТЬСЯ","Поместите край мягкой упаковки в паз и прокручивайте / перемещайте изделие по упаковке — только если это соответствует реальной конструкции и инструкции производителя.")
rounded(d,(70,650,1430,1650),44,PALE); paste_contain(im,hero,(120,740,1260,760))
d.text((120,1510),"Перед публикацией сверьте способ применения с продавцом.",font=font(25),fill=MUTED); save(im,7)
# 08 summary
im,d=base("Для повседневных задач","УДОБНО ИЗВЛЕКАТЬ\nСОДЕРЖИМОЕ","Влажный корм • зубная паста • майонез • кетчуп")
rounded(d,(70,540,1430,1680),44,ORANGE); paste_contain(im,hero,(120,610,1260,900))
d.text((130,1510),"ПРАКТИЧНЫЙ АКСЕССУАР ДЛЯ ДОМА",font=font(34,True),fill=WHITE); save(im,8)
print(f"Generated {len(list(OUT.glob('*.jpg')))} slides in {OUT}")
