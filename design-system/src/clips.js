/* The motion library: 50 clips, imagery only.
   Rules every clip follows (checked by design-system/scripts/verify.py):
   - no text of any kind: no headlines, labels or callouts;
   - each piece of imagery is centred both ways in its card;
   - one lime element on screen at a time (a lime part, the trace dot, or a ring);
   - cards are on screen from the first frame, so clips cut together cleanly.
   Data flow: VS.clip() registers each definition; VS.mount() builds it into a Frame. */
(() => {
  const { Card, Layer, Drawing, Phone, PushScreen, Screen, Part, Ring, Tracer, Sweep } = VS.components;
  const { draw, lime, shown, rise, zoom, ring } = VS.moves;
  const { ease, prog, lerp, smooth } = VS.engine;
  const L = VS.layout;

  // The part of each object drawing that turns lime (an anchor in illustrations/anchors.json).
  // building, building-floors, unit-plan and phone carry their own lime part.
  // The part of each object drawing that turns lime (an anchor in illustrations/anchors.json).
  // Small on purpose: a lime part covers at most a fifth of its drawing (verify.py checks).
  // building, building-floors, unit-plan and phone carry their own lime part.
  const PART = {
    dishwasher: "display", fridge: "dispenser", range: "hob", "washer-dryer": "washer", vanity: "basin",
    toilet: "seat", "water-heater": "plate", furnace: "filter", condenser: "fan-ring", "rooftop-unit": "hood",
    "electrical-panel": "main", thermostat: "dial", "smoke-detector": "sensor", ladder: "top",
    toolbox: "handle", paint: "can", laptop: "trackpad",
  };
  const NAME = {
    building: "Building", "unit-plan": "Unit plan", dishwasher: "Dishwasher", fridge: "Fridge", range: "Range",
    "washer-dryer": "Washer and dryer", vanity: "Vanity", toilet: "Toilet", "water-heater": "Water heater",
    furnace: "Furnace", condenser: "Condenser", "rooftop-unit": "Rooftop unit", "electrical-panel": "Electrical panel",
    thermostat: "Thermostat", "smoke-detector": "Smoke detector", ladder: "Ladder", toolbox: "Toolbox",
    paint: "Paint", phone: "Phone", laptop: "Laptop",
  };
  const ROUTE = Array.from({ length: 15 }, (_, i) => `route-${i}`);

  /** Draw-on timing scaled to the drawing: more outlines take longer, within limits. */
  function timing(d, t0 = 0.2, { min = 0.8, max = 2.2, per = 0.018, dur = 0.6 } = {}) {
    const span = Math.min(max, Math.max(min, d.items.length * per));
    return { t0, span, dur, done: t0 + span + dur };
  }
  // Flat or wide drawings read larger than tall ones at the same fill; these scale down.
  const SCALE = { "smoke-detector": 0.6, paint: 0.85, toolbox: 0.9 };
  const one = (f) => Card(f, L.single(f)[0]);
  const drawing = (card, name, opts = {}) => {
    const k = SCALE[name] || 1, fill = (opts.fill ?? 0.68) * k, fillW = (opts.fillW ?? 0.8) * k;
    return Drawing(card, name, { lime: PART[name] || null, ...opts, fill, fillW });
  };

  // 1. Draw: each drawing draws on, centred, then its part turns lime (20) ----------
  ["building", "unit-plan", "dishwasher", "fridge", "range", "washer-dryer", "vanity", "toilet", "water-heater",
    "furnace", "condenser", "rooftop-unit", "electrical-panel", "thermostat", "smoke-detector", "ladder",
    "toolbox", "paint", "phone", "laptop"].forEach((n) => VS.clip({
    id: `draw-${n}`, group: "Draw", name: NAME[n],
    build(f) {
      const c = one(f), d = drawing(c, n);
      // The one clip in the library with the scan-gradient sweep (rule: rare, never a cut).
      const sw = n === "building" ? Sweep(c) : null;
      const tm = timing(d), hl = tm.done + 0.25;
      return { duration: hl + 0.48 + 1.5, render(t) { if (sw) sw.at(t, 0.15); draw(d, t, tm.t0, tm.span, tm.dur, hl); } };
    },
  }));

  // 2. Explode: the building opens floor by floor (3) ----------------------------------
  function floors(d) { return { fl: [0, 1, 2, 3, 4].map((k) => d.svg.querySelector(`#floor-${k}`)), roof: d.svg.querySelector("#roof") }; }

  function explodeClip(id, name, { back }) {
    VS.clip({
      id, group: "Explode", name,
      build(f) {
        const c = one(f);
        const GAP = VS.assets.drawings["building-floors"].viewBox[3] * 0.08; // lift per floor, drawing units
        const d = Drawing(c, "building-floors", { lift: 5 * GAP });
        const { fl, roof } = floors(d);
        const tm = timing(d), E0 = tm.done + 0.1, HL = E0 + 0.95, E1 = back ? HL + 1.5 : Infinity;
        const amount = (t, k) => ease(prog(t, E0 + (5 - k) * 0.08, 0.64)) * (1 - ease(prog(t, E1 + k * 0.06, 0.64)));
        return {
          duration: back ? E1 + 0.64 + 0.4 + 1.0 : HL + 0.48 + 1.6,
          render(t) {
            draw(d, t, tm.t0, tm.span, tm.dur, HL, back ? E1 - 0.1 : Infinity);
            fl.forEach((g, k) => g.setAttribute("transform", `translate(0 ${-k * GAP * amount(t, k)})`));
            roof.setAttribute("transform", `translate(0 ${-5 * GAP * amount(t, 5)})`);
            // WHY: keep the opening building centred: the camera rises with half the lift.
            d.look(d.base.cx, d.base.cy - 2.5 * GAP * amount(t, 5));
          },
        };
      },
    });
  }
  explodeClip("explode-building", "Explode and close", { back: true });
  explodeClip("explode-open", "Explode and hold", { back: false });
  VS.clip({
    id: "assemble-building", group: "Explode", name: "Assemble floor by floor",
    build(f) {
      const c = one(f), d = Drawing(c, "building-floors");
      const { fl, roof } = floors(d), parts = [...fl, roof];
      const DROP = d.rest.height * 0.5, T0 = 0.2, STEP = 0.32, DUR = 0.62;
      shown(d);
      const HL = T0 + STEP * 5 + DUR + 0.3;
      return {
        duration: HL + 0.48 + 1.5,
        render(t) {
          parts.forEach((g, k) => {
            const p = ease(prog(t, T0 + k * STEP, DUR));
            g.setAttribute("transform", `translate(0 ${-(1 - p) * DROP})`);
            g.style.opacity = prog(t, T0 + k * STEP, DUR * 0.5);
          });
          lime(d, t, HL);
        },
      };
    },
  });

  // 3. Zoom: the camera moves into the part that matters (4) ------------------------
  function zoomClip(id, name, drawingName, focus, s, opts = {}) {
    VS.clip({
      id, group: "Zoom", name,
      build(f) {
        const c = one(f), d = Drawing(c, drawingName, opts);
        const tm = timing(d), HL = tm.done + 0.2, Z0 = HL + 0.7, ZD = 1.3;
        // Land on the lime part itself when there is one, so it ends centred.
        const at = d.limeCenter() || d.anchor(focus);
        return { duration: Z0 + ZD + 1.4, render(t) { draw(d, t, tm.t0, tm.span, tm.dur, HL); zoom(d, t, Z0, ZD, s, at); } };
      },
    });
  }
  zoomClip("zoom-unit", "Into one unit", "building", "unit", 2.6);
  zoomClip("zoom-kitchen", "Into the kitchen", "unit-plan", "dishwasher", 2.4);
  zoomClip("zoom-bath", "Into the bathroom", "unit-plan", "bath", 2.4, { lime: "bath" });
  VS.clip({
    id: "zoom-out-building", group: "Zoom", name: "Out from a unit",
    build(f) {
      const c = one(f), d = Drawing(c, "building"), at = d.anchor("unit");
      shown(d);
      return { duration: 4.2, render(t) { lime(d, t, -1); const p = ease(prog(t, 0.5, 1.8)); d.camera(lerp(2.6, 1, p), at, 1 - p); } };
    },
  });

  // 4. Trace: the capture walk, room by room (3) ---------------------------------------
  VS.clip({
    id: "trace-walk", group: "Trace", name: "Walk the unit",
    build(f) {
      const c = one(f), d = Drawing(c, "unit-plan", { limeOff: true }), tr = Tracer(d, ROUTE);
      const tm = timing(d), T0 = tm.done + 0.15, TD = 5.2;
      return { duration: T0 + TD + 1.2, render(t) { draw(d, t, tm.t0, tm.span, tm.dur); tr.at(smooth(prog(t, T0, TD)), t >= T0 - 0.2 ? 1 : 0); } };
    },
  });
  VS.clip({
    id: "trace-to-kitchen", group: "Trace", name: "Walk to the kitchen",
    build(f) {
      const c = one(f), d = Drawing(c, "unit-plan"), tr = Tracer(d, ROUTE.slice(0, 9));
      const tm = timing(d), T0 = tm.done + 0.15, TD = 2.8, OUT = T0 + TD + 0.15, HL = OUT + 0.3;
      return {
        duration: HL + 0.48 + 1.5,
        render(t) {
          draw(d, t, tm.t0, tm.span, tm.dur, HL);
          // One lime at a time: the dot leaves before the dishwasher turns lime.
          tr.at(smooth(prog(t, T0, TD)), t < T0 - 0.2 ? 0 : 1 - prog(t, OUT, 0.3));
        },
      };
    },
  });
  VS.clip({
    id: "trace-follow", group: "Trace", name: "Follow the walk",
    build(f) {
      const c = one(f), d = Drawing(c, "unit-plan", { limeOff: true }), tr = Tracer(d, ROUTE);
      const tm = timing(d), Z0 = tm.done + 0.1, T0 = Z0 + 0.6, TD = 6.0, Z1 = T0 + TD + 0.1, S = 1.9;
      return {
        duration: Z1 + 0.9 + 0.8,
        render(t) {
          draw(d, t, tm.t0, tm.span, tm.dur);
          const p = smooth(prog(t, T0, TD)), q = tr.pointAt(p);
          const z = ease(prog(t, Z0, 0.9)) * (1 - ease(prog(t, Z1, 0.9)));
          d.camera(lerp(1, S, z), [q.x, q.y], z);
          tr.at(p, t >= Z0 ? 1 : 0);
        },
      };
    },
  });

  // 5. Swap: one card, one drawing after another (6) -----------------------------------
  function swapClip(id, name, names) {
    VS.clip({
      id, group: "Swap", name,
      build(f) {
        const c = one(f);
        let t0 = 0.2;
        const seg = names.map((n) => {
          const layer = Layer(c), d = drawing(c, n, { parent: layer });
          const tm = timing(d, t0, { min: 0.7, max: 1.4, per: 0.014, dur: 0.5 });
          const s = { layer, d, tm, hl: tm.done + 0.15 };
          s.out = s.hl + 0.48 + 0.75;
          t0 = s.out + 0.4;
          return s;
        });
        const last = seg[seg.length - 1];
        return {
          duration: last.hl + 0.48 + 1.4,
          render(t) {
            seg.forEach((s) => {
              draw(s.d, t, s.tm.t0, s.tm.span, s.tm.dur, s.hl);
              s.layer.style.opacity = s === last ? 1 : 1 - ease(prog(t, s.out, 0.35));
            });
          },
        };
      },
    });
  }
  swapClip("swap-kitchen", "Kitchen", ["fridge", "range", "dishwasher"]);
  swapClip("swap-bath-laundry", "Bath and laundry", ["vanity", "toilet", "washer-dryer"]);
  swapClip("swap-mechanical", "Mechanical", ["water-heater", "furnace", "condenser", "rooftop-unit"]);
  swapClip("swap-safety", "Power and safety", ["electrical-panel", "thermostat", "smoke-detector"]);
  swapClip("swap-turn", "Unit turn", ["ladder", "paint", "toolbox"]);
  swapClip("swap-devices", "Devices", ["phone", "laptop"]);

  // 6. Tiles: a bento of cards, one drawing centred in each (6) ----------------------
  function tilesClip(id, name, names, { cols = names.length, rows = 1, target = null, walk = false } = {}) {
    VS.clip({
      id, group: "Tiles", name,
      build(f) {
        const boxes = rows > 1 ? L.grid(f, cols, rows) : L.row(f, names.length);
        const tiles = names.map((n, i) => {
          const c = Card(f, boxes[i]);
          const d = drawing(c, n, { fill: rows > 1 ? 0.62 : 0.58, fillW: 0.74 });
          return { d, tm: timing(d, 0.2 + i * 0.22, { min: 0.6, max: 1.3, per: 0.014, dur: 0.5 }) };
        });
        const all = Math.max(...tiles.map((x) => x.tm.done)) + 0.25, STEP = 1.15;
        tiles.forEach((x, i) => {
          if (walk) { x.on = all + i * STEP; x.off = i === tiles.length - 1 ? Infinity : x.on + 0.7; }
          else { x.on = i === target ? all : Infinity; x.off = Infinity; }
        });
        const end = walk ? all + (tiles.length - 1) * STEP : all;
        return { duration: end + 0.48 + 1.5, render(t) { tiles.forEach((x) => draw(x.d, t, x.tm.t0, x.tm.span, x.tm.dur, x.on, x.off)); } };
      },
    });
  }
  tilesClip("tiles-kitchen", "Kitchen, three up", ["fridge", "range", "dishwasher"], { target: 2 });
  tilesClip("tiles-mechanical", "Mechanical, three up", ["water-heater", "furnace", "condenser"], { target: 0 });
  tilesClip("tiles-bath-laundry", "Bath and laundry, three up", ["vanity", "toilet", "washer-dryer"], { target: 1 });
  tilesClip("tiles-six", "Six appliances", ["fridge", "range", "dishwasher", "washer-dryer", "water-heater", "furnace"], { cols: 3, rows: 2, target: 4 });
  tilesClip("tiles-six-walk", "Six appliances, lime moves", ["fridge", "range", "dishwasher", "washer-dryer", "water-heater", "furnace"], { cols: 3, rows: 2, walk: true });
  tilesClip("tiles-building-plan", "Building to unit", ["building", "unit-plan"], { walk: true });

  // 7. App: real screens from the app, centred, one ring at a time (8) ------------------
  const RISE = 40;
  function phoneClip(id, name, screen, rings, gap = 0.3) {
    VS.clip({
      id, group: "App", name,
      build(f) {
        const c = one(f), ph = Phone(c, screen);
        let t0 = 1.2;
        const rs = rings.map((n, i) => {
          const r = { el: Ring(c, ph.box(n)), on: t0 };
          r.off = i === rings.length - 1 ? Infinity : t0 + 1.3;
          t0 = r.off + gap;
          return r;
        });
        const lastOn = rs[rs.length - 1].on;
        return { duration: lastOn + 0.36 + 1.6, render(t) { rise(ph.el, t, 0.15, 0.7, RISE * f.u); rs.forEach((r) => ring(r.el, t, r.on, r.off)); } };
      },
    });
  }
  phoneClip("app-field-home", "Field home, waiting on you", "field-home", ["waiting"]);
  phoneClip("app-report", "Report status, then decisions", "report", ["status", "to-decide"]);
  VS.clip({
    id: "app-push-work-order", group: "App", name: "Work list to work order",
    build(f) {
      const c = one(f), ph = Phone(c, "manager-work"), push = PushScreen(ph, "work-order");
      const r1 = Ring(c, ph.box("water-heater")), r2 = Ring(c, push.box("quote"));
      return {
        duration: 5.6,
        render(t) {
          rise(ph.el, t, 0.15, 0.7, RISE * f.u);
          ring(r1, t, 1.2, 2.6);
          push.at(ease(prog(t, 2.95, 0.55)));
          ring(r2, t, 3.75);
        },
      };
    },
  });
  VS.clip({
    id: "app-phone-pair", group: "App", name: "Two phones, request and quote",
    build(f) {
      const c = one(f), h = 0.8 * c.h, w = h * (421 / 880), half = w / 2 + 50 * f.u;
      const a = Phone(c, "manager-work", { fill: 0.8, dx: -half }), b = Phone(c, "work-order", { fill: 0.8, dx: half });
      const r1 = Ring(c, a.box("water-heater")), r2 = Ring(c, b.box("quote"));
      return {
        duration: 5.0,
        render(t) {
          rise(a.el, t, 0.15, 0.7, RISE * f.u); rise(b.el, t, 0.4, 0.7, RISE * f.u);
          ring(r1, t, 1.5, 2.8); ring(r2, t, 3.1);
        },
      };
    },
  });
  function screenClip(id, name, screen, focus, s, { zoomAt = 1.3, zoomDur = 1.4, ringAt = null } = {}) {
    VS.clip({
      id, group: "App", name,
      build(f) {
        const c = one(f), sc = Screen(c, screen), r = Ring(c, sc.box(focus), { pad: 10, radius: 18 });
        const R = ringAt ?? zoomAt + zoomDur + 0.1;
        return {
          duration: R + 0.36 + 1.6,
          render(t) {
            rise(sc.el, t, 0.15, 0.7, RISE * f.u);
            sc.view(s, focus, ease(prog(t, zoomAt, zoomDur)));
            r.place(sc.box(focus));
            ring(r, t, R);
          },
        };
      },
    });
  }
  screenClip("app-board-zoom", "Board, into the leak", "maintenance-board", "leak", 2.1);
  screenClip("app-reports", "Reports, the first report", "reports", "first-report", 1, { ringAt: 1.3 });
  screenClip("app-locations", "Locations, into one", "locations", "first", 1.7);
  VS.clip({
    id: "app-work-orders", group: "App", name: "A stack of work orders",
    build(f) {
      // Back to front: door, parts, then the leak in front with the ring. Each card shows
      // its title row above the next; the stack as a whole is centred in the card.
      const c = one(f), S = VS.assets.imageSizes, w = c.w * 0.5, step = 150 * f.u;
      const srcs = ["door", "parts", "leak"].map((n) => `desktop/parts/work-order-card-${n}.png`);
      const hs = srcs.map((src) => (S[src][1] / S[src][0]) * w);
      const total = 2 * step + hs[2];
      const parts = srcs.map((src, i) => Part(c, src, { w, y: (c.h - total) / 2 + i * step, natural: S[src] }));
      const r = Ring(c, parts[2], { pad: 10, radius: 26 });
      return { duration: 4.4, render(t) { parts.forEach((p, i) => rise(p.el, t, 0.15 + i * 0.22, 0.6, RISE * f.u)); ring(r, t, 1.7); } };
    },
  });
})();
