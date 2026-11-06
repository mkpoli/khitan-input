<script>
  // The large script has no Unicode encoding yet, so its characters stand on Private Use code points.
  import { db } from '../lib/db.svelte.js'
  import { ix } from '../lib/data.js'
  import { copy } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'

  let query = $state('')
  const ready = $derived(db.status === 'ready')
  const rows = $derived(!ready ? [] : ix.large.filter(r => !query.trim() || [r.r, r.c, r.m, r.pua].join(' ').toLowerCase().includes(query.trim().toLowerCase())))
  /** @param {string} pua */
  const glyphs = pua => (pua ?? '').split(' ').filter(Boolean).map(hex => String.fromCodePoint(parseInt(hex, 16))).join('')
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.large')}</h1>
    <p class="ui-page-intro">{t('large.intro')}</p>
  </header>
  <input class="ui-input" data-size="lg" data-primary bind:value={query} spellcheck="false" autocomplete="off" aria-label={t('large.label')} placeholder={t('large.placeholder')} />
  <div class="ui-table-wrap"><table class="ui-table">
    <thead><tr><th>{t('large.number')}</th><th>{t('large.glyph')}</th><th>{t('large.reconstruction')}</th><th>{t('large.chinese')}</th><th>{t('large.meaning')}</th><th>PUA</th></tr></thead>
    <tbody>
      {#each rows as r (r.n)}
        <tr><td>{r.n}</td><td><button class="glyph large-glyph" type="button" title={t('common.copy')} onclick={() => copy(glyphs(r.pua))}>{glyphs(r.pua)}</button></td><td class="said">{r.r}</td><td>{r.c ?? ''}</td><td>{r.m ?? ''}</td><td class="ui-mono">{r.pua}</td></tr>
      {/each}
    </tbody>
  </table></div>
  <p class="ui-hint">{t('large.source')}</p>
</div>

<style>
  .glyph{padding:0 var(--ui-space-xs);border:0;border-radius:var(--ui-radius-xs);background:none;color:inherit;font-size:30px;line-height:1.2}
  .glyph:hover{background:var(--ui-color-surface-hover)}
</style>
