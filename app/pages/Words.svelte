<script>
  // Attested words: cognates, Chinese loans, rhyme words and forms cited in the running text.
  import { db } from '../lib/db.svelte.js'
  import { searchWords } from '../lib/data.js'
  import { route, setQuery } from '../lib/route.svelte.js'
  import { autofocus } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'
  import WordRow from '../ui/WordRow.svelte'

  let query = $state(route.q)
  let kind = $state('')
  let limit = $state(100)
  const ready = $derived(db.status === 'ready')
  const hits = $derived(ready ? searchWords(query, kind) : [])
  $effect(() => { void query; void kind; limit = 100 })
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.words')}</h1>
    <p class="ui-page-intro">{t('words.intro')}</p>
  </header>
  <input class="ui-input" data-size="lg" data-primary value={query} spellcheck="false" autocomplete="off"
    aria-label={t('words.label')} placeholder={t('words.placeholder')}
    oninput={(/** @type {Event & { currentTarget: HTMLInputElement }} */ event) => { query = event.currentTarget.value; setQuery(query) }} use:autofocus />
  <div class="tools">
    {#each ['', 'cognate', 'loan', 'rhyme', 'form'] as key (key)}
      <button type="button" class="ui-chip" aria-pressed={kind === key} onclick={() => { kind = key }}>{t(key ? `kind.${key}` : 'graphemes.all')}</button>
    {/each}
    <span class="ui-count">{hits.length}</span>
  </div>
  {#if !ready}<p class="ui-empty">{t('common.loading')}</p>
  {:else if !hits.length}<p class="ui-empty">{t('find.none')}</p>
  {:else}
    <ul class="list">{#each hits.slice(0, limit) as w, i (`${w.k}${w.f}${i}`)}<WordRow {w} />{/each}</ul>
    {#if hits.length > limit}<button class="ui-button" type="button" onclick={() => { limit += 200 }}>{t('common.more')}</button>{/if}
  {/if}
</div>

<style>
  .tools{display:flex;flex-wrap:wrap;align-items:center;gap:var(--ui-space-2xs)}
  .ui-chip[aria-pressed='true']{background:var(--ui-color-accent-soft);color:var(--ui-color-accent-ink);border-color:var(--ui-color-accent)}
  .list{display:grid;margin:0;padding:0;list-style:none}
</style>
