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
  props: ['filterCategories', 'materials', 'selectedFilters'],
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
    onChange(e) {
      const { categoryId, itemId } = e.target.dataset
      const filter = { external_id: categoryId, items: [itemId] }
      let filters = this.selectedFilters

      if (e.target.checked) {
        filters.push(filter)
      } else {
        filters.splice(filters.indexOf(filter), 1)
      }
      this.executeSearch(filters)
    },
    onDateChange(dates) {
      const { start_date, end_date } = dates
      const filter = { external_id: this.publisherDate, items: [start_date, end_date] }
      let filters = this.selectedFilters.filter(el => el.external_id !== this.publisherDate)
      filters.push(filter)
      this.executeSearch(filters)
    },
    executeSearch(filters = []) {
      const { ordering, search_text } = this.materials
      let searchRequest = {
        search_text: search_text,
        ordering: ordering,
        filters: filters
      }

      // Execute search
      this.$router.push(this.generateSearchMaterialsQuery(searchRequest))
      this.$emit('input', searchRequest) // actual search is done by the parent page
    },
    resetFilter() {
      this.$router.push(
        this.generateSearchMaterialsQuery({
          filters: [],
          search_text: this.materials.search_text
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
    },
    datesRangeFilter() {
      if (this.selectedFilters) {
        const datesFilter = this.selectedFilters.find(
          item => item.external_id === this.publisherDate
        )
        if (datesFilter && datesFilter.items) {
          return {
            start_date: datesFilter.items[0] || null,
            end_date: datesFilter.items[1] || null
          }
        }
      }
      else return {}
    }
  },
  computed: {
    filtered_categories() {
      // Return categories that build the filter tree
      let filteredCategories = this.filterCategories
        ? this.filterCategories.filter(item => item.is_hidden === false)
        : []

      // set selected filters
      if (this.selectedFilters) {
        let selectedItems = []
        this.selectedFilters.forEach(filter => {
          selectedItems = selectedItems.concat(filter.items)
        })
        selectedItems = selectedItems.filter(item => item !== null)

        filteredCategories.map(cat => {
          return cat.children.map(child => {
            child.selected = selectedItems.includes(child.external_id)
            return child
          })
        })
      }

      return filteredCategories
    }
  }
}
