<script>
  // The inscriptions behind the citations: an abbreviation such as D.CAL 53 points at a line of one of these.
  import { db } from '../lib/db.svelte.js'
  import { ix } from '../lib/data.js'
  import { t } from '../lib/i18n.svelte.js'

  let script = $state('small')
  const ready = $derived(db.status === 'ready')
  const rows = $derived(ready ? ix.documents.filter(d => d.s === script) : [])
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.documents')}</h1>
    <p class="ui-page-intro">{t('documents.intro')}</p>
  </header>
  <div class="tools">
    {#each ['small', 'large', 'chinese'] as key (key)}
      <button type="button" class="ui-chip" aria-pressed={script === key} onclick={() => { script = key }}>{t(`documents.${key}`)}</button>
    {/each}
    <span class="ui-count">{rows.length}</span>
  </div>
  <div class="ui-table-wrap"><table class="ui-table">
    <thead><tr><th>{t('documents.abbreviation')}</th><th>{t('documents.title')}</th><th>{t('documents.date')}</th><th>{t('documents.lines')}</th><th>{t('documents.page')}</th></tr></thead>
    <tbody>{#each rows as d (d.id)}<tr><td class="ui-mono">{d.a ?? ''}</td><td>{d.t}</td><td>{d.d ?? ''}</td><td>{d.n ?? ''}</td><td>{d.p ?? ''}</td></tr>{/each}</tbody>
  </table></div>
</div>

<style>
  .tools{display:flex;flex-wrap:wrap;align-items:center;gap:var(--ui-space-2xs)}
  .ui-chip[aria-pressed='true']{background:var(--ui-color-accent-soft);color:var(--ui-color-accent-ink);border-color:var(--ui-color-accent)}
</style>
