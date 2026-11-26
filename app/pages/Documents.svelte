<script>
  // The corpus of inscriptions, and the ones behind the citations: an abbreviation such as D.CAL 53 points at a line of one of the latter.
  import { db } from '../lib/db.svelte.js'
  import { ix } from '../lib/data.js'
  import { i18n, t } from '../lib/i18n.svelte.js'

  const COMMONS = 'https://commons.wikimedia.org/wiki/File:'
  let view = $state('corpus')
  let script = $state('large')
  let kind = $state('monument')
  const ready = $derived(db.status === 'ready')
  const scripts = $derived(view === 'corpus' ? ['large', 'small'] : ['small', 'large', 'chinese'])
  const chosen = $derived(scripts.includes(script) ? script : scripts[0])
  const zh = $derived(i18n.locale.startsWith('zh'))
  const source = $derived(ready ? ix.sources.find(s => s.id === 'wikipedia_inscriptions') : null)
  const corpus = $derived(ready && view === 'corpus' ? ix.inscriptions.filter(r => r.s === chosen && r.k === kind) : [])
  const cited = $derived(ready && view === 'cited' ? ix.documents.filter(d => d.s === chosen) : [])
  /** The row's text in the reader's language, English where the Chinese list has none. @param {any} row @param {string} field */
  const say = (row, field) => (zh && row[field + 'z']) || row[field + 'e'] || ''
  /** The language of that text. @param {any} row @param {string} field */
  const tongue = (row, field) => zh && row[field + 'z'] ? 'zh' : 'en'
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.documents')}</h1>
    <p class="ui-page-intro">{t(view === 'corpus' ? 'documents.corpus.intro' : 'documents.intro')}</p>
  </header>
  <div class="tools">
    <div class="ui-segmented" role="radiogroup" aria-label={t('documents.view')}>
      {#each ['corpus', 'cited'] as key (key)}
        <label class="ui-segment"><input type="radio" name="documents-view" value={key} bind:group={view} /><span class="ui-segment-face">{t(`documents.${key}`)}</span></label>
      {/each}
    </div>
    <div class="ui-chip-row">
      {#each scripts as key (key)}
        <button type="button" class="ui-chip" aria-pressed={chosen === key} onclick={() => { script = key }}>{t(`documents.${key}`)}</button>
      {/each}
    </div>
    {#if view === 'corpus'}
      <div class="ui-chip-row">
        {#each ['monument', 'other', 'seal'] as key (key)}
          <button type="button" class="ui-chip" aria-pressed={kind === key} onclick={() => { kind = key }}>{t(`documents.${key}`)}</button>
        {/each}
      </div>
    {/if}
    <span class="ui-count">{view === 'corpus' ? corpus.length : cited.length}</span>
  </div>
  {#if view === 'corpus'}
    <div class="ui-table-wrap"><table class="ui-table corpus">
      <thead><tr><th>{t('documents.title')}</th><th>{t('documents.date')}</th><th>{t('documents.place')}</th><th>{t('documents.found')}</th><th>{t('documents.held')}</th><th>{t('documents.description')}</th></tr></thead>
      <tbody>
        {#each corpus as r (r.id)}
          <tr>
            <th scope="row">
              {#if r.nz}<span class="name" lang="zh">{r.nz}</span>{/if}
              <span class="name" class:second={r.nz} lang="en">{r.ne}</span>
              {#if r.img}<a class="image" href={COMMONS + encodeURIComponent(r.img.replaceAll(' ', '_'))}>{t('documents.image')}</a>{/if}
            </th>
            <td class="num">{r.d ?? ''}</td>
            <td lang={tongue(r, 'p')}>{say(r, 'p')}</td>
            <td class="found" lang={tongue(r, 'f')}>{say(r, 'f')}</td>
            <td lang={tongue(r, 'h')}>{say(r, 'h')}</td>
            <td>
              {#if say(r, 'd')}<p lang={tongue(r, 'd')}>{say(r, 'd')}</p>{/if}
              {#if r.note}<p class="ui-hint" lang="en">{r.note}</p>{/if}
              {#if say(r, 'rf')}
                <details>
                  <summary>{t('documents.references')} <span class="ui-count">{say(r, 'rf').length}</span></summary>
                  <ul lang={tongue(r, 'rf')}>{#each say(r, 'rf') as ref (ref.c)}<li>{#if ref.u}<a href={ref.u}>{ref.c}</a>{:else}{ref.c}{/if}</li>{/each}</ul>
                </details>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table></div>
    {#if source}<p class="ui-hint source"><a href={source.u}>{source.c}</a> {source.t}</p>{/if}
  {:else}
    <div class="ui-table-wrap"><table class="ui-table">
      <thead><tr><th>{t('documents.abbreviation')}</th><th>{t('documents.title')}</th><th>{t('documents.date')}</th><th>{t('documents.lines')}</th><th>{t('documents.page')}</th></tr></thead>
      <tbody>{#each cited as d (d.id)}<tr><td class="ui-mono">{d.a ?? ''}</td><td>{d.t}</td><td>{d.d ?? ''}</td><td>{d.n ?? ''}</td><td>{d.p ?? ''}</td></tr>{/each}</tbody>
    </table></div>
  {/if}
</div>

<style>
  .tools{display:flex;flex-wrap:wrap;align-items:center;gap:var(--ui-space-sm) var(--ui-space-md)}
  .ui-chip[aria-pressed='true']{background:var(--ui-color-accent-soft);color:var(--ui-color-accent-ink);border-color:var(--ui-color-accent)}
  .corpus :where(th, td){vertical-align:top}
  .corpus tbody th{min-inline-size:14rem;max-inline-size:24rem;text-align:start}
  .corpus td{min-inline-size:8rem}
  .corpus td:last-child{min-inline-size:18rem}
  .corpus .num{min-inline-size:0;white-space:nowrap;font-variant-numeric:tabular-nums}
  .corpus .found{min-inline-size:4rem;max-inline-size:10rem;font-variant-numeric:tabular-nums}
  .name{display:block}
  @media (max-width:640px){.corpus tbody th{min-inline-size:9rem}}
  .name.second{color:var(--ui-color-ink-soft);font-size:var(--ui-text-xs);font-weight:var(--ui-weight-regular, 400)}
  .image{font-size:var(--ui-text-xs);font-weight:var(--ui-weight-regular, 400)}
  .corpus p{margin:0}
  .corpus p + p,.corpus details{margin-block-start:var(--ui-space-2xs)}
  .corpus summary{inline-size:fit-content;color:var(--ui-color-ink-soft);font-size:var(--ui-text-xs);cursor:pointer}
  .corpus details ul{display:grid;gap:var(--ui-space-2xs);margin:var(--ui-space-2xs) 0 0;padding-inline-start:var(--ui-space-md);color:var(--ui-color-ink-soft);font-size:var(--ui-text-xs);overflow-wrap:anywhere}
  .source{overflow-wrap:anywhere}
</style>
