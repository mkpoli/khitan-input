<script>
  // One box for anything: pasted Khitan, a catalogue number, a code point, a reading, a meaning, a Chinese word.
  import { db } from '../lib/db.svelte.js'
  import { ix, lookup, matchedReading, searchReadings, searchWords } from '../lib/data.js'
  import { hasKhitan } from '../lib/script.js'
  import { route, setQuery } from '../lib/route.svelte.js'
  import { autofocus } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'
  import Tile from '../ui/Tile.svelte'
  import WordRow from '../ui/WordRow.svelte'

  let query = $state(route.q)
  const ready = $derived(db.status === 'ready')
  const q = $derived(query.trim())
  const pasted = $derived(ready && hasKhitan(q) ? [...q].map(ch => ix.byChar.get(ch)).filter(Boolean) : [])
  const direct = $derived(ready && q && !pasted.length ? lookup(q) : [])
  const graphemes = $derived(ready && q && !pasted.length ? [...direct, ...searchReadings(q).filter(g => !direct.includes(g))].slice(0, 60) : pasted)
  const words = $derived.by(() => {
    if (!ready || !q) return []
    if (pasted.length) {
      const key = pasted.map(g => g.char).join('')
      return ix.words.filter(w => w.x === key || (w.x && w.x.includes(key)))
    }
    return searchWords(q)
  })
  const EXAMPLES = ['aa', 'tuu', '339', 'U+18B01', '郎君', '檀', '馬']
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.find')}</h1>
    <p class="ui-page-intro">{t('find.intro')}</p>
  </header>
  <input class="ui-input" data-size="xl" data-primary value={query} spellcheck="false" autocomplete="off" autocapitalize="off"
    aria-label={t('find.label')} placeholder={t('find.placeholder')}
    oninput={(/** @type {Event & { currentTarget: HTMLInputElement }} */ event) => { query = event.currentTarget.value; setQuery(query) }} use:autofocus />

  {#if !q}
    <div class="start">
      <span class="ui-hint">{t('find.try')}</span>
      {#each EXAMPLES as example (example)}
        <button type="button" class="ui-chip" onclick={() => { query = example; setQuery(example) }}>{example}</button>
      {/each}
    </div>
  {:else if !ready}
    <p class="ui-empty">{t('common.loading')}</p>
  {:else if !graphemes.length && !words.length}
    <p class="ui-empty">{t('find.none')}</p>
  {:else}
    {#if graphemes.length}
      <div class="ui-section-head"><h2 class="ui-label">{t('nav.graphemes')}</h2><span class="ui-count">{graphemes.length}</span></div>
      <div class="ui-tiles" style:--ui-tile-size="66px">{#each graphemes as g, i (`${g.id}${i}`)}<Tile {g} note={pasted.length ? undefined : matchedReading(g, q)} />{/each}</div>
    {/if}
    {#if words.length}
      <div class="ui-section-head"><h2 class="ui-label">{t('nav.words')}</h2><span class="ui-count">{words.length}</span></div>
      <ul class="list">{#each words.slice(0, 80) as w, i (i)}<WordRow {w} />{/each}</ul>
    {/if}
  {/if}
</div>

<style>
  .start{display:flex;flex-wrap:wrap;align-items:center;gap:var(--ui-space-xs)}
  .list{display:grid;margin:0;padding:0;list-style:none}
</style>
