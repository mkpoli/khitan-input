<script>
  import seal from '../../data/seal/records.json' with { type: 'json' }
  import mappings from '../../data/seal/correspondences.json' with { type: 'json' }
  import { t } from '../lib/i18n.svelte.js'

  let { weight = $bindable(400) } = $props()
  const covers = seal.inscriptions.map(cover => ({
    id: cover.id,
    text: seal.forms.filter(form => form.inscription === cover.id).map(form => form.identification).join('')
  }))
  let sample = $state(covers.find(cover => cover.id === 'xuanyi')?.text ?? '')
  const covered = new Set([
    ...Object.values(mappings.blocks).map(block => block.character),
    ...Object.keys(mappings.unicode_aliases).map(code => String.fromCodePoint(parseInt(code.slice(2), 16)))
  ])
  let comparison = $derived(Array.from(sample, c => covered.has(c) || /\s/u.test(c) ? c : '□').join(''))
</script>

<section class="specimen" aria-labelledby="specimen-title">
  <div class="heading">
    <h2 id="specimen-title">Qingling Seal</h2>
    <div class="presets">
      {#each covers as cover (cover.id)}
        <button type="button" aria-pressed={sample === cover.text} onclick={() => sample = cover.text}>{t(cover.id === 'xuanyi' ? 'seal.xuanyi' : 'seal.daozong')}</button>
      {/each}
    </div>
  </div>
  <label class="editor">
    <span>{t('seal.sample')}</span>
    <textarea rows="1" spellcheck="false" bind:value={sample}></textarea>
  </label>
  <div class="proofs">
    <section class="proof">
      <h3>Qingling Seal</h3>
      <p class="qingling" style:font-weight={weight}>{comparison}</p>
    </section>
    <section class="proof">
      <h3><a href="https://www.babelstone.co.uk/Fonts/KhitanSmallSeal.html">BabelStone Khitan Small Seal</a></h3>
      <p class="babelstone">{comparison}</p>
    </section>
  </div>
  {#if comparison !== sample}<p class="missing">{t('seal.missing')}</p>{/if}
  <div class="axis">
    <label for="seal-weight">{t('seal.weight')}</label>
    <div class="control">
      <span aria-hidden="true">200</span>
      <input id="seal-weight" type="range" min="200" max="800" bind:value={weight} style:--fill={((weight - 200) / 6) + '%'} />
      <span aria-hidden="true">800</span>
    </div>
    <output for="seal-weight">{weight}</output>
  </div>
</section>

<style>
  .specimen{overflow:hidden;border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-xl);background:var(--ui-color-surface)}
  .heading,.axis{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;padding:1rem clamp(1rem,3vw,2rem)}
  .heading h2{margin:0;font:500 clamp(1.6rem,3vw,2.35rem)/1.15 var(--ui-font-serif)}
  .presets{display:flex;gap:.25rem}
  .presets button{border:1px solid transparent;border-radius:var(--ui-radius-pill);padding:.4rem .85rem;color:var(--ui-color-ink-soft);background:transparent;cursor:pointer}
  .presets button:hover{background:var(--ui-color-surface-hover)}
  .presets button[aria-pressed="true"]{background:var(--ui-color-accent-soft);color:var(--ui-color-accent-ink)}
  .editor{display:grid;gap:.4rem;margin:0 clamp(1rem,3vw,2rem) 1rem}
  .editor span,.proof h3,.axis label{font-size:var(--ui-text-sm);font-weight:600}
  textarea{box-sizing:border-box;width:100%;min-height:2.8rem;resize:vertical;padding:.5rem .8rem;border:1px solid var(--ui-color-control-border);border-radius:var(--ui-radius-sm);background:var(--ui-color-canvas);color:var(--ui-color-ink);font:1.3rem/1.45 'Noto Serif Khitan Small Script',serif}
  .proofs{display:grid;grid-template-columns:1fr 1fr;border-block:1px solid var(--ui-color-border)}
  .proof{min-width:0;padding:1rem clamp(1rem,3vw,2rem) 1.5rem}
  .proof+.proof{border-inline-start:1px solid var(--ui-color-border)}
  .proof h3{margin:0 0 .75rem;color:var(--ui-color-ink-soft)}
  .proof p{margin:0;min-height:1.3em;white-space:pre-wrap;overflow-wrap:anywhere;font-size:clamp(2.25rem,4.4vw,4rem);line-height:1.35}
  .qingling{font-family:'Qingling Seal',serif}
  .babelstone{font-family:'BabelStone Khitan Small Seal',serif}
  .missing{padding-inline:1rem;color:var(--ui-color-ink-soft);font-size:var(--ui-text-sm)}
  .axis{display:grid;grid-template-columns:auto minmax(0,1fr) 3.4rem;background:var(--ui-color-surface-sunken)}
  .control{display:flex;align-items:center;gap:.8rem;font-size:var(--ui-text-xs);color:var(--ui-color-ink-soft);font-variant-numeric:tabular-nums}
  .axis output{padding:.2rem .4rem;text-align:center;border:1px solid var(--ui-color-border);border-radius:var(--ui-radius-sm);color:var(--ui-color-accent-ink);background:var(--ui-color-surface);font-variant-numeric:tabular-nums}
  input[type=range]{appearance:none;min-width:0;width:100%;height:2.75rem;margin:0;cursor:pointer;background:transparent;accent-color:var(--ui-color-accent);--rail:linear-gradient(to right,var(--ui-color-accent) var(--fill),var(--ui-color-control-border) var(--fill))}
  input::-webkit-slider-runnable-track{height:6px;background:var(--rail);border-radius:9px}
  input::-moz-range-track{height:6px;background:var(--rail);border-radius:9px}
  input::-webkit-slider-thumb{appearance:none;box-sizing:border-box;width:22px;height:22px;margin-top:-8px;background:var(--ui-color-surface);border:5px solid var(--ui-color-accent);border-radius:50%;box-shadow:var(--ui-shadow-1)}
  input::-moz-range-thumb{box-sizing:border-box;width:22px;height:22px;background:var(--ui-color-surface);border:5px solid var(--ui-color-accent);border-radius:50%;box-shadow:var(--ui-shadow-1)}
  @media(max-width:640px){.proofs{grid-template-columns:1fr}.proof+.proof{border-inline-start:0;border-block-start:1px solid var(--ui-color-border)}.axis{gap:.6rem}.control{gap:.45rem}}
  @media(forced-colors:active){input[type=range]{appearance:auto}input::-webkit-slider-thumb{appearance:auto}}
</style>
