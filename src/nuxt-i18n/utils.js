/**
 * Asynchronously load messages from translation files
 * @param  {VueI18n}  i18n  vue-i18n instance
 * @param  {String}   lang  Language code to load
 * @return {Promise}
 */
import axios from 'axios';


export async function loadLanguageAsync (i18n, locale) {
  const LOCALE_CODE_KEY = 'code';

  if (!i18n.loadedLanguages) {
    i18n.loadedLanguages = []
  }
  if (!i18n.loadedLanguages.includes(locale)) {
    const langOptions = i18n.locales.find(l => l[LOCALE_CODE_KEY] === locale);
    if (langOptions) {
      try {
        const messages = await axios
            .get(process.env.VUE_APP_LOCALES_URL + langOptions.code)
            .then(response => {
                return response.data;
            });
        i18n.setLocaleMessage(locale, messages);
        i18n.loadedLanguages.push(locale);
        return messages;
      } catch (error) {
        console.error(error)
      }

    } else {
      console.warn('[nuxt-i18n] Could not find lang file for locale ' + locale)
    }

  }
  return Promise.resolve()
}
