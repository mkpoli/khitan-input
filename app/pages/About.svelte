<script>
  // Where every value comes from.
  import { db } from '../lib/db.svelte.js'
  import { ix } from '../lib/data.js'
  import { t } from '../lib/i18n.svelte.js'

  const ready = $derived(db.status === 'ready')
  const TIERS = ['stated', 'stated_tentative', 'stated_unattested', 'single_grapheme_word', 'aligned_spelling']
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.about')}</h1>
    <p class="ui-page-intro">{t('about.intro')}</p>
  </header>
  <section class="ui-section">
    <h2 class="ui-label">{t('about.tiers')}</h2>
    <dl class="tiers">{#each TIERS as tier (tier)}<dt>{t(`tier.${tier}`)}</dt><dd>{t(`tier.${tier}.note`)}</dd>{/each}</dl>
  </section>
  <section class="ui-section">
    <h2 class="ui-label">{t('about.sources')}</h2>
    {#if ready}
      <ul class="sources">
        {#each ix.sources as s (s.id)}
          <li><p>{#if s.u}<a href={s.u}>{s.c}</a>{:else}{s.c}{/if}</p>{#if s.t}<p class="ui-hint">{s.t}</p>{/if}{#if s.n}<p class="ui-hint">{s.n}</p>{/if}</li>
        {/each}
      </ul>
    {/if}
  </section>
</div>

<style>
  .tiers{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:var(--ui-space-xs) var(--ui-space-lg);margin:0;font-size:var(--ui-text-sm)}
  .tiers dt{font-weight:var(--ui-weight-semibold)}
  .tiers dd{margin:0;color:var(--ui-color-ink-soft)}
  .sources{display:grid;gap:var(--ui-space-md);margin:0;padding:0;list-style:none;font-size:var(--ui-text-sm)}
  .sources p{overflow-wrap:anywhere}
</style>
