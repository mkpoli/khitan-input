<script>
  // The frame: the bar with the finders, the text being written, the finder of the page, and the card
  // of the open grapheme beside it (a sheet over it on a phone).
  import { db, load } from './lib/db.svelte.js'
  import { route, go, PAGES } from './lib/route.svelte.js'
  import { ui, toast, applyTheme } from './lib/ui.svelte.js'
  import { MARK } from './lib/script.js'
  import { t } from './lib/i18n.svelte.js'
  import Writing from './ui/Writing.svelte'
  import SettingsRows from './ui/SettingsRows.svelte'
  import Card from './ui/Card.svelte'
  import Find from './pages/Find.svelte'
  import Syllabary from './pages/Syllabary.svelte'
  import Graphemes from './pages/Graphemes.svelte'
  import Draw from './pages/Draw.svelte'
  import Reading from './pages/Reading.svelte'
  import Words from './pages/Words.svelte'
  import Sentences from './pages/Sentences.svelte'
  import Blocks from './pages/Blocks.svelte'
  import Large from './pages/Large.svelte'
  import Documents from './pages/Documents.svelte'
  import About from './pages/About.svelte'

  load()
  applyTheme()

  let settingsOpen = $state(false)
  const FULL = new Set(['about', 'documents', 'large'])

  $effect(() => {
    const entry = PAGES.find(p => p.path === route.page)
    document.title = entry && entry.path ? `${t(entry.label)} · ${t('app.name')}` : t('app.name')
  })

  /** @param {MouseEvent} event @param {string} page */
  function nav(event, page) {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.button !== 0) return
    event.preventDefault()
    go(page)
  }

  /** @param {KeyboardEvent} event */
  function keys(event) {
    const typing = /** @type {HTMLElement} */ (event.target).closest('input, textarea')
    if (event.key === '/' && !typing) {
      const input = /** @type {HTMLElement | null} */ (document.querySelector('[data-primary]'))
      if (input) { event.preventDefault(); input.focus() }
    }
    if (event.key === 'Escape' && (ui.sheet || settingsOpen)) {
      event.preventDefault()
      ui.sheet = false
      settingsOpen = false
    }
  }
</script>

<!-- Capture, so a page sees whether Escape already closed something. -->
<svelte:window onkeydowncapture={keys} />

