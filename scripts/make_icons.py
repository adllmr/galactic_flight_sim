"""Generate app icons from the simulator's own effective potential (run: python3 scripts/make_icons.py)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Rc, v0, a = 50.0, 1.0, 150.0
RCR = 1.2 * a

def phi(x, y):
    T = np.sqrt(Rc**2 + y**2); c0 = x - a; c1 = x + a
    return v0**2/(4*a)*((c1*np.log(c1**2+T**2)+2*T*np.arctan2(c1, T))-(c0*np.log(c0**2+T**2)+2*T*np.arctan2(c0, T)))

def fy(y):
    T = np.sqrt(Rc**2 + y**2)
    return -y*v0**2/(2*a*T)*(np.arctan2(a, T)-np.arctan2(-a, T))
Om = np.sqrt(-fy(RCR)/RCR)
def phieff(x, y): return phi(x, y) - 0.5*Om**2*(x**2+y**2)

def render(S, extent, bg=(0, 0, 64), safe=1.0):
    ss = 2; N = S*ss
    L = extent / safe
    xs = np.linspace(-L, L, N); X, Y = np.meshgrid(xs, xs)
    P = phieff(X, Y)
    lo = phieff(0, 0); hi = max(phieff(0, -1.5*RCR), phieff(0, -RCR) - 0.001)
    lev = np.floor((P - lo)/((hi - lo)/10))
    lev = np.clip(lev, -1, 11)
    edge = (np.diff(lev, axis=0, prepend=lev[:1]) != 0) | (np.diff(lev, axis=1, prepend=lev[:, :1]) != 0)
    edge &= (lev >= 0) & (lev <= 10)
    img = np.zeros((N, N, 3), np.uint8); img[:] = bg
    mask = Image.fromarray((edge*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3*ss + 1 if ss % 2 == 0 else 3*ss))
    base = Image.fromarray(img); base.paste((255, 225, 0), mask=mask)
    d = ImageDraw.Draw(base)
    px = lambda wx, wy: ((wx + L)/(2*L)*N, (wy + L)/(2*L)*N)
    # cyan orbit around L5 (small banana-ish ellipse)
    t = np.linspace(0, 2*np.pi, 200)
    pts = [px(0.55*RCR*np.sin(tt)*1.0, -RCR + 0.12*RCR*np.cos(tt)) for tt in t]
    pts = [px(RCR*np.sin(0.6*np.sin(tt)) , -(RCR + 0.10*RCR*np.cos(tt))*np.cos(0.6*np.sin(tt))) for tt in t]
    d.line(pts, fill=(0, 255, 255), width=int(N*0.012), joint='curve')
    # ship at L5, pointing right
    sx, sy = px(0, -RCR); z = N*0.085
    d.polygon([(sx - z*1.2, sy), (sx - z*0.5, sy - z*0.25), (sx - z*0.5, sy + z*0.25)], fill=(255, 165, 0))
    d.polygon([(sx + z, sy), (sx - z/2, sy - z/2), (sx - z/2, sy + z/2)], fill=(255, 255, 255), outline=(0, 0, 0))
    return base.resize((S, S), Image.LANCZOS)

ext = 1.55*RCR
icon = render(1024, ext)
icon.save(os.path.join(ROOT, 'assets', 'icon.png'))
for s, name in [(192, 'icon-192.png'), (512, 'icon-512.png'), (180, 'apple-touch-icon.png')]:
    icon.resize((s, s), Image.LANCZOS).save(os.path.join(ROOT, 'www', 'icons', name))
render(512, ext, safe=0.8).save(os.path.join(ROOT, 'www', 'icons', 'icon-maskable-512.png'))
# splash for @capacitor/assets: icon centred on navy
sp = Image.new('RGB', (2732, 2732), (0, 0, 64)); sp.paste(render(1100, ext), (816, 816))
sp.save(os.path.join(ROOT, 'assets', 'splash.png')); sp.save(os.path.join(ROOT, 'assets', 'splash-dark.png'))
print('ok', Om)
