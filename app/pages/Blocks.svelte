<script>
  // The text being written as it would stand on stone: blocks down the column, columns right to left.
  import { text } from '../lib/text.svelte.js'
  import { parseWord } from '../lib/script.js'
  import { readingOf } from '../lib/data.js'
  import { db } from '../lib/db.svelte.js'
  import { put } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'
  import Block from '../ui/Block.svelte'

  const FILLER = '\u{16FE4}'
  const ready = $derived(db.status === 'ready')
  const lines = $derived(text.value.split('\n').map(line => line.split(/\s+/).filter(Boolean).map(parseWord)).filter(line => line.length))
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.blocks')}</h1>
    <p class="ui-page-intro">{t('blocks.intro')}</p>
  </header>
  <div class="tools">
    <button class="ui-button" data-size="sm" type="button" onclick={() => put(' ')}>{t('blocks.space')}</button>
    <button class="ui-button" data-size="sm" type="button" onclick={() => put(FILLER)}>{t('blocks.filler')}</button>
  </div>
  {#if !lines.length}
    <p class="ui-empty">{t('blocks.empty')}</p>
  {:else}
    <div class="stone" lang="zkt">
      {#each lines as line, l (l)}
        <div class="column">
          {#each line as word, w (w)}
            <div class="cell">
              <Block chars={word.chars} single={word.single} size={38} />
              {#if ready}<span class="said">{word.chars.map(ch => readingOf(ch) || '?').join('-')}</span>{/if}
            </div>
          {/each}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .tools{display:flex;gap:var(--ui-space-xs)}
  .stone{display:flex;flex-direction:row-reverse;justify-content:flex-start;gap:var(--ui-space-2xl);overflow-x:auto;padding:var(--ui-space-xl);border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-lg);background:var(--ui-color-surface)}
  .column{flex:none;display:flex;flex-direction:column;align-items:center;gap:var(--ui-space-lg);padding-inline:var(--ui-space-xs)}
  .cell{display:grid;justify-items:center;gap:2px}
  .cell .said{font-size:var(--ui-text-2xs);color:var(--ui-color-ink-muted)}
</style>