<div class="shell">
  <header class="top">
    <a class="mark" href="/" onclick={event => nav(event, '')} aria-label={t('app.home')}>
      <span class="badge" aria-hidden="true"><span class="ui-script">{MARK}</span></span>
      <span class="name">{t('app.name')}</span>
    </a>
    <nav class="finders" aria-label={t('nav.label')}>
      {#each PAGES as page (page.path)}
        <a href="/{page.path}" class:on={route.page === page.path} aria-current={route.page === page.path ? 'page' : undefined}
          title={t(page.hint)} onclick={event => nav(event, page.path)}>{t(page.label)}</a>
      {/each}
    </nav>
    <div class="aside">
      <div class="settings">
        <button class="ui-button" data-variant="quiet" data-size="icon" type="button" aria-label={t('settings.label')} title={t('settings.label')}
          aria-expanded={settingsOpen} onclick={() => { settingsOpen = !settingsOpen }}>
          <svg viewBox="0 0 20 20" width="17" height="17" aria-hidden="true"><path d="M4 7h10M18 7h2M4 17h4M12 17h8M16 5v4M10 15v4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>
        </button>
        {#if settingsOpen}<div class="settings-pop ui-popover" role="dialog" aria-label={t('settings.label')}><SettingsRows /></div>{/if}
      </div>
    </div>
  </header>

  <Writing />

  {#if db.status === 'failed'}
    <p class="fault">{t('app.failed')}</p>
  {:else}
    <div class="body" class:full={FULL.has(route.page)}>
      <main class="finder">
        {#if route.page === ''}<Find />
        {:else if route.page === 'syllabary'}<Syllabary />
        {:else if route.page === 'graphemes'}<Graphemes />
        {:else if route.page === 'draw'}<Draw />
        {:else if route.page === 'reading'}<Reading />
        {:else if route.page === 'words'}<Words />
        {:else if route.page === 'sentences'}<Sentences />
        {:else if route.page === 'blocks'}<Blocks />
        {:else if route.page === 'large'}<Large />
        {:else if route.page === 'documents'}<Documents />
        {:else}<About />{/if}
        <footer class="foot ui-hint">
          <a href="/documents" onclick={event => nav(event, 'documents')}>{t('nav.documents')}</a> ·
          <a href="/about" onclick={event => nav(event, 'about')}>{t('nav.about')}</a>
        </footer>
      </main>
      {#if !FULL.has(route.page)}
        <aside class="card" class:open={ui.sheet} aria-label={t('card.label')}><Card /></aside>
      {/if}
    </div>
  {/if}

  <nav class="tabs" aria-label={t('nav.label')}>
    {#each PAGES as page (page.path)}
      <a href="/{page.path}" class:on={route.page === page.path} onclick={event => nav(event, page.path)}>{t(page.label)}</a>
    {/each}
  </nav>

  <div class="toast" role="status" aria-live="polite">{#if toast.message}<span class="ui-toast">{toast.message}</span>{/if}</div>
</div>

<style>
  .shell{min-block-size:100dvh;display:flex;flex-direction:column}
  .top{position:sticky;top:0;z-index:var(--ui-z-chrome);display:flex;align-items:center;gap:var(--ui-space-xl);block-size:var(--topbar-h);padding-inline:var(--ui-space-2xl);background:var(--ui-color-surface);border-bottom:1px solid var(--ui-color-border)}
  .mark{display:flex;align-items:center;gap:var(--ui-space-sm);color:var(--ui-color-ink);text-decoration:none}
  .badge{display:grid;place-items:center;inline-size:30px;block-size:30px;border-radius:var(--ui-radius-sm);background:var(--ui-color-accent);color:var(--ui-color-on-accent);font-size:21px}
  .name{font-family:var(--ui-font-serif);font-size:17px;font-weight:var(--ui-weight-semibold);letter-spacing:.005em;white-space:nowrap}
  .finders{align-self:stretch;display:flex;align-items:stretch;gap:2px;min-inline-size:0;overflow-x:auto;scrollbar-width:none}
  .finders::-webkit-scrollbar{display:none}
  .finders a{position:relative;display:flex;align-items:center;padding:0 var(--ui-space-sm);color:var(--ui-color-ink-soft);text-decoration:none;font-size:var(--ui-text-sm);font-weight:var(--ui-weight-medium);white-space:nowrap}
  .finders a:hover{color:var(--ui-color-ink);background:var(--ui-color-surface-hover)}
  .finders a.on{color:var(--ui-color-ink);font-weight:var(--ui-weight-semibold)}
  .finders a.on::after{content:'';position:absolute;inset-inline:var(--ui-space-sm);bottom:0;block-size:2px;background:var(--ui-color-accent)}
  .aside{margin-inline-start:auto;display:flex;align-items:center;gap:var(--ui-space-2xs)}
  @media (max-width:900px){
  }
  .settings{position:relative}
  .settings-pop{position:absolute;inset-inline-end:0;inset-block-start:calc(100% + var(--ui-space-sm));z-index:var(--ui-z-menu);inline-size:360px;padding:var(--ui-space-2xs) var(--ui-space-lg) var(--ui-space-sm)}

  .body{flex:1;display:grid;grid-template-columns:minmax(0,1fr) 400px;align-items:start}
  .body.full{grid-template-columns:minmax(0,1fr)}
  .finder{min-inline-size:0;padding:var(--ui-space-3xl) var(--ui-space-4xl) 72px}
  .card{position:sticky;top:var(--topbar-h);block-size:calc(100dvh - var(--topbar-h));overflow:auto;border-inline-start:1px solid var(--ui-color-border);background:var(--ui-color-surface);overscroll-behavior:contain}
  .fault{margin:64px auto;max-inline-size:36em;color:var(--ui-color-danger)}
  .foot{margin-top:var(--ui-space-4xl);font-size:var(--ui-text-2xs);color:var(--ui-color-ink-soft)}
  .foot a{color:inherit;text-underline-offset:2px}
  .tabs{display:none}

  .toast{position:fixed;left:50%;bottom:var(--ui-space-3xl);transform:translateX(-50%);z-index:var(--ui-z-toast);pointer-events:none}


  @media (max-width:1180px){
    .top{gap:var(--ui-space-md);padding-inline:var(--ui-space-xl)}
    .finders a{padding-inline:var(--ui-space-xs);font-size:var(--ui-text-xs)}
    .finders a.on::after{inset-inline:var(--ui-space-xs)}
  }
  /* A tablet keeps every finder: the bar takes a second row, and its rule runs the width of the
     page like the row above. The sticky chrome below it follows the new height. */
  @media (min-width:901px) and (max-width:1180px){
    .shell{--topbar-h:96px}
    .top{flex-wrap:wrap;gap:0 var(--ui-space-xl);padding-inline:var(--ui-space-xl);block-size:var(--topbar-h)}
    .mark,.aside{block-size:55px}
    .finders{order:3;flex:0 0 100%;block-size:40px;border-top:1px solid var(--ui-color-border)}
    .finders a{padding-inline:var(--ui-space-sm);font-size:var(--ui-text-sm)}
    .finders a.on::after{inset-inline:var(--ui-space-sm)}
  }
  @media (max-width:900px){
    .shell{--topbar-h:54px}
    .top{gap:var(--ui-space-sm);padding-inline:var(--ui-space-lg)}
    .finders{display:none}
    .settings-pop{display:none}
    .aside{gap:2px}
    .body{grid-template-columns:minmax(0,1fr)}
    .finder{padding:var(--ui-space-xl) var(--ui-space-lg) 96px}
    .card{position:fixed;inset:0;block-size:100dvh;z-index:var(--ui-z-modal);border:0;transform:translateY(100%);transition:transform var(--ui-duration) var(--ui-ease);visibility:hidden}
    .card.open{transform:none;visibility:visible}
    .name{display:none}
    .tabs{position:fixed;inset-inline:0;bottom:0;z-index:var(--ui-z-chrome);display:flex;overflow-x:auto;scrollbar-width:none;gap:2px;padding:var(--ui-space-xs) var(--ui-space-sm) calc(var(--ui-space-xs) + env(safe-area-inset-bottom));background:var(--ui-color-surface);border-top:1px solid var(--ui-color-border)}
    .tabs a{flex:0 0 auto;padding:9px 4px;border:0;border-radius:var(--ui-radius-sm);text-align:center;color:var(--ui-color-ink-soft);background:none;text-decoration:none;font-size:var(--ui-text-xs);font-weight:var(--ui-weight-medium);white-space:nowrap}
    .tabs a.on{background:var(--ui-color-accent-soft);color:var(--ui-color-accent-ink)}
    .toast{bottom:calc(76px + env(safe-area-inset-bottom))}
  }
  @media (prefers-reduced-motion:reduce){.card{transition:none}}
</style>

