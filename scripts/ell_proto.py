import numpy as np, math, sys
Rc, v0, dt, EPS = 50.0, 1.0, 0.1, 3.0
def acc(x, y, q, mu):
    D = Rc*Rc + x*x + y*y/(q*q)
    ax = -v0*v0*x/D; ay = -v0*v0*(y/(q*q))/D
    if mu > 0:
        GM = mu*v0*v0*Rc; s = (x*x + y*y + EPS*EPS)**1.5
        ax -= GM*x/s; ay -= GM*y/s
    return ax, ay
def run(s, n, q, mu):
    x, y, vx, vy = s; ax, ay = acc(x, y, q, mu)
    for _ in range(n):
        vx += 0.5*ax*dt; vy += 0.5*ay*dt; x += vx*dt; y += vy*dt
        ax, ay = acc(x, y, q, mu); vx += 0.5*ax*dt; vy += 0.5*ay*dt
    return [x, y, vx, vy]
def starts(R0, q, mu):
    _, ay = acc(0, -R0, q, mu); vloop = math.sqrt(R0*abs(ay))
    return {'loop': [0, -R0, vloop, 0], 'box': [R0*math.cos(0.5), -R0*math.sin(0.5)*q, 0, 0],
            'long': [R0, 0, 0, 0], 'short': [0, -R0*q, 0, 0]}
def diverge(s0, q, mu, T=10000, chunk=200):
    a = list(s0); b = list(s0); b[0] += 1e-3; b[1] += 1e-3
    m = 0
    for _ in range(int(T/dt/chunk)):
        a = run(a, chunk, q, mu); b = run(b, chunk, q, mu); m = max(m, math.hypot(a[0]-b[0], a[1]-b[1]))
    return m
R0 = float(sys.argv[1]) if len(sys.argv) > 1 else 180
for q, mu in [(0.85, 0), (0.75, 0), (0.95, 0), (0.85, 0.3), (0.85, 1.0)]:
    st = starts(R0, q, mu)
    print(f'q={q} mu={mu}: ' + '  '.join(f'{k}={diverge(v, q, mu):.2e}' for k, v in st.items()))
