# Galactic Flight Simulator — mobile

One codebase in `www/`, shipped two ways:

- **PWA** – host `www/` on any HTTPS static host (GitHub Pages, Netlify, university web space). On a phone, open it and choose *Add to Home Screen*. Works offline after the first visit.
- **Native apps (Capacitor 8)** – `android/` and `ios/` are ready-made projects wrapping the same `www/` files.

## Quick start

```bash
npm install
npm run serve            # play in a browser at http://localhost:8080
```

To test on your phone over Wi-Fi, open `http://<your-computer-ip>:8080` (offline caching only activates over HTTPS or on localhost).

## Native builds

Requirements: Node 20+, **Android Studio** (Android), **Xcode 16+ on a Mac** (iOS).

```bash
npm run android          # copies www/ into the Android project and opens Android Studio → Run ▶
npm run ios              # same for Xcode (choose your team under Signing & Capabilities) → Run ▶
```

After editing anything in `www/`, run `npx cap sync` (the scripts above do it for you).

Before publishing:

1. Change `appId` in `capacitor.config.json` from `com.example.galacticflight` to an ID you own (e.g. `uk.ac.yourdomain.galacticflight`), then delete `android/` and `ios/` and re-run `npx cap add android && npx cap add ios && npm run icons`.
2. App Store: needs an Apple Developer account (£79/yr). Google Play: one-off $25 developer account.
3. Bump `VERSION` in `www/sw.js` whenever you redeploy the PWA so phones pick up the new files.

## Icons

`scripts/make_icons.py` renders the icon from the simulator's own effective potential (L5 orbit + ship). Edit and run it, then `npm run icons` to regenerate every native icon and splash size from `assets/`.

## What changed from the desktop version

