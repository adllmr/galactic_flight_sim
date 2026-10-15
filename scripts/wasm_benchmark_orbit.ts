// Same leapfrog loop as integrate() in www/index.html (barred potential, rotating frame, aDot = 0)
const RC: f64 = 50.0;
const OUT = new StaticArray<f64>(4);
let gx: f64 = 0, gy: f64 = 0;
@inline function grav(dx: f64, dy: f64, a: f64): void {
  const t = Math.sqrt(RC * RC + dy * dy);
  const chi0 = dx - a, chi1 = dx + a;
  gx = -1.0 / (4.0 * a) * (Math.log(chi1 * chi1 + t * t) - Math.log(chi0 * chi0 + t * t));
  gy = -1.0 * dy / (2.0 * a * t) * (Math.atan2(chi1, t) - Math.atan2(chi0, t));
}
export function integrate(px: f64, py: f64, vx: f64, vy: f64, a: f64, om: f64, n: i32): usize {
  const dt: f64 = 0.1;
  grav(px, py, a);
  let hx = gx, hy = gy;
  for (let i = 0; i < n; i++) {
    let fx = hx + 2.0 * om * vy + om * om * px;
    let fy = hy - 2.0 * om * vx + om * om * py;
    vx += 0.5 * fx * dt; vy += 0.5 * fy * dt;
    px += vx * dt; py += vy * dt;
    grav(px, py, a); hx = gx; hy = gy;
    fx = hx + 2.0 * om * vy + om * om * px;
    fy = hy - 2.0 * om * vx + om * om * py;
    vx += 0.5 * fx * dt; vy += 0.5 * fy * dt;
  }
  OUT[0] = px; OUT[1] = py; OUT[2] = vx; OUT[3] = vy;
  return changetype<usize>(OUT);
}
