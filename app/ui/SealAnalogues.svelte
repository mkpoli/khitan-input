<script>
  import designs from '../../data/seal/font/analogues.json' with { type: 'json' }
  import { t } from '../lib/i18n.svelte.js'

  let { weight } = $props()
  /** @param {string} code */
  const char = code => String.fromCodePoint(parseInt(code.slice(2), 16))
</script>

<section class="ui-section">
  <h2 class="ui-label">{t('seal.proposed')}</h2>
  <p class="ui-hint">{t('seal.analogy')}</p>
  <table>
    <thead><tr><th scope="col">Zhuque Fangsong</th><th scope="col">Sealie</th><th scope="col">Noto Serif Khitan</th><th scope="col">Qingling Seal</th></tr></thead>
    <tbody>
      {#each designs as design (design.unicode)}
        <tr>
          <td><span class="zhuque">{design.han}</span></td>
          <td><span class="sealie">{char(design.smallSeal)}</span></td>
          <td><span class="regular">{char(design.unicode)}</span></td>
          <td><span class="qingling" style:font-weight={weight}>{char(design.unicode)}</span><small>{design.unicode} · {design.model}</small></td>
        </tr>
      {/each}
    </tbody>
  </table>
</section>

<style>
  @font-face{font-family:'Comparison Zhuque';src:url('/fonts/ComparisonZhuque.woff2') format('woff2');font-display:swap}
  @font-face{font-family:'Comparison Sealie';src:url('/fonts/ComparisonSealie.woff2') format('woff2');font-display:swap}
  table{width:100%;max-width:54rem;border-collapse:collapse;table-layout:fixed;text-align:center}
  th,td{padding:.65rem .25rem;border-bottom:1px solid var(--ui-color-border);vertical-align:middle}
  th{font-size:var(--ui-text-sm);color:var(--ui-color-ink-soft)}
  td span{display:block;font-size:clamp(2rem,5vw,3.8rem);line-height:1.3}
  td small{display:block;color:var(--ui-color-ink-soft);font-size:var(--ui-text-xs)}
  .zhuque{font-family:'Comparison Zhuque',serif}
  .sealie{font-family:'Comparison Sealie',serif}
  .regular{font-family:'Noto Serif Khitan Small Script',serif}
  .qingling{font-family:'Qingling Seal',serif}
</style>