- **Touch controls**: hold ⟲ / ⟳ to rotate. Thrust is a slider on the right: drag up to fire, and it springs back to zero when you let go. It goes up to **4× the original main-engine thrust** (0.002 instead of 0.0005). The response is quadratic so the bottom of the slider gives fine control: the old FINE thrust (0.0001) is about 22% of the way up and the old main engine (1×) is halfway; notches mark 1×, 2× and 3×. Multi-touch, so you can rotate and fire together. Keyboard controls are unchanged (↑ = 1×, Shift+↑ = fine). To change the maximum, edit `THRUST_MAX` in `www/index.html`.
- **Fits any screen**: buttons scale with screen width, the view is fitted so the L5 region clears the top bar, and landscape uses the full height. Checked on 13 sizes from a 320×568 iPhone SE to a 13" iPad, portrait and landscape, with no overlaps.
- **UI**: sliders and toggles moved into a settings sheet (⚙); start menu (☰) with Lagrange point choice, instructions and physics; reset-to-start (↺); respects notches and home indicators; pauses while help is open.
- **View**: physics now runs in fixed "world" coordinates (1 unit = 1 desktop pixel, Rc = 50) centred on the galaxy, and the view is scaled to fit the screen. Pinch or scroll to zoom, double-tap to reset. HiDPI rendering.
- **Timing**: fixed 60 Hz simulation tick, so 90/120 Hz phones fly at the same speed as a 60 Hz monitor.
- **Performance** (same numbers, less work):
  - gravitational force is reused between the end of one leapfrog step and the start of the next (it's at the same position) – 4× fewer force evaluations;
  - the 50,000-step projected orbit is only fully recomputed when something changes (thrust, sliders, toggles); while coasting, one interval is added to the end each tick;
  - contour grid is cached and only recomputed when the bar or zoom changes; dots are drawn in one batched path.
- **Display fix**: in the inertial (non-rotating) view the ship's nose is now rotated with the frame, so it points in the direction the thrust is actually applied.

Physics check: with η = 0, from identical initial conditions, the mobile integrator matches the desktop `predictPath()` to ~1e-11 after 50,000 steps (rotating and inertial frames). See the Euler-force fix below for η ≠ 0.

## Start menu and Lagrange points

The app opens on a menu where you choose the starting Lagrange point (L1–L5). The galaxy stays visible above the menu, or beside it in landscape, with all five points marked; tap a row or a marker to pick one, and the ship jumps there as a preview. Each point is labelled stable or unstable, with a one-line explanation. ☰ reopens the menu mid-flight: **Resume flight** carries on where you were, **Launch** restarts from the chosen point, and ↺ returns to it at any time. The markers can be hidden in Settings.

How the points are found (`lagrangePoints()` in `www/index.html`): they are the stationary points of Φ_eff, where gravity plus centrifugal force is zero for a ship at rest in the rotating frame.
- L4/L5: on the minor axis at exactly ±R_CR, because that's how Ω is defined from R_CR.
- L3: the centre.
- L1/L2: on the major axis at ±x_L, found by bisection on `gX(x, 0) + Ω² x = 0`. For the default bar, x_L = 211.2 versus R_CR = 180.
- Stability: on the axes Φ_xy = 0, so the linearised equations with the Coriolis terms give λ⁴ + (Φ_xx + Φ_yy + 4Ω²) λ² + Φ_xx Φ_yy = 0. A point is stable when both roots for λ² are real and negative. L1/L2 come out unstable (saddles). L3 is stable (minimum). L4/L5 are stable maxima, held by the Coriolis force.
- Everything is recomputed every frame, so the points and their labels follow the sliders, including a bar that changes with η.

Checks: the residual force at each point is ~1e-18. Over five bar settings, nudging the ship 0.7 units and coasting for t = 20,000 gives drift of 1–3 units for L3/L4/L5 and 200–500 units for L1/L2, matching the stability test.

Placing the ship exactly on L1 or L2 balances it so precisely that the instability (e-folding time ≈ 350 time units) takes a few minutes at speed 1.0 to grow rounding errors into visible drift. A small thrust sends it away at once.

## Elliptical galaxy

Choose **Elliptical** at the top of the start menu. It's a non-rotating galaxy with a flattened logarithmic potential (Binney & Tremaine):

  Φ = ½ v₀² ln(R_c² + x² + y²/q²)  [+ optional softened black hole −GM/√(r² + ε²), ε = 3]

It uses the same units as the bar (R_c = 50, v₀ = 1). There is no rotation, so there are no Coriolis or centrifugal forces and no Lagrange points.
- **Settings** (shown only for this galaxy): axis ratio q from 0.71 to 1 (default 0.85), black-hole mass GM / v₀²R_c from 0 to 1 (default 0, off), and starting radius from 0.5 to 8 R_c (default 3.6 R_c = 180, the same radius as the bar's L4/L5).
- **Why q ≥ 0.71:** below 1/√2 the density implied by the potential goes negative (checked numerically). I avoided the simpler flattened-potential Hernquist model because its implied density is negative beyond a few scale lengths at any flattening.
- **Starting orbits:**
  - *Loop*: launched from the short axis at the local circular speed.
  - *Box*: released at rest off the axes, with zero angular momentum.
  - *Long-axis* and *short-axis*: released at rest on each axis.
- **Stability labels:** each start is integrated next to a copy displaced by 0.001 units for t = 8000. If they separate by more than 5 units, it's labelled unstable. Regular orbits stay within about 0.1 units; unstable ones separate by hundreds. Without a black hole, the short-axis orbit is the only unstable one. With GM = 0.3, the box and both axis orbits become unstable. The check reruns when you change q, the black hole or the radius.
- **Checks:** energy is conserved to ~1e-8 for loop and box orbits, and ~4e-4 for a box orbit plunging through a GM = 1 black hole. Switching back to the barred spiral restores its physics; it still matches the desktop original to ~1e-11.

## Performance notes: is WebAssembly worth it?

I benchmarked the hot loop (the 50,000-step projected orbit, same equations) in Node 22, which uses Chrome's V8 engine:

| | Time for 50,000 steps | Result |
|---|---|---|
| JavaScript (the app's loop) | 6.9 ms | reference |
| WebAssembly (AssemblyScript, -O3) | 4.9 ms | identical to 8 decimal places |

That's about 1.4× faster. The loop is dominated by `log` and `atan2`, which V8 already compiles to fast machine code, so WebAssembly has little to win. Rust or C would land in the same range; I couldn't build Rust here because its WebAssembly toolchain download was blocked.

The real cost is *when* the work happens. While coasting, a tick costs ~0.02 ms because the orbit is extended incrementally. While thrusting, the whole projected orbit is recomputed every frame: ~8 ms on a desktop, roughly 35 ms on a phone-speed CPU, which can drop frames. A Web Worker or spreading the rebuild over several frames fixes that regardless of language.

### Background thread (implemented)

The projected orbit and the elliptical-galaxy stability check now run on a Web Worker, so thrusting no longer stalls the animation.
- **One copy of the physics.** The equations live in `<script id="physics">`, which has no DOM access. The page runs it, and the worker is built from the same text (a `blob:` URL), so there is no second copy of the physics to keep in sync.
- **How a rebuild works.** The worker integrates from a snapshot of the ship. When its result arrives, the ship has flown on a few ticks, so that many points are dropped from the front of the path and the same number added at the end.
- **Exact.** For both galaxies, the worker's path after catch-up matches one computed in place exactly (difference 0). While coasting, the ship lands exactly on each successive path point.
- **During a burn,** the cyan line can lag the ship by a frame or two.
- **Fallback.** If a device can't create the worker, the app falls back to computing on the main thread, as before (tested with `Worker` removed).
- **Timing.** On a CPU throttled 4× (roughly phone speed), in a headless browser that draws in software and tops out at ~30 fps:

| | Coasting | Thrusting |
|---|---|---|
| Before (main thread) | 30 fps | 15 fps |
| With the background thread | 29 fps | 24 fps |

The 27 ms rebuild is gone from the main thread. A real phone draws with the GPU and has more cores, so the coasting ceiling will be higher (typically 60 fps) and thrusting should stay close to it.

## Physics fix: Euler force

The desktop `totalForce()` had the y-component of the Euler force as `- OmegaDot * dy`; it should be `- OmegaDot * dx`, so the fictitious force is `-dΩ/dt × r = (Ω̇ y, -Ω̇ x)`, the same sign convention as the Coriolis term already in the code. This is corrected in `integrate()` in `www/index.html`. It only matters when the bar is speeding up or slowing down (η ≠ 0).

Check (`scripts/euler_check.py`): a force-free particle integrated in a frame with time-varying Ω and mapped back to the inertial frame should move in a straight line. With the original term it is off by ~400 units after t = 600; with the corrected term the deviation is ~6e-9.

With η = 0 the mobile and desktop trajectories agree to ~1e-11 after 50,000 steps. With η ≠ 0 they now differ, because of this fix.
