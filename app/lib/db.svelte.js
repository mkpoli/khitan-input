import { fill } from './data.js'

export const db = $state({ /** @type {'loading' | 'ready' | 'failed'} */ status: 'loading' })

export async function load() {
  try {
    const response = await fetch('/data/khitan.json')
    if (!response.ok) throw new Error(String(response.status))
    fill(await response.json())
    db.status = 'ready'
  } catch (error) {
    console.error(error)
    db.status = 'failed'
  }
}
