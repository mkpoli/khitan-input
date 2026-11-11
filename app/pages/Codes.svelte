<script>
  // Every mapped character in block order, with the counts the catalogue adds up to.
  import { db } from '../lib/db.svelte.js'
  import { ix } from '../lib/data.js'
  import { copy } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'
  import { BLOCK_START, BLOCK_END, COLUMNS, FILLER, PAGE_SIZE, codeChart, codePointLabel, rangeLabel } from '../lib/code-chart.js'

  let at = $state(0)
  /** @type {HTMLElement | null} */
  let top = $state(null)

  const ready = $derived(db.status === 'ready')
  const chart = $derived(ready ? codeChart(ix.graphemes) : null)
  const current = $derived(chart ? chart.pages[at] : null)

  const percent = (/** @type {number} */ value, /** @type {number} */ total) =>
    total ? Math.round(value / total * 1000) / 10 : 0
  const percentLabel = (/** @type {number} */ value) => `${value.toFixed(1).replace(/\.0$/, '')}%`

  /** @param {string} label @param {number} value @param {number} total @param {string} [note] */
  function count(label, value, total, note = '') {
    return { label, note, display: String(value), percent: percent(value, total) }
  }
  /** @param {string} label @param {number} value @param {number} total @param {string} [note] */
  function ratio(label, value, total, note = '') {
    return { label, note, display: `${value} / ${total}`, percent: percent(value, total) }
  }

  const panels = $derived.by(() => {
    if (!chart) return []
    const all = chart.graphemes
    const mapped = chart.codePoints
    return [
      {
        title: t('codes.inventory'),
        rows: [
          count(t('codes.graphemes'), chart.graphemes, all),
          count(t('codes.codePoints'), chart.codePoints, all),
          count(t('graphemes.noCodePoint'), chart.withoutCodePoint, all),
        ],
      },
      {
        title: t('codes.block'),
        rows: [
          ratio(rangeLabel({ start: BLOCK_START, end: BLOCK_END }), chart.block, BLOCK_END - BLOCK_START + 1),
          ratio(codePointLabel(FILLER), chart.filler, 1, t('codes.filler')),
        ],
      },
      {
        title: t('codes.status'),
        rows: [
          count(t('codes.current'), chart.status.current ?? 0, all),
          count(t('codes.variant'), chart.status.variant ?? 0, all),
          count(t('codes.unicodeOnly'), chart.status.unicode ?? 0, all),
          count(t('codes.uncatalogued'), chart.status.uncatalogued ?? 0, all),
        ],
      },
      {
        title: t('codes.confidence'),
        rows: [
          count(t('codes.high'), chart.confidence.high, mapped),
          count(t('codes.medium'), chart.confidence.medium, mapped),
          count(t('codes.none'), chart.confidence.none, mapped),
        ],
      },
    ]
  })

  /** @param {number} delta */
  function turn(delta) {
    if (!chart) return
    at = Math.max(0, Math.min(chart.pages.length - 1, at + delta))
    top?.scrollIntoView({ block: 'start' })
  }
</script>

