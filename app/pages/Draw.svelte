<script>
  // Draw: sketch one grapheme and see the glyphs closest to it. There is no recognizer for the script;
  // this compares where ink lies with the printed glyphs of one face, and says so beside the results.
  import { onMount } from 'svelte'
  import { db } from '../lib/db.svelte.js'
  import { ix } from '../lib/data.js'
  import { parseShapes, indexShapes, rasterize, rankShapes, SIZE } from '../lib/shape.js'
  import { put, ui } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'
  import Tile from '../ui/Tile.svelte'

  /** @type {HTMLCanvasElement | null} */
  let canvas = $state(null)
  /** Strokes as fractions of the pad's side, so they survive the pad changing size. @type {[number, number][][]} */
  let strokes = $state.raw([])
  /** @type {[number, number][] | null} */
  let current = null
  /** The one pointer drawing; a palm or second finger is ignored. @type {number | null} */
  let pen = null
  /** @type {'loading' | 'ready' | 'failed'} */
  let status = $state('loading')
  /** @type {import('../lib/shape.js').ShapeIndex | null} */
  let index = $state.raw(null)
  /** @type {Uint8Array} */
  let mask = $state.raw(new Uint8Array(SIZE * SIZE))

  onMount(() => {
    fetch('/data/shapes.bin')
      .then(response => { if (!response.ok) throw new Error(String(response.status)); return response.arrayBuffer() })
      .then(buffer => { index = indexShapes(parseShapes(new Uint8Array(buffer))); status = 'ready' })
      .catch(() => { status = 'failed' })
    resize()
    // The ink colour comes from the theme, which the system can change too.
    const scheme = matchMedia('(prefers-color-scheme: dark)')
    scheme.addEventListener('change', paint)
    return () => scheme.removeEventListener('change', paint)
  })

  $effect(() => {
    void ui.theme
    paint()
  })

  const hits = $derived.by(() => {
    if (status !== 'ready' || db.status !== 'ready' || !index || !strokes.length) return []
    return rankShapes(index, mask, { limit: 48 }).map(hit => ix.byChar.get(hit.char)).filter(Boolean)
  })

  function resize() {
    if (!canvas) return
    const box = canvas.getBoundingClientRect()
    const ratio = devicePixelRatio || 1
    canvas.width = Math.round(box.width * ratio)
    canvas.height = Math.round(box.height * ratio)
    paint()
  }

  function paint() {
    const context = canvas?.getContext('2d')
    if (!canvas || !context) return
    const ratio = devicePixelRatio || 1
    context.setTransform(ratio, 0, 0, ratio, 0, 0)
    const { width, height } = canvas.getBoundingClientRect()
    context.clearRect(0, 0, width, height)
    context.strokeStyle = getComputedStyle(canvas).color
    context.lineCap = 'round'
    context.lineJoin = 'round'
    context.lineWidth = Math.max(5, width / 42)
    for (const stroke of [...strokes, ...(current ? [current] : [])]) {
      context.beginPath()
      stroke.forEach(([x, y], i) => i ? context.lineTo(x * width, y * height) : context.moveTo(x * width, y * height))
      if (stroke.length === 1) context.lineTo(stroke[0][0] * width + 0.1, stroke[0][1] * height)
      context.stroke()
    }
  }

  /** @param {PointerEvent} event @returns {[number, number]} */
  function point(event) {
    const box = /** @type {HTMLCanvasElement} */ (canvas).getBoundingClientRect()
    return [(event.clientX - box.left) / box.width, (event.clientY - box.top) / box.height]
  }

  /** @param {PointerEvent} event */
  function down(event) {
    if (event.button !== 0 || pen !== null) return
    pen = event.pointerId
    canvas?.setPointerCapture(event.pointerId)
    current = [point(event)]
    paint()
  }

  /** @param {PointerEvent} event */
  function move(event) {
    if (!current || event.pointerId !== pen) return
    const [x, y] = point(event)
    const last = current[current.length - 1]
    const side = /** @type {HTMLCanvasElement} */ (canvas).getBoundingClientRect().width
    if (Math.hypot(x - last[0], y - last[1]) * side < 2) return
    current.push([x, y])
    paint()
  }

  /** @param {PointerEvent} event */
  function up(event) {
    if (!current || event.pointerId !== pen) return
    pen = null
    strokes = [...strokes, current]
    current = null
    update()
  }

  function update() {
    mask = rasterize(strokes)
    paint()
  }

  function undo() { strokes = strokes.slice(0, -1); update() }
  function clear() { strokes = []; update() }

  /** @param {KeyboardEvent} event */
  function keys(event) {
    // The sponsor dialog is modal: its keys do not reach the pad behind it.
    if (document.querySelector('dialog[open]')) return
    const target = /** @type {HTMLElement} */ (event.target)
    if (target.closest('input, textarea, select')) return
    if ((event.ctrlKey || event.metaKey) && event.key === 'z') { event.preventDefault(); undo() }
    // Something else already took this Escape, such as the settings closing.
    else if (event.key === 'Escape' && !event.defaultPrevented) clear()
    // A focused link, tile or button keeps its own Enter.
    else if (event.key === 'Enter' && hits[0] && !target.closest('a, button')) { event.preventDefault(); put(hits[0].char); clear() }
  }
