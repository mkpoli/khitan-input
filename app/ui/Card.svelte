<script>
  // Everything recorded about the open grapheme: how to use it, Otake's value, every other scholar's
  // value under their name, where the Unicode link came from, and the words it spells.
  import { db } from '../lib/db.svelte.js'
  import { ix, wordsWith } from '../lib/data.js'
  import { MARK, fromHex } from '../lib/script.js'
  import { link, route } from '../lib/route.svelte.js'
  import { ui, put, copy, choose } from '../lib/ui.svelte.js'
  import { t } from '../lib/i18n.svelte.js'
  import Block from './Block.svelte'

  const g = $derived(db.status === 'ready' ? ix.byId.get(route.g) : undefined)
  const otake = $derived((g?.rs ?? []).filter((/** @type {any} */ r) => r.s.startsWith('otake')))
  const others = $derived((g?.rs ?? []).filter((/** @type {any} */ r) => !r.s.startsWith('otake')))
  const words = $derived(g ? wordsWith(g.id) : [])
  const numbers = $derived(Object.entries(g?.num ?? {}).filter(([scheme]) => ['chinggeltei1985', 'chinggeltei2010', 'kane2009', 'n4725r'].includes(scheme)))
  const related = $derived((g?.rel ?? []).map((/** @type {[string, string]} */ [type, cp]) => ({ type, other: ix.byChar.get(fromHex(cp)) })).filter((/** @type {any} */ r) => r.other))

  /** A table or section as printed, or how many rows give this value. @param {any} r */
  const where = r => !r.l ? '' : /^\d/.test(r.l) ? ` ×${parseInt(r.l)}` : `, ${r.l}`

  /** @param {string} s */
  function sourceName(s) {
    if (s.startsWith('n4725r:')) return t(`scholar.${s.slice(7)}`)
    return t(`scholar.${s}`)
  }
</script>