<div class="ui-page codes" data-width="wide">
  <header class="ui-page-head head">
    <h1 class="ui-page-title">{t('nav.codes')}</h1>
    <div class="chips">
      <span class="chip"><strong class="ui-num">{chart?.codePoints ?? '—'}</strong> <span class="chip-label">{t('codes.codePoints')}</span></span>
      <span class="chip"><strong class="ui-num">{chart?.graphemes ?? '—'}</strong> <span class="chip-label">{t('codes.graphemes')}</span></span>
    </div>
  </header>

  {#if !chart || !current}
    <p class="ui-empty">{t('common.loading')}</p>
  {:else}
    <div class="stats">
      {#each panels as panel (panel.title)}
        <section class="panel">
          <h2 class="ui-label">{panel.title}</h2>
          <div class="rows">
            {#each panel.rows as row (row.label)}
              <div class="stat">
                <div class="stat-head">
                  <span class="stat-label">{row.label}{#if row.note}<span class="stat-note">{row.note}</span>{/if}</span>
                  <span class="stat-value ui-num">{row.display}</span>
                  <span class="stat-pct ui-num">{percentLabel(row.percent)}</span>
                </div>
                <div class="track" aria-hidden="true"><span class="fill" style:inline-size={`${row.percent}%`}></span></div>
              </div>
            {/each}
          </div>
        </section>
      {/each}
    </div>

    <section class="chart" bind:this={top}>
      <div class="chart-head">
        <h2 class="ui-label range-label">{rangeLabel(current)}</h2>
        <span class="ui-count">{current.filled} / {PAGE_SIZE}</span>
        <button class="ui-chip filler-copy" type="button" title={t('common.copy')} onclick={() => copy(String.fromCodePoint(FILLER))}>
          {t('codes.filler')} <span class="ui-mono">{codePointLabel(FILLER)}</span>
        </button>
      </div>

      <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
      <div class="scroll" role="region" tabindex="0" aria-label={t('codes.page', { page: at + 1, pages: chart.pages.length })}>
        <div class="cells" style={`--columns:${COLUMNS}`}>
          {#each current.cells as g, i (i)}
            {#if g}
              <button class="cell" class:no-glyph={!g.drawn} type="button" title={t('common.copy')} onclick={() => copy(g.char || String.fromCodePoint(parseInt(g.cp, 16)))}>
                {#if g.drawn}<span class="ui-script glyph">{g.char}</span>{/if}
                <span class="code">{codePointLabel(parseInt(g.cp, 16))}</span>
              </button>
            {:else}
              <span class="cell empty" aria-hidden="true"></span>
            {/if}
          {/each}
        </div>
      </div>

      <div class="pager">
        <button class="ui-button" data-size="sm" type="button" disabled={at === 0} onclick={() => turn(-1)}>{t('codes.previous')}</button>
        <span class="ui-count" aria-live="polite">{at + 1} / {chart.pages.length}</span>
        <button class="ui-button" data-size="sm" type="button" disabled={at === chart.pages.length - 1} onclick={() => turn(1)}>{t('codes.next')}</button>
      </div>
    </section>
  {/if}
</div>

<style>
  .codes{gap:var(--ui-space-2xl)}
  .head{flex-direction:row;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:var(--ui-space-lg)}
  .chips{display:flex;flex-wrap:wrap;gap:var(--ui-space-xs)}
  .chip{display:inline-flex;align-items:baseline;gap:var(--ui-space-xs);padding:var(--ui-space-xs) var(--ui-space-lg);border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-pill);background:var(--ui-color-surface)}
  .chip strong{font-family:var(--ui-font-serif);font-size:var(--ui-text-xl);font-weight:var(--ui-weight-semibold);line-height:1;font-variant-numeric:tabular-nums}
  .chip-label{color:var(--ui-color-ink-muted);font-size:var(--ui-text-xs)}

  .stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--ui-space-xl) var(--ui-space-4xl)}
  .panel{display:grid;align-content:start;gap:var(--ui-space-md);padding-block-start:var(--ui-space-md);border-top:1px solid var(--ui-color-border-strong)}
  .rows{display:grid;gap:var(--ui-space-sm)}
  .stat{display:grid;gap:5px}
  .stat-head{display:flex;align-items:baseline;gap:var(--ui-space-sm);min-inline-size:0}
  .stat-label{display:flex;align-items:baseline;gap:var(--ui-space-xs);min-inline-size:0;overflow:hidden;color:var(--ui-color-ink-soft);font-size:var(--ui-text-sm);white-space:nowrap;text-overflow:ellipsis}
  .stat-note{color:var(--ui-color-ink-muted);font-size:var(--ui-text-2xs)}
  .stat-value{margin-inline-start:auto;color:var(--ui-color-ink);font-size:var(--ui-text-sm);font-weight:var(--ui-weight-medium);white-space:nowrap}
  .stat-pct{min-inline-size:3.1em;color:var(--ui-color-ink-muted);font-size:var(--ui-text-xs);text-align:end;white-space:nowrap}
  .track{overflow:hidden;block-size:4px;border-radius:var(--ui-radius-pill);background:var(--ui-color-surface-sunken)}
  .fill{display:block;block-size:100%;border-radius:inherit;background:var(--ui-color-accent)}

  .chart{display:flex;flex-direction:column;gap:var(--ui-space-md);scroll-margin-block-start:calc(var(--topbar-h) + var(--ui-space-2xl))}
  .chart-head{display:flex;align-items:baseline;flex-wrap:wrap;gap:var(--ui-space-sm)}
  .range-label{font-family:var(--ui-font-mono);font-size:var(--ui-text-xs);letter-spacing:0;text-transform:none}
  .filler-copy{margin-inline-start:auto;gap:var(--ui-space-xs);white-space:nowrap}
  .scroll{overflow-x:auto;padding-block-end:var(--ui-space-xs)}
  .cells{display:grid;grid-template-columns:repeat(var(--columns),minmax(0,1fr));gap:3px;min-inline-size:640px}
  .cell{display:grid;grid-template-rows:1fr auto;place-items:center;gap:2px;min-inline-size:0;min-block-size:64px;padding:var(--ui-space-xs) 2px var(--ui-space-2xs);border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-xs);background:var(--ui-color-surface);color:var(--ui-color-ink);font:inherit;line-height:1}
  button.cell{cursor:pointer;transition:background-color var(--ui-duration-fast) var(--ui-ease),border-color var(--ui-duration-fast) var(--ui-ease)}
  button.cell:hover{border-color:var(--ui-color-accent);background:var(--ui-color-accent-soft)}
  button.cell:active{background:var(--ui-color-surface-active)}
  .cell .glyph{font-family:var(--ui-font-script);font-size:clamp(20px,2.6vw,30px);line-height:1}
  .cell .code{color:var(--ui-color-ink-muted);font-family:var(--ui-font-mono);font-size:clamp(7px,.78vw,9px);line-height:1;white-space:nowrap}
  .cell.empty{border-style:dashed;background:var(--ui-color-surface-sunken)}
  .no-glyph{border-style:dashed;background:var(--ui-color-surface-sunken)}
  .pager{display:flex;align-items:center;justify-content:flex-end;gap:var(--ui-space-sm)}
  .pager .ui-count{min-inline-size:3.4em;text-align:center}

  @media (max-width:760px){
    .stats{grid-template-columns:minmax(0,1fr)}
    .cells{min-inline-size:600px;gap:2px}
    .cell{min-block-size:56px}
  }
</style>
