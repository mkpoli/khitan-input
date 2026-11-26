<script>
  // Seals with a face in the Khitan large script, in the wording of West's survey.
  import survey from '../../data/seal/large/west2012.json' with { type: 'json' }
  import { t } from '../lib/i18n.svelte.js'

  let kind = $state('ninefold')
  const seals = $derived(survey.seals.filter(seal => seal.kind === kind))
  const characters = survey.characters.filter(row => row.standard)
  /** Text cut into runs, so that Private Use characters take the large-script face. @param {string} text */
  const runs = text => text.split(/([-]+)/).filter(Boolean).map(run => ({ run, khitan: /[-]/.test(run) }))
</script>

{#snippet said(/** @type {string | undefined} */ text)}
  {#each runs(text ?? '') as part, n (n)}{#if part.khitan}<span class="large-glyph">{part.run}</span>{:else}{part.run}{/if}{/each}
{/snippet}

<section class="ui-section" id="large">
  <div class="ui-section-head">
    <h2 class="ui-label">{t('seal.large.title')}</h2>
    <span class="ui-count">{seals.length}</span>
  </div>
  <p class="ui-hint">{t('seal.large.intro')}</p>
  <div class="ui-segmented" role="radiogroup" aria-label={t('seal.large.kind')}>
    {#each ['ninefold', 'other'] as key (key)}
      <label class="ui-segment"><input type="radio" name="large-seal-kind" value={key} bind:group={kind} /><span class="ui-segment-face">{t(`seal.large.${key}`)}</span></label>
    {/each}
  </div>
  <div class="ui-table-wrap"><table class="ui-table seals" lang="en">
    <thead><tr><th>{t('seal.large.seal')}</th><th>{t('documents.place')}</th><th>{t('documents.held')}</th><th>{t('seal.large.inscription')}</th><th>{t('seal.large.reading')}</th></tr></thead>
    <tbody>
      {#each seals as seal (seal.id)}
        <tr>
          <th scope="row"><a href={seal.url}>{seal.id}</a>{#if seal.plate}<span class="plate">{seal.plate}</span>{/if}</th>
          <td>{seal.found ?? ''}</td>
          <td>{seal.held ?? ''}</td>
          <td>
            {#if seal.inscription}<p>{seal.inscription}</p>{/if}
            {#if seal.description}<p class="ui-hint">{@render said(seal.description)}</p>{/if}
            {#if seal.remark}<p><q>{@render said(seal.remark)}</q></p>{/if}
          </td>
          <td>{#if seal.reading}<q>{@render said(seal.reading)}</q>{/if}</td>
        </tr>
      {/each}
    </tbody>
  </table></div>

  <div class="ui-section-head">
    <h3 class="ui-label">{t('seal.large.characters')}</h3>
    <span class="ui-count">{characters.length}</span>
  </div>
  <div class="ui-table-wrap"><table class="ui-table" lang="en">
    <thead><tr><th>{t('seal.large.standard')}</th><th>{t('seal.large.meaning')}</th></tr></thead>
    <tbody>
      {#each characters as row, n (n)}
        <tr><td class="form">{@render said(row.standard)}</td><td>{@render said(row.meaning)}</td></tr>
      {/each}
    </tbody>
  </table></div>
  <p class="ui-hint"><a href={survey.source.url}>{survey.source.author}, {survey.source.title}, {survey.source.site}, {survey.source.date}</a></p>
</section>

<style>
  .seals :where(th, td){vertical-align:top}
  .seals tbody th{white-space:nowrap;text-align:start}
  .seals td{min-inline-size:9rem}
  .seals td:nth-child(4){min-inline-size:20rem}
  .seals td:nth-child(5){min-inline-size:14rem}
  .plate{display:block;inline-size:9rem;color:var(--ui-color-ink-soft);font-size:var(--ui-text-xs);font-weight:var(--ui-weight-regular, 400);white-space:normal}
  p{margin:0}
  td p + p{margin-block-start:var(--ui-space-2xs)}
  .large-glyph{font-size:1.35em;line-height:1}
  .form{font-size:var(--ui-text-lg);white-space:nowrap}
</style>
