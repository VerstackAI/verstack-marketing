/* Clip registry and runtime.
   Data flow: clips.js calls VS.clip(def) for each library clip. VS.mount(root, id)
   builds the clip into a Frame, waits for its images, and returns render(t).
   The player page and the catalog both use this, so what plays in the browser is
   exactly what render.py records. */
window.VS = window.VS || {};
VS.clips = VS.clips || [];

/** Register a clip: { id, group, name, build(frame) -> render(t) or { render, duration } }. */
VS.clip = (def) => { VS.clips.push(def); };

/** Build clip `id` into root at W x H. Resolves when every image has decoded. */
VS.mount = async (root, id, { W = 1920, H = 1080 } = {}) => {
  const def = VS.clips.find((c) => c.id === id);
  if (!def) throw new Error(`no clip ${id}`);
  const frame = VS.components.Frame(root, W, H);
  const imgs = () => [...frame.el.querySelectorAll("img")];
  const built = def.build(frame);
  // WHY: a clip may work out its own length from its drawings (more outlines take longer to draw).
  const render = typeof built === "function" ? built : built.render;
  const duration = (typeof built === "function" ? null : built.duration) ?? def.duration;
  await Promise.all(imgs().map((i) => (i.complete ? Promise.resolve() : i.decode().catch(() => {}))));
  render(0);
  return { def, frame, render, duration };
};

/** Loop a mounted clip in real time (with a short rest at the end). Returns stop(). */
VS.play = (mounted, { rest = 0.8, isVisible = () => true } = {}) => {
  let start = performance.now(), raf = 0, stopped = false;
  const tick = () => {
    if (stopped) return;
    if (isVisible()) {
      const t = ((performance.now() - start) / 1000) % (mounted.duration + rest);
      mounted.render(Math.min(t, mounted.duration));
    } else start = performance.now();
    raf = requestAnimationFrame(tick);
  };
  tick();
  return () => { stopped = true; cancelAnimationFrame(raf); };
};
