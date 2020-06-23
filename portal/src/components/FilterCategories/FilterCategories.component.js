import { generateSearchMaterialsQuery } from '../_helpers'
import DatesRange from '~/components/DatesRange'
import _ from 'lodash'

export default {
  name: 'filter-categories',
  components: { DatesRange },
  data() {
    const publisherDate = 'lom.lifecycle.contribute.publisherdate'
    return {
      publisherDate,
      data: {
        start_date: null,
        end_date: null
      }
    }
  },
  props: ['filterCategories'],
  methods: {
    generateSearchMaterialsQuery,
    hasVisibleChildren(category) {
      if (!category.children.length) {
        return false
      }
      return _.some(category.children, child => {
        if (child.count > 0) {
          return !child.is_hidden
        }
      })
    },
    onToggleCategory(category, update = true) {
      category.isOpen = !category.isOpen
      _.forEach(category.children, child => {
        this.onToggleCategory(child, false)
      })
      if (update) {
        this.$forceUpdate()
      }
    },
    onChange() {
      const { categoryId, itemId } = event.target.dataset
      const filter = { external_id: categoryId, items: [itemId] }
      this.executeSearch(filter)
    },
    onDateChange() {
      this.executeSearch()
    },
    executeSearch(filter = {}) {
      let searchText = this.$store.getters.materials.search_text
      let ordering = this.$store.getters.materials.ordering

      let filters = this.$store.getters.search_filters
      filters.push(filter)
      let searchRequest = {
        search_text: searchText,
        ordering: ordering,
        filters: filters
      }

      // Execute search
      this.$router.push(this.generateSearchMaterialsQuery(searchRequest))
      this.$emit('input', searchRequest) // actual search is done by the parent page
    },
    /**
     * Event the reset filter
     */
    resetFilter() {
      this.$router.push(
        this.generateSearchMaterialsQuery({
          filters: [],
          search_text: this.$store.getters.materials.search_text
        }),
        () => {
          location.reload()
        },
        () => {
          location.reload()
        }
      )
    },
    getTitleTranslation(category, language) {
      if (
        !_.isNil(category.title_translations) &&
        !_.isEmpty(category.title_translations)
      ) {
        return category.title_translations[language]
      }
      return category.name
    }
  },
  computed: {
    filtered_categories() {
      // Return categories that build the filter tree
      return this.filterCategories
        ? this.filterCategories.filter((item) => item.is_hidden === false) : []
    }
  }
}
