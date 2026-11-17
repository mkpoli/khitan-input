<script>
  // The Jurchen side of the comparison: nine characters a cited figure sets beside Khitan large-script
  // forms, drawn here from BabelStone's Private Use glyphs and the Jurchen face, and the four
  // directions the figure leaves without a Khitan counterpart.
  import { t } from '../lib/i18n.svelte.js'

  /** The nine of Kiyose's figure, with the gloss it prints above them. */
  const NINE = [
    { gloss: '天', khitan: '\u{E000}', jurchen: '\u{18E16}', reading: 'abxa' },
    { gloss: '年', khitan: '\u{E018}', jurchen: '\u{19012}', reading: 'ania' },
    { gloss: '日', khitan: '\u{E0C9}', jurchen: '\u{18F7A}', reading: 'inəŋgi' },
    { gloss: '月', khitan: '\u{E0C6}', jurchen: '\u{190FA}', reading: 'bia' },
    { gloss: '龍', khitan: '\u{E0FF}', jurchen: '\u{18F65}', reading: 'mudu' },
    { gloss: '人', khitan: '\u{E00A}', jurchen: '\u{1906F}', reading: 'nialma' },
    { gloss: '聽', khitan: '\u{E47C}', jurchen: '\u{1907C}', reading: 'dondi' },
    { gloss: '中', khitan: '\u{E345}', jurchen: '\u{190FB}', reading: 'duli' },
    { gloss: '福', khitan: '\u{E034}', jurchen: '\u{19182}', reading: 'xutu' },
  ]

  /** The four directions as Kiyose writes them: a stem and a suffix, two characters in all. */
  const DIRECTIONS = [
    { gloss: '東', form: 'jule-ši' },
    { gloss: '西', form: 'fuli-ši' },
    { gloss: '南', form: 'fan-ti' },
    { gloss: '北', form: 'uli-ti' },
  ]
</script>

<article class="ui-page jurchen" data-width="narrow">
  <header class="ui-page-head">
    <h1 class="ui-page-title">{t('jurchen.title')}</h1>
    <p class="ui-page-intro">{t('jurchen.lead')}</p>
  </header>

  <section class="ui-section">
    <h2 class="ui-label">{t('jurchen.nineTitle')}</h2>
    <div class="ui-table-wrap"><table class="ui-table">
      <thead><tr><th>{t('jurchen.gloss')}</th><th>{t('jurchen.khitan')}</th><th>{t('jurchen.jurchen')}</th><th>{t('jurchen.reading')}</th></tr></thead>
      <tbody>
        {#each NINE as item (item.gloss)}
          <tr>
            <th scope="row" class="gloss">{item.gloss}</th>
            <td><span class="k-glyph">{item.khitan}</span></td>
            <td><span class="j-glyph">{item.jurchen}</span></td>
            <td class="said">{item.reading}</td>
          </tr>
        {/each}
      </tbody>
    </table></div>
    <p class="ui-hint">{t('jurchen.note')} <a href="https://www.chikyukotobamura.org/muse/wr_easia_9.html">{t('jurchen.figure')}</a></p>
  </section>

  <section class="ui-section">
    <h2 class="ui-label">{t('jurchen.directionsTitle')}</h2>
    <p class="ui-prose">{t('jurchen.directionsLead')}</p>
    <ul class="directions">
      {#each DIRECTIONS as item (item.gloss)}
        <li><span class="gloss">{item.gloss}</span><span class="said">{item.form}</span></li>
      {/each}
    </ul>
    <p class="ui-prose">{t('jurchen.directionsNote')}</p>
  </section>

  <section class="ui-section">
    <h2 class="ui-label">{t('jurchen.sources')}</h2>
    <ul class="sources">
      <li><a href="https://www.chikyukotobamura.org/muse/wr_easia_9.html">Kiyose Gizaburō Norifu, 「女真文字」, 地球ことば村, 2022</a></li>
      <li><a href="https://archive.org/details/Khitan-et-Jurchen-languages">Kane, <cite>The Sino-Jurchen Vocabulary of the Bureau of Interpreters</cite>, 1989, pp. 22–23</a></li>
      <li><a href="https://archive.org/download/Khitan-et-Jurchen-languages/%E5%A5%B3%E7%9C%9F%E8%AF%AD%E8%A8%80%E6%96%87%E5%AD%97%E7%A0%94%E7%A9%B6.pdf#page=67">Jin Guangping and Jin Qizong, 《女真語言文字研究》, 1980, pp. 56–57</a></li>
    </ul>
  </section>
</article>

<style>
  .jurchen{gap:var(--ui-space-2xl)}
  .gloss{font-family:var(--ui-font-serif);font-size:var(--ui-text-sm);font-weight:normal}
  .k-glyph{display:inline-block;inline-size:2em;margin-inline:-.5em;text-align:center;font-family:'BabelStone Khitan Large',serif;font-size:38px;line-height:1.15}
  .j-glyph{font-family:'Alari Xuwasun Jurchen',serif;font-size:38px;line-height:1.15}
  .ui-table{table-layout:fixed;inline-size:100%}
  .ui-table th{white-space:normal}
  .ui-table th:nth-child(1){inline-size:16%}
  .ui-table th:nth-child(2){inline-size:30%}
  .ui-table th:nth-child(3){inline-size:27%}
  .ui-table th:nth-child(4){inline-size:27%}
  .ui-table td,.ui-table th{padding-block:var(--ui-space-xs)}
  .directions{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--ui-space-xs);margin:0;padding:0;list-style:none;max-inline-size:640px}
  .directions li{display:flex;align-items:baseline;gap:var(--ui-space-2xs);padding-block:var(--ui-space-2xs);border-block-start:1px solid var(--ui-color-border)}
  .sources{display:grid;gap:var(--ui-space-xs);margin:0;padding:0;list-style:none;font-size:var(--ui-text-xs);line-height:1.5;color:var(--ui-color-ink-soft)}
  .sources a{color:inherit;text-underline-offset:2px}
  .ui-hint a{color:inherit;text-underline-offset:2px}
  @media (max-width:900px){.directions{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