{#if ui.sheet}
  <div class="sheetbar"><button class="ui-button" data-variant="quiet" data-size="sm" type="button" onclick={() => { ui.sheet = false }}>{t('card.back')}</button></div>
{/if}

{#if !g}
  <div class="blank">
    <p class="ui-script blank-glyph" aria-hidden="true">{MARK}</p>
    <p>{t('card.blank')}</p>
  </div>
{:else}
  <article class="record">
    <header class="head">
      <div class="frame">{#if g.char}<span class="ui-script">{g.char}</span>{:else}<span class="nocp">{t('card.noCodePoint')}</span>{/if}</div>
      <div class="facts">
        {#if g.cp}<button class="cp ui-mono" type="button" title={t('card.copyCodePoint')} onclick={() => copy(`U+${g.cp}`)}>U+{g.cp}</button>{/if}
        {#if g.v}<p class="value said">{g.v}</p>{/if}
        {#if !g.id.startsWith('U+')}<p class="meta">{t('card.number', { id: g.id })}</p>{/if}
        {#if g.ty}<p class="meta">{t('card.type', { type: g.ty })}</p>{/if}
      </div>
    </header>

    {#if g.char}
      <div class="use">
        <button class="ui-button" data-variant="primary" data-size="sm" type="button" onclick={() => put(g.char)}>{t('card.add')}</button>
        <button class="ui-button" data-size="sm" type="button" onclick={() => copy(g.char)}>{t('common.copy')}</button>
      </div>
    {/if}

    {#if g.st === 'variant'}<p class="ui-hint note">{t('card.variantOf', { id: g.tg })}</p>{/if}
    {#if g.jur}<p class="ui-hint note">{t('card.jurchen')}</p>{/if}

    <section>
      <h3 class="ui-label">{t('card.otake')}</h3>
      {#if otake.length}
        <table class="values"><tbody>
          {#each otake as r, i (i)}
            <tr><td class="said">{r.v}</td><td class="where">{t(`tier.${r.t}`)}<br>{sourceName(r.s)}{where(r)}{r.p ? `, p.${r.p}` : ''}</td></tr>
          {/each}
        </tbody></table>
      {:else}<p class="ui-hint">{t('card.noReading')}</p>{/if}
    </section>

    {#if others.length}
      <section>
        <h3 class="ui-label">{t('card.others')}</h3>
        <table class="values"><tbody>
          {#each others as r, i (i)}
            <tr><td class="said" class:gloss={r.k === 'semantic'}>{r.v}</td><td class="where">{sourceName(r.s)}{r.k === 'mnemonic' ? ` · ${t('card.mnemonic')}` : ''}</td></tr>
          {/each}
        </tbody></table>
      </section>
    {/if}

    {#if related.length}
      <section>
        <h3 class="ui-label">{t('card.related')}</h3>
        <div class="rel">{#each related as r, i (i)}<button class="ui-button" data-size="sm" type="button" onclick={() => choose(r.other.id)}>{t(`relation.${r.type === '~' ? 'variant' : r.type === '>' ? 'dotted' : r.type === '<' ? 'undotted' : 'part'}`)} <span class="ui-script">{r.other.char}</span></button>{/each}</div>
      </section>
    {/if}

    {#if words.length}
      <section>
        <h3 class="ui-label">{t('card.words', { count: words.length })}</h3>
        <ul class="words">
          {#each words.slice(0, 14) as w, i (i)}
            <li><Block spelling={w.sp.split('~')[0]} size={20} /> <span class="said">{w.f}</span> <span class="ui-hint">{w.g ?? w.h ?? ''}</span></li>
          {/each}
        </ul>
      </section>
    {/if}

    <section>
      <h3 class="ui-label">{t('card.link')}</h3>
      {#if g.um}<p class="ui-hint">{t(`link.${g.um}`)}{g.uc && g.uc !== 'high' ? ` ${t(`confidence.${g.uc}`)}` : ''}</p>{:else if g.id.startsWith('U+')}<p class="ui-hint">{t('link.unicodeOnly')}</p>{:else}<p class="ui-hint">{t('link.none')}{g.cand ? ` ${t('link.candidate', { cp: g.cand })}` : ''}</p>{/if}
      {#if numbers.length}<p class="ui-hint">{numbers.map(([s, n]) => `${t(`number.${s}`)} ${n}`).join(' · ')}</p>{/if}
    </section>

    <footer class="ui-hint credit"><a href={link('about')}>{t('nav.about')}</a></footer>
  </article>
{/if}

<style>
  .sheetbar{position:sticky;top:0;z-index:2;padding:var(--ui-space-xs) var(--ui-space-lg);background:var(--ui-color-surface);border-bottom:1px solid var(--ui-color-border)}
  .blank{display:grid;gap:var(--ui-space-md);justify-items:center;text-align:center;padding:72px var(--ui-space-3xl);color:var(--ui-color-ink-soft)}
  .blank-glyph{font-size:88px;line-height:1;color:var(--ui-color-border-strong)}
  .record{display:block;padding:var(--ui-space-2xl) var(--ui-space-2xl) var(--ui-space-5xl)}
  .head{display:flex;align-items:center;gap:var(--ui-space-xl);padding-bottom:var(--ui-space-xl)}
  .frame{display:grid;place-items:center;flex:none;inline-size:112px;block-size:112px;border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-lg);background:var(--ui-color-surface-sunken)}
  .frame :global(.ui-script){font-size:68px;line-height:1}
  .nocp{padding:var(--ui-space-sm);font-size:var(--ui-text-2xs);color:var(--ui-color-ink-muted);text-align:center}
  .facts{display:grid;gap:var(--ui-space-2xs);min-inline-size:0}
  .cp{justify-self:start;margin-inline-start:-6px;padding:2px 6px;border:0;border-radius:var(--ui-radius-xs);background:none;color:var(--ui-color-ink-soft);font-size:var(--ui-text-sm)}
  .cp:hover{background:var(--ui-color-surface-hover)}
  .value{font-size:var(--ui-text-2xl,26px);line-height:1.15}
  .meta{color:var(--ui-color-ink-muted);font-size:var(--ui-text-xs)}
  .use{display:flex;gap:var(--ui-space-xs);padding-bottom:var(--ui-space-xl)}
  .note{padding-bottom:var(--ui-space-md)}
  section{display:grid;gap:var(--ui-space-sm);padding-block:var(--ui-space-xl);border-top:1px solid var(--ui-color-border)}
  .values{border-collapse:collapse;inline-size:100%}
  .values td{padding:var(--ui-space-2xs) var(--ui-space-sm) var(--ui-space-2xs) 0;vertical-align:baseline}
  .values tr + tr{border-top:1px solid var(--ui-color-border)}
  .values .said{font-size:var(--ui-text-md);white-space:nowrap}
  .values .gloss{font-family:var(--ui-font-sans);font-size:var(--ui-text-xs);white-space:normal}
  .where{color:var(--ui-color-ink-muted);font-size:var(--ui-text-2xs);line-height:1.45}
  .rel{display:flex;flex-wrap:wrap;gap:var(--ui-space-xs)}
  .words{display:grid;gap:var(--ui-space-xs);margin:0;padding:0;list-style:none;font-size:var(--ui-text-sm)}
  .words li{display:flex;align-items:center;gap:var(--ui-space-sm)}
  .credit{font-size:var(--ui-text-2xs)}
</style>
