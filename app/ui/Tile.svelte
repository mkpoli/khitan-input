<script>
  // A grapheme as a tile: a click opens its record, a double click writes it.
  import { route } from '../lib/route.svelte.js'
  import { choose, put } from '../lib/ui.svelte.js'

  /** @type {{ g: any, note?: string }} */
  let { g, note } = $props()
  const shown = $derived(note ?? g.v ?? '—')
</script>

<button type="button" class="ui-tile" data-open={route.g === g.id ? '' : undefined} title={g.id}
  onclick={() => choose(g.id)} ondblclick={() => put(g.char)}>
  {#if g.char}<span class="ui-script">{g.char}</span>{:else}<span class="none">{g.id}</span>{/if}
  <span class="ui-tile-note said">{shown}</span>
</button>

<style>
  .ui-tile :global(.ui-script){font-size:30px;line-height:1.15}
  .ui-tile[data-open]{background:var(--ui-color-accent-soft)}
  .ui-tile-note{font-size:var(--ui-text-2xs);white-space:nowrap}
  .none{font-family:var(--ui-font-mono);font-size:var(--ui-text-xs);color:var(--ui-color-ink-muted)}
</style>
