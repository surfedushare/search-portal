import { mapGetters } from 'vuex'
import { VueAutosuggest } from 'vue-autosuggest'
import { generateSearchMaterialsQuery } from './../../_helpers'
import { debounce } from 'lodash'

import axios from '~/axios'

export default {
  name: 'search',
  components: {
    VueAutosuggest
  },
  props: {
    'educational-level-category-id': {
      type: String
    },
    'material-type-external-id': {
      type: String
    },
    placeholder: {
      type: String,
      default: function() {
        return this.$t('Search-by-keywords')
      }
    },
    value: {
      type: Object,
      default: () => ({
        page_size: 10,
        page: 1,
        filters: [{}],
        search_text: null
      })
    }
  },
  mounted() {
    this.$store.dispatch('getFilterCategories')
  },
  data() {
    return {
      searchText: this.value.search_text,
      suggestions: [],
      formData: {
        ...this.value,
        page_size: 10,
        page: 1,
        ordering: null
      }
    }
  },
  methods: {
    generateSearchMaterialsQuery,
    onInputChange(query) {
      this.searchSuggestions(query, this)
    },
    searchSuggestions: debounce(async function(search) {
      if (!search) {
        this.suggestions = []
        return
      }

      const keywords = await axios.$get('keywords/', {
        params: { query: search }
      })

      this.suggestions = [{ data: keywords }]
    }, 350),
    onSelectSuggestion(result) {
      if (result) {
        this.emitSearch(result.item)
      } else if (this.searchText) this.emitSearch(this.searchText)
    },
    onSubmit() {
      if (!this.searchText) {
        return
      }

      const { filter_categories_loading } = this.$store.state.filterCategories

      if (filter_categories_loading) {
        filter_categories_loading.then(() => this.emitSearch(this.searchText))
      } else {
        this.emitSearch(this.searchText)
      }
    },
    emitSearch(searchText) {
      this.formData.search_text = searchText
      this.formData.filters = this.$store.getters.search_filters
      this.$router.push(this.generateSearchMaterialsQuery(this.formData))
      this.$emit('input', this.formData)
    },

    titleTranslation(filterCategory) {
      if (filterCategory.title_translations) {
        return filterCategory.title_translations[this.$i18n.locale]
      }
      return filterCategory.name
    },
    changeFilterCategory($event) {
      this.educationalLevelCategory.children = this.educationalLevelCategory.children.map(
        item => {
          item.selected = item.external_id === $event.target.value
          return item
        }
      )
    }
  },
  watch: {
    value(value) {
      this.formData = { ...value }
      this.searchText = value.search_text
    }
  },
  computed: {
    ...mapGetters({
      filterCategories: 'filter_categories',
      keywords: 'materials_keywords'
    }),
    autosuggestInputProps: function() {
      return {
        placeholder: this.placeholder,
        id: 'autosuggest__input',
        type: 'search',
        class: {
          'with-dropdown': this.suggestions.length > 0
        }
      }
    },
    autosuggestClasses: function() {
      return {
        'with-dropdown': this.suggestions.length > 0
      }
    },
    displayEducationalLevelSelect() {
      const { filterCategories, educationalLevelCategoryId } = this

      return (
        filterCategories &&
        filterCategories.results &&
        educationalLevelCategoryId
      )
    },
    educationalLevelCategory() {
      if (!this.displayEducationalLevelSelect) {
        return false
      }

      const { filterCategories, educationalLevelCategoryId } = this

      return filterCategories.results.find(
        category => category.external_id === educationalLevelCategoryId
      )
    },

    displayMaterialTypeFilter() {
      return (
        this.materialTypeExternalId &&
        this.filterCategories &&
        this.filterCategories.results.length > 0
      )
    },
    materialTypeCategory() {
      const { filterCategories, materialTypeExternalId } = this

      if (!this.displayMaterialTypeFilter) {
        return false
      }

      return filterCategories.results.find(
        item => item.external_id === materialTypeExternalId
      )
    }
  }
}
