import { startsWith, forEach } from 'lodash'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import { getLocation } from '~/utils'

Vue.use(VueI18n)

export async function createI18N() {
  // Set instance options
  const i18n = new VueI18n({ fallbackLocale: 'nl' })
  i18n.locales = [
    { code: 'en', iso: 'en-US', file: 'en.js' },
    { code: 'nl', iso: 'nl-NL', file: 'nl.js' }
  ]
  i18n.defaultLocale = 'nl'
  i18n.differentDomains = false
  i18n.forwardedHost = false
  i18n.beforeLanguageSwitch = () => null
  i18n.onLanguageSwitched = () => null
  i18n.locale = startsWith(getLocation(), '/en/') ? 'en' : 'nl'

  // Lazy-load translations
  const { loadLanguageAsync } = require('./utils')
  await loadLanguageAsync(i18n, i18n.locale)
  forEach(i18n.locales, locale => {
    if (locale.code === i18n.locale) {
      return
    }
    loadLanguageAsync(i18n, locale.code)
  })

  return i18n
}
