<script>
  // A word in a list: its block, form and meaning, opening onto its evidence.
  import { put } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'
  import Block from './Block.svelte'

  /** @type {{ w: any }} */
  let { w } = $props()
  let open = $state(false)
  const spellings = $derived((w.sp ?? '').split('~').map((/** @type {string} */ s) => s.trim()))
  const scholar = $derived(t(`scholar.${w.src}`))
</script>

<li class="word">
  <div class="line">
    <span class="blocks">{#each spellings as sp, i (i)}<Block spelling={sp} size={22} />{/each}</span>
    <button class="main" type="button" aria-expanded={open} onclick={() => { open = !open }}>
      <span class="form said">{w.f ?? ''}</span>
      {#if w.h}<span class="han">{w.h}</span>{/if}
      {#if w.g}<span class="gloss">{w.g}</span>{/if}
      <span class="kind ui-hint">{t(`kind.${w.k}`)}</span>
    </button>
    {#if w.x}<button class="ui-button" data-size="icon-sm" data-variant="quiet" type="button" aria-label={t('card.add')} title={t('card.add')} onclick={() => put(`${w.x} `)}>+</button>{/if}
  </div>
  {#if open}
    <dl class="more">
      {#if w.pos}<dt>{t('word.pos')}</dt><dd>{w.pos}</dd>{/if}
      {#if w.sg}<dt>{t('word.segments')}</dt><dd class="said">{w.sg}</dd>{/if}
      {#if w.sec}<dt>{t('word.section')}</dt><dd>{w.sec}</dd>{/if}
      {#each w.rf ?? [] as [language, text], i (i)}<dt>{language}</dt><dd class="said">{text}</dd>{/each}
      {#each w.uses ?? [] as use, i (i)}<dt>{i ? '' : t('word.uses')}</dt><dd>{use}</dd>{/each}
      {#if w.at?.length}<dt>{t('word.attested')}</dt><dd>{w.at.join(', ')}</dd>{/if}
      {#if w.cf}<dt>Cf.</dt><dd>{w.cf.replace(/⟦[^⟧]*⟧/g, '□')}</dd>{/if}
      <dt>{t('word.source')}</dt><dd>{scholar}{w.p ? `, p.${w.p}` : ''}</dd>
    </dl>
  {/if}
</li>

<style>
  .word{border-bottom:1px solid var(--ui-color-border);padding-block:var(--ui-space-xs)}
  .line{display:flex;align-items:center;gap:var(--ui-space-md)}
  .blocks{display:flex;gap:var(--ui-space-xs);flex:none;min-inline-size:52px;justify-content:center}
  .main{flex:1;min-inline-size:0;display:flex;flex-wrap:wrap;align-items:baseline;gap:var(--ui-space-sm);padding:var(--ui-space-2xs) var(--ui-space-xs);border:0;border-radius:var(--ui-radius-sm);background:none;color:inherit;text-align:start;font:inherit}
  .main:hover{background:var(--ui-color-surface-hover)}
  .form{font-size:var(--ui-text-md)}
  .gloss{font-size:var(--ui-text-sm);color:var(--ui-color-ink-soft)}
  .kind{margin-inline-start:auto;font-size:var(--ui-text-2xs)}
  .more{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:2px var(--ui-space-md);margin:var(--ui-space-xs) 0 var(--ui-space-sm) 64px;font-size:var(--ui-text-xs)}
  .more dt{color:var(--ui-color-ink-muted)}
  .more dd{margin:0;overflow-wrap:anywhere}
</style>
