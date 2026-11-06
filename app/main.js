// Khitan Input: find a grapheme by whatever is known about it, read its record, and write with it.
import { mount } from 'svelte'
import App from './App.svelte'
import './app.css'

mount(App, { target: /** @type {HTMLElement} */ (document.getElementById('app')) })
