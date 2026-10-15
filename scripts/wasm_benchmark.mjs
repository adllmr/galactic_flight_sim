import fs from 'fs';
const Rc = 50, v0 = 1, dt = 0.1;
let gX = 0, gY = 0;
function grav(dx, dy, a) { const T = (Rc**2 + dy**2)**0.5, chi0 = dx - a, chi1 = dx + a;
  gX = -1 * v0**2 / (4 * a) * (Math.log(chi1**2 + T**2) - Math.log(chi0**2 + T**2));
  gY = -1 * dy * v0**2 / (2 * a * T) * (Math.atan2(chi1, T) - Math.atan2(chi0, T)); }
function integrateJS(px, py, vx, vy, a, Om, n) {   // the app's loop
  grav(px, py, a); let gx = gX, gy = gY;
  for (let i = 0; i < n; i++) {
    let fx = gx + 2 * Om * vy + Om**2 * px, fy = gy - 2 * Om * vx + Om**2 * py;
    vx += 0.5 * fx * dt; vy += 0.5 * fy * dt; px += vx * dt; py += vy * dt;
    grav(px, py, a); gx = gX; gy = gY;
    fx = gx + 2 * Om * vy + Om**2 * px; fy = gy - 2 * Om * vx + Om**2 * py;
    vx += 0.5 * fx * dt; vy += 0.5 * fy * dt;
  }
  return [px, py, vx, vy];
}
const a = 150, R = 180; grav(0, R, a); const Om = (-gY / R)**0.5;
const { instance } = await WebAssembly.instantiate(fs.readFileSync(process.argv[2]), { env: { abort() {} } });
const W = instance.exports;
const wasm = (n) => { const p = W.integrate(0, -R, 0.05, -0.02, a, Om, n); return [...new Float64Array(W.memory.buffer, p, 4)]; };
const js = (n) => integrateJS(0, -R, 0.05, -0.02, a, Om, n);
const N = 50000;
for (let i = 0; i < 30; i++) { js(N); wasm(N); }
const time = (f) => { const t = []; for (let i = 0; i < 41; i++) { const s = performance.now(); f(N); t.push(performance.now() - s); } t.sort((x, y) => x - y); return t[20]; };
const tj = time(js), tw = time(wasm);
const rj = js(N), rw = wasm(N);
console.log(`50,000 steps: JavaScript ${tj.toFixed(2)} ms, WebAssembly ${tw.toFixed(2)} ms -> ${(tj / tw).toFixed(2)}x`);
console.log(`end position: JS (${rj[0].toFixed(8)}, ${rj[1].toFixed(8)})  Wasm (${rw[0].toFixed(8)}, ${rw[1].toFixed(8)})`);
