<script>
  // Interlinear sentences: blocks, transcription, gloss, translation and where each stands.
  import { db } from '../lib/db.svelte.js'
  import { ix } from '../lib/data.js'
  import { put } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'
  import Block from '../ui/Block.svelte'

  const ready = $derived(db.status === 'ready')
  /** @param {any} example */
  const textOf = example => example.lines.flatMap((/** @type {any} */ l) => l.w).map((/** @type {any} */ w) => w.x).filter(Boolean).join(' ')
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.sentences')}</h1>
    <p class="ui-page-intro">{t('sentences.intro')}</p>
  </header>
  {#if !ready}<p class="ui-empty">{t('common.loading')}</p>{:else}
    {#each ix.examples as e (e.n)}
      <article class="example">
        <header class="meta"><span class="ui-label">({e.n})</span> <span>{e.cit}</span>
          <button class="ui-button" data-size="sm" data-variant="quiet" type="button" onclick={() => put(textOf(e))}>{t('card.add')}</button></header>
        {#each e.lines as line, i (i)}
          <div class="words">
            {#each line.w as w, j (j)}
              <div class="word"><Block spelling={w.sp} size={26} /><span class="said">{w.t ?? ''}</span></div>
            {/each}
          </div>
          {#if !line.w.every((/** @type {any} */ w) => w.t)}<p class="said latin">{line.tr}</p>{/if}
          {#if line.gl}<p class="gloss">{line.gl}</p>{/if}
        {/each}
        <p class="translation">{e.tr}</p>
        {#if e.note}<p class="ui-hint">{e.note}</p>{/if}
      </article>
    {/each}
    <p class="ui-hint">{t('sentences.source')}</p>
  {/if}
</div>

<style>
  .example{display:grid;gap:var(--ui-space-xs);padding-block:var(--ui-space-lg);border-bottom:1px solid var(--ui-color-border)}
  .meta{display:flex;align-items:center;gap:var(--ui-space-sm);color:var(--ui-color-ink-soft);font-size:var(--ui-text-sm)}
  .words{display:flex;flex-wrap:wrap;gap:var(--ui-space-sm) var(--ui-space-md);align-items:flex-start}
  .word{display:grid;justify-items:center;gap:2px;font-size:var(--ui-text-sm)}
  .latin{font-size:var(--ui-text-sm)}
  .gloss{color:var(--ui-color-ink-muted);font-size:var(--ui-text-xs)}
  .translation{font-size:var(--ui-text-md);margin-top:var(--ui-space-2xs)}
</style>
