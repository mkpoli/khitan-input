<script>
  // Every grapheme, under Unicode's radical groups or in catalogue order.
  import { db } from '../lib/db.svelte.js'
  import { ix } from '../lib/data.js'
  import { t } from '../lib/i18n.svelte.js'
  import Tile from '../ui/Tile.svelte'

  let order = $state('radical')
  let filter = $state('all')
  const ready = $derived(db.status === 'ready')
  const list = $derived(!ready ? [] : ix.graphemes.filter(g => filter === 'all' || (filter === 'read' ? g.v : !g.v)))
  const groups = $derived.by(() => {
    if (order === 'number') {
      const numbered = list.filter(g => !g.id.startsWith('U+')).sort((a, b) => a.id.localeCompare(b.id))
      const unicode = list.filter(g => g.id.startsWith('U+')).sort((a, b) => a.cp.localeCompare(b.cp))
      return [[t('graphemes.catalogue'), numbered], [t('graphemes.unicodeOnly'), unicode]].filter(([, g]) => g.length)
    }
    /** @type {Map<string, any[]>} */
    const map = new Map()
    for (const g of list) {
      const key = !g.cp ? '~none' : g.rad ?? '~other'
      map.set(key, [...(map.get(key) ?? []), g])
    }
    /** @param {string} key */
    const name = key => key === '~none' ? t('graphemes.noCodePoint') : key === '~other' ? t('graphemes.other') : t('graphemes.radical', { n: Number(key.replace(/\D/g, '')) })
    return [...map].sort((a, b) => a[0].localeCompare(b[0])).map(([key, items]) => [name(key), items.sort((x, y) => (x.cp ?? '').localeCompare(y.cp ?? ''))])
  })
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.graphemes')}</h1>
    <p class="ui-page-intro">{t('graphemes.intro')}</p>
  </header>
  <div class="tools">
    <div class="ui-segmented" role="group" aria-label={t('graphemes.order')}>
      {#each [['radical', 'graphemes.byRadical'], ['number', 'graphemes.byNumber']] as [key, label] (key)}
        <button type="button" class="ui-chip" aria-pressed={order === key} onclick={() => { order = key }}>{t(label)}</button>
      {/each}
    </div>
    <div class="ui-segmented" role="group" aria-label={t('graphemes.filter')}>
      {#each [['all', 'graphemes.all'], ['read', 'graphemes.read'], ['unread', 'graphemes.unread']] as [key, label] (key)}
        <button type="button" class="ui-chip" aria-pressed={filter === key} onclick={() => { filter = key }}>{t(label)}</button>
      {/each}
    </div>
    <span class="ui-count">{list.length}</span>
  </div>
  {#if !ready}<p class="ui-empty">{t('common.loading')}</p>{/if}
  {#each groups as [name, items] (name)}
    <div class="ui-section-head"><h2 class="ui-label">{name}</h2><span class="ui-count">{items.length}</span></div>
    <div class="ui-tiles" style:--ui-tile-size="62px">{#each items as g (g.id)}<Tile {g} />{/each}</div>
  {/each}
</div>

<style>
  .tools{display:flex;flex-wrap:wrap;align-items:center;gap:var(--ui-space-md)}
  .ui-segmented{display:flex;gap:var(--ui-space-2xs)}
  .ui-chip[aria-pressed='true']{background:var(--ui-color-accent-soft);color:var(--ui-color-accent-ink);border-color:var(--ui-color-accent)}
</style>
