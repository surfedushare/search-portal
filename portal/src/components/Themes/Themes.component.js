import { isEmpty } from 'lodash'

export default {
  name: 'themes',
  props: ['themes'],
  mounted() {},
  data() {
    return {}
  },
  methods: {
    getTitleTranslation(theme, language) {
      if (
        !isEmpty(theme.title_translations)
      ) {
        return theme.title_translations[language]
      }
      return theme.title
    },
    getDescriptionTranslation(theme, language) {
      if (
        !isEmpty(theme.description_translations)
      ) {
        return theme.description_translations[language]
      }
      return theme.description
    }
  },
  computed: {
    /**
     * Get the current theme
     * @returns {*}
     */
    currentThemes() {
      const themes = this.themes
      if (themes) {
        if (themes.results) {
          return themes.results.length ? themes.results : false
        }
        return themes
      }
      return false
    }
  }
}
