# Is the implied density (Laplacian of Phi) non-negative everywhere for the candidate potentials?
# 3D, with the galaxy flattened equally in y and z (m^2 = x^2 + (y^2 + z^2)/q^2); we only fly in z = 0.
import numpy as np
h = 1e-3
def lap(phi, x, y, z):
    return sum((phi(*(np.array([x, y, z]) + h*e)) - 2*phi(x, y, z) + phi(*(np.array([x, y, z]) - h*e)))/h**2 for e in np.eye(3))
def hern(q):  # a = 1, GM = 4 (peak circular speed 1)
    return lambda x, y, z: -4.0/(1.0 + np.sqrt(x*x + (y*y + z*z)/q**2))
def logp(q):  # Rc = 1, v0 = 1
    return lambda x, y, z: 0.5*np.log(1.0 + x*x + (y*y + z*z)/q**2)
r = np.geomspace(0.05, 200, 60); th = np.linspace(0, np.pi/2, 40)
for name, f in [('Hernquist', hern), ('log', logp)]:
    out = []
    for q in [0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.6]:
        phi = f(q); neg = min(lap(phi, R*np.cos(t), R*np.sin(t), 0.0) / abs(lap(phi, R*np.cos(t), 0, 0)) for R in r for t in th)
        out.append(f"q={q}: {'OK' if neg >= -1e-6 else 'NEGATIVE'}")
    print(name, ' | '.join(out))
print('--- where Hernquist goes negative (radius in units of the scale length a) ---')
for q in [0.95, 0.9, 0.8]:
    phi = hern(q); bad = [R for R in r for t in th if lap(phi, R*np.cos(t), R*np.sin(t), 0.0) < 0]
    print(f'q={q}: negative for r > {min(bad):.1f} a')
print('--- log potential, flattened in y only (z like x) ---')
for q in [0.8, 0.75, 0.72, 0.71, 0.70, 0.65]:
    phi = lambda x, y, z, q=q: 0.5*np.log(1.0 + x*x + y*y/q**2 + z*z)
    neg = min(lap(phi, R*np.cos(t), R*np.sin(t), 0.0) for R in r for t in th)
    print(f'q={q}: {"OK" if neg >= -1e-9 else "NEGATIVE"}')
