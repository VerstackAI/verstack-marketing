/* Catalog page: renders the design system from the live code.
   Data flow: VS.tokens -> Foundations; VS.clips (clips.js) -> live previews mounted with
   VS.mount and looped with VS.play only while on screen; illustrations/, product-ui/ and
   releases/_sample/ images -> reference grids. */
(() => {
  const $ = (s) => document.querySelector(s);
  const make = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };

  // Foundations ---------------------------------------------------------------
  const SWATCHES = [
    ["ground-900", "Ground. Every frame's background."], ["ground-800", "Raised dark surface."],
    ["mist", "Light card."], ["ink-700", "Drawing line and ring inner line."], ["ink-500", "Muted ink."],
    ["lime-electric", "The lime. One element at a time."], ["lime-soft", "Lime on a left-facing face."],
    ["scan-6", "Lime on a right-facing face."], ["surface-200", "Hairline on light."],
  ];
  SWATCHES.forEach(([n, use]) => {
    const v = VS.tokens[n];
    const s = make("div", "sw", `<div class="chip" style="background:${v}"></div><div class="lbl"><b>${n}</b>${v}<br>${use}</div>`);
    $("#swatches").appendChild(s);
  });
  ["seam", "card-radius", "fill", "ring", "sweep", "stroke-line", "dur-enter", "ease-standard"].forEach((n) => {
    if (VS.tokens[n]) $("#frame-tokens").appendChild(make("div", "", `${n}<span>${VS.tokens[n]}</span>`));
  });

  // Live clip previews ----------------------------------------------------------
  const live = new Map();
  const io = new IntersectionObserver((entries) => entries.forEach((e) => { const p = live.get(e.target); if (p) p.visible = e.isIntersecting; }), { rootMargin: "200px" });

  function preview(id, W, H) {
    const def = VS.clips.find((c) => c.id === id);
    const a = make("a", "clip");
    a.href = `player.html?clip=${id}&w=${W}&h=${H}`;
    a.onclick = (e) => { e.preventDefault(); open(id, W, H); };
    const stage = make("div", "stage"), inner = make("div", "inner");
    stage.style.aspectRatio = `${W} / ${H}`;
    stage.appendChild(inner);
    a.appendChild(stage);
    a.appendChild(make("div", "meta", `${def.name}<span>${id}</span>`));
    const state = { visible: false, stop: null };
    live.set(stage, state);
    const fit = () => { inner.style.transform = `scale(${stage.clientWidth / W})`; };
    new ResizeObserver(fit).observe(stage);
    // Mount once the card is in the page, so drawings can measure themselves.
    requestAnimationFrame(async () => {
      const m = await VS.mount(inner, id, { W, H });
      fit();
      state.stop = VS.play(m, { isVisible: () => state.visible });
    });
    io.observe(stage);
    return a;
  }

  // Full-size view of one clip, in the page ------------------------------------
  let closeOpen = null;
  async function open(id, W, H) {
    if (closeOpen) closeOpen();
    const def = VS.clips.find((c) => c.id === id);
    const ov = make("div", "overlay");
    const box = make("div", "ov-box"), stage = make("div", "ov-stage"), inner = make("div", "inner");
    const k = Math.min((innerWidth * 0.9) / W, (innerHeight * 0.8) / H);
    Object.assign(stage.style, { width: `${W * k}px`, height: `${H * k}px` });
    inner.style.transform = `scale(${k})`;
    stage.appendChild(inner);
    const bar = make("div", "ov-bar", `<span>${def.name}</span><span class="id">${id} &middot; ${W} x ${H} &middot; motion/out/${id}.mp4</span>`);
    const x = make("button", "ov-close", "Close");
    bar.appendChild(x);
    box.append(stage, bar);
    ov.appendChild(box);
    document.body.appendChild(ov);
    const m = await VS.mount(inner, id, { W, H });
    const stop = VS.play(m);
    closeOpen = () => { stop(); ov.remove(); closeOpen = null; };
    x.onclick = closeOpen;
    ov.onclick = (e) => { if (e.target === ov) closeOpen(); };
  }
  addEventListener("keydown", (e) => { if (e.key === "Escape" && closeOpen) closeOpen(); });

  // Components ------------------------------------------------------------------
  const COMPONENTS = [
    ["Frame and Card", "The dark ground and the light cards on it, laid out by VS.layout (single, row, grid) with a 16px seam.", "tiles-six"],
    ["Drawing", "A line drawing centred in its card; its viewBox is the camera. Draws on outline by outline; one part turns lime.", "draw-dishwasher"],
    ["Drawing camera", "Moves into the lime part and keeps hairlines at 1.25px at any zoom.", "zoom-kitchen"],
    ["Tracer", "The lime dot walking a route through a unit plan. The camera can follow it.", "trace-follow"],
    ["Phone and Ring", "A real phone screen, centred, with the lime ring on one captured element.", "app-field-home"],
    ["PushScreen", "The next screen slides in under a still status bar and device shell.", "app-push-work-order"],
    ["Screen", "A real desktop screen, centred, that zooms toward one element without showing past its edge.", "app-board-zoom"],
    ["Part", "Captured app cards (work orders, locations) placed on a card.", "app-work-orders"],
  ];
  COMPONENTS.forEach(([name, text, id]) => {
    const c = make("div", "comp", `<h3>${name}</h3><p>${text}</p>`);
    c.appendChild(preview(id, 1920, 1080));
    $("#component-list").appendChild(c);
  });

  // Motion library ----------------------------------------------------------------
  const groups = ["All", ...new Set(VS.clips.map((c) => c.group))];
  let group = "All";
  const renderLibrary = () => {
    live.forEach((s, stage) => { if (stage.closest("#library")) { if (s.stop) s.stop(); live.delete(stage); io.unobserve(stage); } });
    const lib = $("#library");
    lib.innerHTML = "";
    const [W, H] = $("#size").value.split("x").map(Number);
    VS.clips.filter((c) => group === "All" || c.group === group).forEach((c) => lib.appendChild(preview(c.id, W, H)));
  };
  groups.forEach((g) => {
    const n = g === "All" ? VS.clips.length : VS.clips.filter((c) => c.group === g).length;
    const b = make("button", g === group ? "on" : "", `${g} ${n}`);
    b.onclick = () => { group = g; [...$("#groups").children].forEach((x) => x.classList.toggle("on", x === b)); renderLibrary(); };
    $("#groups").appendChild(b);
  });
  $("#size").onchange = renderLibrary;
  renderLibrary();

  // Reference grids ---------------------------------------------------------------
  Object.keys(VS.assets.drawings).forEach((n) => {
    ["light", "dark"].forEach((theme) => {
      $("#drawing-list").appendChild(make("div", `tile${theme === "dark" ? " dark" : ""}`, `<img src="../illustrations/svg/${n}-${theme}.svg" alt="">${n}`));
    });
  });
  Object.keys(VS.assets.imageSizes).forEach((p) => {
    $("#pui-list").appendChild(make("div", "tile ui", `<img src="../product-ui/${p}" alt="">${p.replace(".png", "")}`));
  });
  ["spec-sheet-1080x1350", "data-plate-1080x1350", "annotated-1920x1080", "email-hero-1104x552", "link-preview-1200x630",
    "product-phone-1080x1350", "product-desktop-1920x1080"].forEach((n) => {
    $("#layout-list").appendChild(make("div", "tile layout", `<img src="../releases/_sample/${n}.png" alt="">${n}`));
  });
})();
