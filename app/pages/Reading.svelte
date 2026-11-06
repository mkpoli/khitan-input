<script>
  // An input method over readings. A hyphen or space writes the first candidate and starts the next
  // segment, so a segmented form such as (ə)b-uu can be typed straight through.
  import { db } from '../lib/db.svelte.js'
  import { searchReadings } from '../lib/data.js'
  import { fold } from '../lib/script.js'
  import { route, setQuery } from '../lib/route.svelte.js'
  import { put, autofocus, choose } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'

  let query = $state(route.q)
  /** @type {HTMLInputElement | null} */
  let input = $state(null)
  const LETTERS = ['ə', 'ɵ', 'ʊ', 'ä', 'ö', 'ü', 'ı', 'ǰ', 'č', 'š', 'ž', 'ň', 'ľ', 'ŋ', 'γ', 'χ', 'ğ', 'ʷ']
  const ready = $derived(db.status === 'ready')
  const hits = $derived(ready && query.trim() ? searchReadings(query).filter(g => g.char).slice(0, 18) : [])

  /** The value that matched, which may not be the primary one. @param {any} g */
  function matched(g) {
    const key = fold(query.trim())
    const hit = (g.rs ?? []).find((/** @type {any} */ r) => r.k === 'phonetic' && fold(r.v) === key) ?? (g.rs ?? []).find((/** @type {any} */ r) => r.k === 'phonetic' && fold(r.v).startsWith(key))
    return hit?.v ?? g.v ?? ''
  }

  /** @param {any} g */
  function pick(g) {
    put(g.char)
    query = ''
    setQuery('')
    input?.focus()
  }

  /** @param {KeyboardEvent & { currentTarget: HTMLInputElement }} event */
  function keys(event) {
    if ((event.key === ' ' || event.key === '-' || event.key === 'Enter') && hits.length) { event.preventDefault(); pick(hits[0]) }
    else if (/^[1-9]$/.test(event.key) && hits[Number(event.key) - 1]) { event.preventDefault(); pick(hits[Number(event.key) - 1]) }
    else if (event.key === ' ' && !query) { event.preventDefault(); put(' ') }
    else if (event.key === 'Escape') { query = ''; setQuery('') }
  }

  /** @param {string} letter */
  function letter(letter) {
    query += letter
    setQuery(query)
    input?.focus()
  }
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.reading')}</h1>
    <p class="ui-page-intro">{t('reading.intro')}</p>
  </header>
  <input bind:this={input} class="ui-input said" data-size="xl" data-primary value={query} spellcheck="false" autocomplete="off" autocapitalize="off"
    aria-label={t('reading.label')} placeholder={t('reading.placeholder')}
    oninput={(/** @type {Event & { currentTarget: HTMLInputElement }} */ event) => { query = event.currentTarget.value; setQuery(query) }} onkeydown={keys} use:autofocus />
  <div class="letters">{#each LETTERS as l (l)}<button type="button" class="ui-chip said" onclick={() => letter(l)}>{l}</button>{/each}</div>
  {#if query.trim() && ready}
    {#if hits.length}
      <ol class="candidates">
        {#each hits as g, i (g.id)}
          <li><button type="button" class="candidate" onclick={() => pick(g)} ondblclick={() => choose(g.id)}>
            <span class="n">{i < 9 ? i + 1 : ''}</span><span class="ui-script">{g.char}</span><span class="said">{matched(g)}</span><span class="id ui-hint">{g.id.startsWith('U+') ? g.cp : g.id}</span>
          </button></li>
        {/each}
      </ol>
    {:else}<p class="ui-empty">{t('find.none')}</p>{/if}
  {/if}
</div>

<style>
  .letters{display:flex;flex-wrap:wrap;gap:var(--ui-space-2xs)}
  .candidates{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:var(--ui-space-2xs);margin:0;padding:0;list-style:none}
  .candidate{display:flex;align-items:center;gap:var(--ui-space-sm);inline-size:100%;padding:var(--ui-space-xs) var(--ui-space-sm);border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-sm);background:var(--ui-color-surface);color:inherit;font:inherit;text-align:start}
  .candidate:hover{background:var(--ui-color-surface-hover)}
  .n{color:var(--ui-color-ink-muted);font-size:var(--ui-text-xs);inline-size:1em}
  .candidate :global(.ui-script){font-size:30px;line-height:1.1}
  .id{margin-inline-start:auto;font-size:var(--ui-text-2xs)}
</style>
