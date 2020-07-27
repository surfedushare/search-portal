import { startsWith } from 'lodash'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import { getLocation } from '~/utils'
import axios from 'axios'
import injector from 'vue-inject'

Vue.use(VueI18n)
const $log = injector.get('$log')

export async function loadLanguages() {
  async function loadLanguageAsync(i18n, locale) {
    if (!i18n.loadedLanguages.includes(locale)) {
      try {
        const messages = await axios
          .get('/locales/' + locale)
          .then(response => response.data)

        i18n.setLocaleMessage(locale, messages)
        i18n.loadedLanguages.push(locale)
        return messages
      } catch (error) {
        $log.error(error)
      }
    }

    return Promise.resolve()
  }

  await loadLanguageAsync(i18n, i18n.locale)

  i18n.locales
    .filter(locale => locale !== i18n.locale)
    .forEach(locale => loadLanguageAsync(i18n, locale.code))
}

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
i18n.loadedLanguages = []
i18n.locale = startsWith(getLocation(), '/en/') ? 'en' : 'nl'

export default i18n
