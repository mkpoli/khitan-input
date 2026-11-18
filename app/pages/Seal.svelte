<script>
  // The seal-script covers of the Qingling 哀册: two inscriptions, 46 blocks, no reading assigned.
  import seal from '../../data/seal/records.json' with { type: 'json' }
  import { t } from '../lib/i18n.svelte.js'

  /** @param {string} id */
  const blocks = id => seal.forms.filter(form => form.inscription === id)
  const xuanyi = seal.forms.filter(form => form.inscription === 'xuanyi')
  /** @param {string} id */
  const identified = id => blocks(id).filter(block => block.identification).length
</script>

<div class="ui-page" data-width="wide">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('nav.seal')}</h1>
    <p class="ui-page-intro">{t('seal.intro')}</p>
    <p class="method">{t('seal.method')}</p>
    <p class="ui-hint">{t('seal.ids')}</p>
  </header>

  {#each seal.inscriptions as inscription (inscription.id)}
    <section class="ui-section cover-section">
      <figure class="cover">
        <img src={inscription.image} width={inscription.image_width} height={inscription.image_height}
          alt={`${inscription.title} (${inscription.plate})`} decoding="async" />
        <figcaption class="ui-hint">
          <span>{inscription.plate} · {inscription.object} · {inscription.date}</span><br />
          {t('seal.figure')} <span class="credit">{inscription.source_record.author} · {inscription.source_record.licence}</span>
        </figcaption>
      </figure>

      <div class="record">
        <h2 class="title">{inscription.title}</h2>
        <p class="meta">
          {inscription.person} · {inscription.plate} · {inscription.date}
        </p>
        <p class="reading">
          <span class="ui-hint">{t('seal.firstLine')}</span>
          <span class="text">{inscription.reading}</span>
          <span class="ui-hint">({inscription.reading_source})</span>
        </p>
        <div class="counts">
          <span>{t('seal.blocks', { count: blocks(inscription.id).length })}</span>
          <span>{t('seal.columns', { count: inscription.columns })}</span>
          <span>{t('seal.rows', { count: inscription.rows })}</span>
          {#if identified(inscription.id)}
            <span>{identified(inscription.id)} {t('seal.identified')}</span>
          {:else}
            <span class="unknown">{t('seal.unidentified')}</span>
          {/if}
        </div>
        <ol class="blocks" style={`grid-template-columns:repeat(${inscription.columns}, minmax(0, 1fr))`}>
          {#each blocks(inscription.id) as block (block.id)}
            <li class="block" style={`grid-column:${inscription.columns - block.col + 1};grid-row:${block.row}`}
              title={`${block.id}: ${block.identification ?? t('seal.unidentified')}${block.unicode ? ` ${block.unicode}` : ''}`}>
              <span class="id">{block.id}</span>
              <span class="pos">{block.col}·{block.row}</span>
            </li>
          {/each}
        </ol>
        <p class="ui-hint">{t('seal.order')}</p>
      </div>
    </section>
  {/each}

  <section class="ui-section typeface">
    <div class="ui-section-head">
      <h2 class="ui-label">{t('seal.typeface')}</h2>
      <span class="ui-count">U+18B00–U+18CFF</span>
    </div>
    <p class="typeface-note">{t('seal.typeface.note')}</p>
    <div class="typeface-grid">
      {#each xuanyi as form (form.id)}
        <span class="typeface-cell">
          <span class="typeface-glyph" style={form.id === 'XY-05' ? 'font-feature-settings:"ss01" 1' : ''}>{form.identification}</span>
          <span class="typeface-code">{form.id} · {form.unicode}</span>
          <span class="typeface-normal">{form.identification}</span>
        </span>
      {/each}
    </div>
    <p class="ui-hint">
      <a href="/fonts/QinglingSeal-Regular.ttf" download>{t('seal.typeface.download')}</a> · CC BY-SA 4.0
      · <a href="https://github.com/iebb/sealie">Sealie</a> (OFL 1.1)
      · <a href="https://www.babelstone.co.uk/Fonts/KhitanSmallSeal.html">BabelStone Khitan Small Seal</a>
    </p>
  </section>

  <section class="ui-section">
    <h2 class="ui-label">{t('seal.sources')}</h2>
    <ul class="sources">
      {#each seal.sources as item (item.id)}
        <li>
          <p><a href={item.url}>{item.citation}</a></p>
          <p>{item.author} · {item.date} · {item.licence}{#if item.page} · <a href={item.page}>{t('seal.article')}</a>{/if}</p>
          <p class="ui-hint">{item.terms}</p>
        </li>
      {/each}
    </ul>
  </section>
</div>

<style>
  .cover-section{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:var(--ui-space-2xl);align-items:start}
  .cover{margin:0;display:flex;flex-direction:column;gap:var(--ui-space-xs)}
  .cover img{inline-size:100%;block-size:auto;border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-sm);background:#111}
  .cover figcaption{max-inline-size:60ch}
  .credit{white-space:nowrap}
  .record{display:flex;flex-direction:column;gap:var(--ui-space-sm);min-inline-size:0}
  .title{font-family:var(--ui-font-serif);font-size:var(--ui-text-lg);font-weight:var(--ui-weight-semibold);line-height:var(--ui-leading-tight)}
  .meta{color:var(--ui-color-ink-soft);font-size:var(--ui-text-sm)}
  .reading{display:flex;flex-wrap:wrap;align-items:baseline;gap:var(--ui-space-xs);font-size:var(--ui-text-sm)}
  .reading .text{font-family:var(--ui-font-serif);font-size:var(--ui-text-md);letter-spacing:.02em}
  .method{max-inline-size:66ch;color:var(--ui-color-ink-soft);font-size:var(--ui-text-sm);line-height:var(--ui-leading-loose)}
  .counts{display:flex;flex-wrap:wrap;gap:var(--ui-space-xs) var(--ui-space-md);color:var(--ui-color-ink-soft);font-size:var(--ui-text-xs);font-variant-numeric:tabular-nums}
  .counts .unknown{color:var(--ui-color-ink-muted)}
  .blocks{display:grid;grid-auto-rows:64px;gap:4px;margin:0;padding:0;list-style:none}
  .block{position:relative;display:flex;flex-direction:column;justify-content:space-between;padding:5px 7px;border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-xs);background:var(--ui-color-surface)}
  .block .id{color:var(--ui-color-ink-muted);font-size:10px;letter-spacing:.02em;font-variant-numeric:tabular-nums}
  .block .pos{font-size:15px;font-weight:var(--ui-weight-semibold);font-variant-numeric:tabular-nums;line-height:1}
  .typeface-note{max-inline-size:66ch;font-size:var(--ui-text-sm);line-height:var(--ui-leading-normal)}
  .typeface-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--ui-space-sm);max-inline-size:760px}
  .typeface-cell{display:flex;flex-direction:column;align-items:center;gap:var(--ui-space-xs);padding:var(--ui-space-md) 0;border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-xs)}
  .typeface-glyph{font-family:'Qingling Seal';font-size:76px;line-height:1}
  .typeface-code{color:var(--ui-color-ink-muted);font-size:11px;font-variant-numeric:tabular-nums}
  .typeface-normal{display:flex;align-items:baseline;gap:4px;font-family:'Noto Serif Khitan Small Script';font-size:22px;line-height:1}
  .sources{display:grid;gap:var(--ui-space-md);margin:0;padding:0;list-style:none;font-size:var(--ui-text-sm)}
  .sources p{overflow-wrap:anywhere}
  .sources p + p{margin-block-start:2px;color:var(--ui-color-ink-soft)}
  @media (max-width:900px){
    .cover-section{grid-template-columns:minmax(0,1fr)}
    .blocks{grid-auto-rows:56px}
    .typeface-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
    .typeface-glyph{font-size:64px}
  }
</style>
