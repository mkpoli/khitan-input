<script>
  // The text being written. Every finder inserts here at the caret; it can also be typed or pasted into.
  import { text, setText, remember, asCodePoints, asReadings } from '../lib/text.svelte.js'
  import { copy } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'

  /** @type {HTMLTextAreaElement | null} */
  let field = $state(null)
  const count = $derived([...text.value].filter(ch => !/\s/.test(ch)).length)

  // The font's tall line box only counts once it has arrived.
  let fontReady = $state(false)
  document.fonts.load("20px 'Noto Serif Khitan Small Script'", '\u{18BFA}').then(() => { fontReady = true })

  // Grow with the text up to two lines of blocks.
  $effect(() => {
    void text.value
    void fontReady
    if (!field) return
    field.style.height = 'auto'
    field.style.height = `${Math.min(field.scrollHeight + 2, 190)}px`
  })

  $effect(() => {
    if (!field) return
    if (text.start >= 0 && document.activeElement === field) field.setSelectionRange(text.start, text.end)
  })
</script>

<section class="writing" aria-label={t('writing.label')}>
  <label class="ui-label writing-label" for="writing">{t('writing.text')}</label>
  <textarea id="writing" bind:this={field} class="ui-input writing-field" data-filled={count ? '' : undefined} rows="1" spellcheck="false" autocomplete="off"
    value={text.value} placeholder={t('writing.placeholder')}
    oninput={event => { setText(event.currentTarget.value); remember(event.currentTarget) }}
    onkeyup={event => remember(event.currentTarget)} onclick={event => remember(event.currentTarget)} onblur={event => remember(event.currentTarget)}></textarea>
  <div class="actions">
    {#if count}<span class="ui-count">{count}</span>{/if}
    <button class="ui-button" data-size="sm" type="button" disabled={!count} onclick={() => copy(text.value, t('writing.text'))}>{t('common.copy')}</button>
    <button class="ui-button" data-size="sm" data-variant="quiet" type="button" disabled={!count} onclick={() => copy(asCodePoints(text.value), t('writing.codePoints'))}>U+</button>
    <button class="ui-button" data-size="sm" data-variant="quiet" type="button" disabled={!count} onclick={() => copy(asReadings(text.value), t('writing.readings'))}>{t('writing.readings')}</button>
    <button class="ui-button" data-size="sm" data-variant="quiet" type="button" disabled={!text.value} onclick={() => { setText(''); text.start = text.end = -1 }}>{t('writing.clear')}</button>
  </div>
</section>

<style>
  .writing{position:sticky;top:var(--topbar-h);z-index:14;display:flex;align-items:center;gap:var(--ui-space-lg);padding:var(--ui-space-sm) var(--ui-space-2xl);background:var(--ui-color-surface);border-bottom:1px solid var(--ui-color-border)}
  .writing-label{flex:none}
  .writing-field{flex:1;min-inline-size:0;min-block-size:var(--ui-control-h-lg);padding:var(--ui-space-xs) var(--ui-space-lg);border-color:var(--ui-color-border);border-radius:var(--ui-radius-md);background:var(--ui-color-surface-sunken);font-size:24px;line-height:1.3;resize:none;overflow:auto}
  /* The font stacks a word into a block itself and its line box is four ems tall, so the field gives it room. */
  .writing-field[data-filled]{font-size:20px;line-height:normal}
  .writing-field::placeholder{font-size:var(--ui-text-md);color:var(--ui-color-ink-muted);line-height:2.1}
  .actions{display:flex;align-items:center;gap:var(--ui-space-2xs)}
  @media (max-width:900px){
    .writing{flex-wrap:wrap;gap:var(--ui-space-xs);padding:var(--ui-space-xs) var(--ui-space-lg)}
    .writing-label{display:none}
    .writing-field{flex-basis:100%;font-size:20px}
  }
</style>
