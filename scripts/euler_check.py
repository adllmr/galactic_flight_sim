# Free particle (no gravity) seen from a frame with time-varying Omega(t).
# Integrate the rotating-frame equations with each Euler term, map back to the
# inertial frame, and measure deviation from the exact straight line.
import numpy as np
from scipy.integrate import solve_ivp
Om  = lambda t: 0.005 + 2e-5*t          # spinning up
OmD = lambda t: 2e-5
th  = lambda t: 0.005*t + 1e-5*t**2      # integral of Om
def rhs(t, s, variant):
    x, y, vx, vy = s; O, Od = Om(t), OmD(t)
    fx = 2*O*vy + O**2*x + Od*y
    fy = -2*O*vx + O**2*y - Od*(y if variant == 'original' else x)
    return [vx, vy, fx, fy]
x0, y0, vx0, vy0 = 100., -50., 0.3, 0.1
T = 600
# inertial frame: canvas rotates by +theta (xyInert), so r_rot = R(-theta) r_in
for v in ['original', 'corrected']:
    sol = solve_ivp(rhs, (0, T), [x0, y0, vx0 - (-Om(0)*y0), vy0 - Om(0)*x0] if False else
                    [x0, y0, vx0 + Om(0)*y0, vy0 - Om(0)*x0], args=(v,), rtol=1e-11, atol=1e-11, dense_output=True)
    ts = np.linspace(0, T, 50); err = 0
    for t in ts:
        x, y = sol.sol(t)[:2]; c, s = np.cos(th(t)), np.sin(th(t))
        xi, yi = x*c - y*s, x*s + y*c                     # back to inertial
        err = max(err, np.hypot(xi - (x0 + vx0*t), yi - (y0 + vy0*t)))
    print(f'{v:10s} max deviation from straight line: {err:.3e}')