</script>

<svelte:window onresize={resize} onkeydown={keys} />

<div class="ui-page draw" data-width="wide">
  <section class="pad-column" aria-label={t('draw.canvas')}>
    <header class="ui-page-head">
      <h1 class="ui-page-title">{t('nav.draw')}</h1>
      <p class="ui-page-intro">{t('draw.intro')}</p>
    </header>
    <div class="pad">
      <canvas bind:this={canvas} aria-label={t('draw.canvas')}
        onpointerdown={down} onpointermove={move} onpointerup={up} onpointercancel={up}></canvas>
      {#if !strokes.length}<p class="hint" aria-hidden="true">{t('draw.here')}</p>{/if}
    </div>
    <div class="tools">
      <button type="button" class="ui-button" data-size="sm" onclick={undo} disabled={!strokes.length}>{t('draw.undo')}</button>
      <button type="button" class="ui-button" data-size="sm" onclick={clear} disabled={!strokes.length}>{t('draw.clear')}</button>
      <span class="ui-count strokes">{t('draw.strokes', { count: strokes.length })}</span>
    </div>
  </section>

  <section class="results" aria-label={t('draw.results')}>
    <div class="ui-section-head">
      <h2 class="ui-label">{t('draw.results')}</h2>
      {#if status === 'loading'}<span class="ui-count">{t('draw.loading')}</span>{:else if status === 'failed'}<span class="ui-count">{t('draw.failed')}</span>{/if}
    </div>
    {#if hits.length}
      <div class="ui-tiles" style:--ui-tile-size="62px">{#each hits as g (g.id)}<Tile {g} />{/each}</div>
      <p class="ui-hint keys">{t('draw.keys')}</p>
    {:else if status === 'ready' && !strokes.length}
      <p class="ui-empty">{t('draw.empty')}</p>
    {/if}
    <p class="ui-notice note">{t('draw.note')}</p>
  </section>
</div>

<style>
  .draw{display:grid;grid-template-columns:minmax(260px,340px) minmax(0,1fr);gap:var(--ui-space-xl) var(--ui-space-3xl);align-items:start}
  .pad-column{display:grid;gap:var(--ui-space-lg)}
  .results{min-inline-size:0}
  .pad{position:relative;aspect-ratio:1;border:1px solid var(--ui-color-border-strong);border-radius:var(--ui-radius-xl);background:var(--ui-color-surface-sunken);overflow:hidden}
  .pad::before,.pad::after{content:"";position:absolute;background:var(--ui-color-border);pointer-events:none}
  .pad::before{left:50%;top:14px;bottom:14px;width:1px}
  .pad::after{top:50%;left:14px;right:14px;height:1px}
  canvas{position:relative;z-index:1;display:block;width:100%;height:100%;touch-action:none;cursor:crosshair;color:var(--ui-color-ink)}
  .hint{position:absolute;left:0;right:0;bottom:16px;text-align:center;color:var(--ui-color-ink-muted);font-size:var(--ui-text-2xs);pointer-events:none}
  .tools{display:flex;align-items:center;gap:var(--ui-space-xs)}
  .strokes{margin-inline-start:auto}
  .keys{margin-top:var(--ui-space-md)}
  .note{margin-top:var(--ui-space-lg)}
  @media (max-width:1100px){.draw{grid-template-columns:minmax(0,440px)}}
  /* A phone keeps the candidates on screen beside the pad's last stroke. */
  @media (max-width:900px){.pad{inline-size:min(100%,38dvh);margin-inline:auto}.keys{display:none}}
</style>
