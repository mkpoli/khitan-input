<script>
  // One written word: graphemes in rows of two, an odd last one centred. The font stacks a typed word the
  // same way; laying the rows out here lets a grapheme with no code point stand in the block by its number.
  import { blockRows } from '../lib/script.js'
  import { ix } from '../lib/data.js'

  /** @type {{ spelling?: string, chars?: string[], single?: boolean, size?: number }} */
  let { spelling = '', chars, single = false, size = 26 } = $props()

  const items = $derived(chars
    ? chars.map(ch => ({ ch, label: '' }))
    : spelling.split(/\s+/).filter(Boolean).map(id => ({ ch: ix.byId.get(id)?.char ?? '', label: id })))
  const rows = $derived(blockRows(items, single))
</script>

<span class="block" style:--size="{size}px" lang="zkt">
  {#each rows as row, r (r)}
    <span class="row" class:lone={row.length === 1}>
      {#each row as item, i (i)}
        {#if item.ch}<span class="ui-script">{item.ch}</span>{:else}<span class="missing" title={item.label}>{item.label.startsWith('x') ? '?' : item.label}</span>{/if}
      {/each}
    </span>
  {/each}
</span>

<style>
  .block{display:inline-grid;gap:0;justify-items:center;vertical-align:middle;font-size:var(--size);line-height:1}
  .row{display:flex;justify-content:center}
  .row :global(.ui-script){line-height:1.05}
  .missing{display:grid;place-items:center;inline-size:1em;block-size:1em;font-family:var(--ui-font-mono);font-size:.34em;color:var(--ui-color-ink-muted);border:1px dashed var(--ui-color-border-strong)}
</style>
