<script>
  // The logo as a select of the input sites.
  import { tick } from 'svelte'
  import { t } from '../lib/i18n.svelte.js'

  /** @type {{ home: (event: MouseEvent) => unknown, children: import('svelte').Snippet }} */
  let { home, children } = $props()

  const uid = $props.id()
  const SITES = [
    { id: 'khitan', href: '/', logo: '/favicon.svg', name: 'app.name' },
    { id: 'tangut', href: 'https://tangut.mkpo.li/', logo: '/sites/tangut.svg', name: 'app.sites.tangut' },
    { id: 'jurchen', href: 'https://jurchen.mkpo.li/', logo: '/sites/jurchen.svg', name: 'app.sites.jurchen' },
    { id: 'ids', href: 'https://ids.mkpo.li/', logo: '/sites/ids.svg', name: 'app.sites.ids' },
  ]

  let open = $state(false)
  /** @type {HTMLDivElement | null} */
  let root = $state(null)
  /** @type {HTMLButtonElement | null} */
  let trigger = $state(null)
  const items = () => /** @type {HTMLElement[]} */ ([...(root?.querySelectorAll('[role="menuitem"]') ?? [])])

  async function show() {
    open = true
    await tick()
    ;/** @type {HTMLElement | null | undefined} */ (root?.querySelector('[aria-current]'))?.focus()
  }

  /** @param {boolean} [restore] */
  function hide(restore = false) {
    open = false
    if (restore) trigger?.focus()
  }

  /** @param {KeyboardEvent} event */
  function triggerKeys(event) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      show()
    }
  }

  // The menu's keys stay in it, so the page's shortcuts do not act behind it.
  /** @param {KeyboardEvent} event */
  function menuKeys(event) {
    event.stopPropagation()
    const list = items()
    const at = list.indexOf(/** @type {HTMLElement} */ (document.activeElement))
    if (event.key === 'Escape') {
      event.preventDefault()
      hide(true)
    } else if (event.key === 'Tab') {
      hide(true)
    } else if (event.key === ' ') {
      event.preventDefault()
      list[at]?.click()
    } else {
      const to = { ArrowDown: at + 1, ArrowUp: at - 1, Home: 0, End: list.length - 1 }[event.key]
      if (to === undefined) return
      event.preventDefault()
      list[(to + list.length) % list.length].focus()
    }
  }

  $effect(() => {
    if (!open) return
    const away = (/** @type {PointerEvent} */ event) => {
      if (root && !event.composedPath().includes(root)) hide()
    }
    addEventListener('pointerdown', away, true)
    return () => removeEventListener('pointerdown', away, true)
  })
</script>

<div class="site-select" bind:this={root}>
  <button class="site-trigger" type="button" bind:this={trigger}
    aria-haspopup="menu" aria-expanded={open} aria-controls={open ? `sites-${uid}` : undefined} aria-label={`${t('app.name')}, ${t('app.sites')}`}
    onclick={() => (open ? hide() : show())} onkeydown={triggerKeys}>
    {@render children()}
    <svg class="chevron" class:up={open} viewBox="0 0 10 10" width="10" height="10" aria-hidden="true"><path d="M2 3.5 5 6.5 8 3.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
  </button>
  {#if open}
    <div class="ui-menu site-menu" id={`sites-${uid}`} role="menu" tabindex="-1" aria-label={t('app.sites')} onkeydown={menuKeys}>
      {#each SITES as site (site.id)}
        {@const current = site.id === 'khitan'}
        <a class="ui-menu-item site-item" role="menuitem" tabindex="-1" href={site.href}
          aria-current={current ? 'page' : undefined}
          onclick={event => { if (current) home(event); hide(current) }}>
          <img src={site.logo} alt="" width="28" height="28" />
          <span class="site-name">{t(site.name)}</span>
          {#if current}
            <svg class="check" viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="m3 8.5 3 3 7-7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {/if}
        </a>
      {/each}
    </div>
  {/if}
</div>

<style>
  .site-select{position:relative;display:flex;align-items:center;block-size:100%}
  .site-trigger{display:flex;align-items:center;gap:var(--ui-space-sm);padding:var(--ui-space-2xs) var(--ui-space-xs);margin-inline:calc(var(--ui-space-xs) * -1);border:0;border-radius:var(--ui-radius-sm);background:none;color:var(--ui-color-ink);font:inherit;cursor:pointer}
  .site-trigger:hover{background:var(--ui-color-surface-hover)}
  .chevron{flex:none;color:var(--ui-color-ink-muted);transition:transform var(--ui-duration) var(--ui-ease)}
  .chevron.up{transform:rotate(180deg)}
  .site-menu{position:absolute;inset-block-start:calc(100% - var(--ui-space-xs));inset-inline-start:calc(var(--ui-space-xs) * -1);z-index:var(--ui-z-menu);inline-size:248px;max-inline-size:calc(100vw - 2 * var(--ui-space-lg))}
  .site-item{align-items:center;gap:var(--ui-space-md);padding:var(--ui-space-sm)}
  .site-item img{flex:none;border-radius:6px}
  .site-name{flex:1;min-inline-size:0;font-weight:var(--ui-weight-medium)}
  .check{flex:none;color:var(--ui-color-accent-ink)}
  @media (prefers-reduced-motion:reduce){.chevron{transition:none}}
</style>
