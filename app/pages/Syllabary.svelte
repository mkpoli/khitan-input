<script>
  // Otake's values as a grid: vowels across, codas down. Position gives the value, so a tile only names its number.
  import { db } from '../lib/db.svelte.js'
  import { ix } from '../lib/data.js'
  import { t } from '../lib/i18n.svelte.js'
  import Tile from '../ui/Tile.svelte'

  const VOWELS = ['əə', 'ə', 'a', 'o', 'u', 'ʊ', 'i', 'e', 'ä', 'ö', 'ü']
  const VC = [['d', 'ǰ', 'g', 'gʷ', 'γ', 'γʷ', 'b'], ['z', 'ž'], ['r', 'y', 'ğ', 'ğʷ', 'w'], ['n', 'ň', 'm'], ['l', 'ľ']]
  const VCC = ['nd', 'nz', 'ŋg', 'ŋgʷ', 'ŋγ', 'ŋγʷ', 'rd', 'rǰ', 'ld', 'lz', 'wǰ', 'yl']

  const ready = $derived(db.status === 'ready')
  const valued = $derived(ready ? ix.graphemes.filter(g => g.v && g.st !== 'uncatalogued') : [])

  /** @param {string} value */
  function split(value) {
    for (const vowel of VOWELS) if (value.startsWith(vowel)) return [vowel, value.slice(vowel.length)]
    return ['', value]
  }
  /** @param {any[]} list @param {string} coda */
  const row = (list, coda) => VOWELS.map(vowel => list.filter(g => { const [v, c] = split(g.v); return v === vowel && c === coda }))

  const vs = $derived(valued.filter(g => g.ty === 'V'))
  const vcs = $derived(valued.filter(g => g.ty === 'VC'))
  const vccs = $derived(valued.filter(g => g.ty === 'VCC'))
  const placed = $derived(new Set([...vs, ...vcs, ...vccs]))
  const rest = $derived(valued.filter(g => !placed.has(g)).sort((a, b) => a.v.localeCompare(b.v)))
  const none = $derived(ready ? ix.graphemes.filter(g => !g.v && g.st === 'current') : [])
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.syllabary')}</h1>
    <p class="ui-page-intro">{t('syllabary.intro')}</p>
  </header>
  {#if !ready}<p class="ui-empty">{t('common.loading')}</p>{:else}
    <div class="ui-section-head"><h2 class="ui-label">V</h2></div>
    <div class="ui-tiles" style:--ui-tile-size="62px">{#each vs as g (g.id)}<Tile {g} />{/each}</div>

    <div class="ui-section-head"><h2 class="ui-label">VC</h2></div>
    <div class="wrap"><table class="grid">
      <thead><tr><th></th>{#each VOWELS as v (v)}<th class="said">{v}-</th>{/each}</tr></thead>
      {#each VC as group, i (i)}
        <tbody>{#each group as coda (coda)}
          <tr><th class="said">-{coda}</th>{#each row(vcs, coda) as cell, c (c)}<td>{#each cell as g (g.id)}<Tile {g} note={g.id} />{/each}</td>{/each}</tr>
        {/each}</tbody>
      {/each}
    </table></div>

    <div class="ui-section-head"><h2 class="ui-label">VCC</h2></div>
    <div class="wrap"><table class="grid">
      <thead><tr><th></th>{#each VOWELS as v (v)}<th class="said">{v}-</th>{/each}</tr></thead>
      <tbody>{#each VCC as coda (coda)}
        <tr><th class="said">-{coda}</th>{#each row(vccs, coda) as cell, c (c)}<td>{#each cell as g (g.id)}<Tile {g} note={g.id} />{/each}</td>{/each}</tr>
      {/each}</tbody>
    </table></div>

    <div class="ui-section-head"><h2 class="ui-label">{t('syllabary.rest')}</h2><span class="ui-count">{rest.length}</span></div>
    <div class="ui-tiles" style:--ui-tile-size="66px">{#each rest as g (g.id)}<Tile {g} />{/each}</div>

    <div class="ui-section-head"><h2 class="ui-label">{t('syllabary.none')}</h2><span class="ui-count">{none.length}</span></div>
    <div class="ui-tiles" style:--ui-tile-size="56px">{#each none as g (g.id)}<Tile {g} note={g.id} />{/each}</div>
  {/if}
</div>

<style>
  .wrap{overflow-x:auto}
  .grid{border-collapse:collapse;font-size:var(--ui-text-sm)}
  .grid th{padding:var(--ui-space-2xs) var(--ui-space-xs);font-weight:var(--ui-weight-medium);color:var(--ui-color-ink-soft);text-align:center;white-space:nowrap}
  .grid td{min-inline-size:50px;padding:2px;border:1px solid var(--ui-color-border);vertical-align:top;text-align:center;background:var(--ui-color-surface)}
  .grid tbody + tbody{border-top:2px solid var(--ui-color-border-strong)}
  .grid td :global(.ui-tile){inline-size:48px;block-size:auto;min-block-size:0;padding:2px;border:0;background:none;display:inline-grid;justify-items:center}
  .grid td :global(.ui-tile:hover){background:var(--ui-color-surface-hover)}
  .grid td :global(.ui-script){font-size:24px}
  .grid td :global(.ui-tile-note){font-size:9px;font-family:var(--ui-font-mono);color:var(--ui-color-ink-muted)}
</style>
