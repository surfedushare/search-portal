import { generateSearchMaterialsQuery } from '../_helpers'
import DatesRange from '~/components/DatesRange'

export default {
  name: 'filter-categories',
  components: { DatesRange },
  data() {
    const publisherDateExternalId = 'lom.lifecycle.contribute.publisherdate'
    const visibleItems = 3
    return {
      publisherDateExternalId,
      visibleItems,
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
      return category.children.some(child => {
        return !child.is_hidden
      })
    },
    onToggleCategory(category, update = true) {
      category.isOpen = !category.isOpen
      category.children.forEach(child => {
        this.onToggleCategory(child, false)
      })
      if (update) {
        this.$forceUpdate()
      }
    },
    onToggleShowAll(category) {
      category.showAll = !category.showAll
      this.$forceUpdate()
    },
    onChange(e) {
      const { categoryId, itemId } = e.target.dataset
      const existingItems = this.selectedFilters[categoryId] || []

      if (e.target.checked) {
        this.selectedFilters[categoryId] = [...existingItems, itemId]
      } else {
        this.selectedFilters[categoryId] = existingItems.filter(
          item => item !== itemId
        )
      }

      return this.executeSearch(this.selectedFilters)
    },
    onDateChange(dates) {
      const { start_date, end_date } = dates
      this.selectedFilters[this.publisherDateExternalId] = [
        start_date,
        end_date
      ]
      this.executeSearch(this.selectedFilters)
    },
    executeSearch(filters = {}) {
      const { ordering, search_text } = this.materials
      const searchRequest = {
        search_text,
        ordering,
        filters: { ...filters }
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
      if (category && category.title_translations) {
        return category.title_translations[language]
      }
      return category.name
    },
    datesRangeFilter() {
      return this.selectedFilters[this.publisherDateExternalId]
    },
    hasDatesRangeFilter() {
      if (!this.datesRangeFilter()) {
        return false
      }

      return this.datesRangeFilter().some(item => item !== null)
    },
    sortFilterItems(items) {
      const nullCounts = items.filter(item => item.count === null)
      const sorted = items
        .filter(item => item.count !== null)
        .sort((a, b) => b.count - a.count)
      return [...sorted, ...nullCounts]
    },
    cleanupFilterItems(filterItems) {
      // selected filter-items
      const selectedItems = Object.values(this.selectedFilters)
        .flat()
        .filter(filter => filter !== null)

      // filter-items that should be shown
      const filteredItems = filterItems.filter(
        item => !item.is_hidden && item.count > 0
      )

      filteredItems.map(item => {
        item.selected = selectedItems.includes(item.external_id)
        return item
      })

      return this.sortFilterItems(filteredItems)
    }
  },
  computed: {
    filtered_categories() {
      // Return categories that build the filter tree
      const filteredCategories = this.filterCategories.filter(
        category => !category.is_hidden
      )

      filteredCategories.map(category => {
        if (category.children) {
          category.children = this.cleanupFilterItems(category.children)

          // if a filter-item is selected, open the filter-category
          if (category.children.some(child => child.selected)) {
            category.isOpen = true
          }

          // if a dates-range is selected, open the dates-range component and
          // fill in the dates
          if (this.hasDatesRangeFilter()) {
            category.isOpen = true
            category.dates = this.datesRangeFilter()
          } else {
            category.dates = { start_date: null, end_date: null }
          }

          // don't show all filter-items of a category if more than 3 (default)
          category.showAll = false
        }
      })

      return filteredCategories
    }
  }
}
