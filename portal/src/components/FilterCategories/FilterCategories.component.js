import { generateSearchMaterialsQuery } from '../_helpers'
import DatesRange from '~/components/DatesRange'
import FilterCategory from './FilterCategory/FilterCategory'

export default {
  name: 'filter-categories',
  components: { DatesRange, FilterCategory },
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
    onCheck(categoryId, itemId) {
      const existingItems = this.selectedFilters[categoryId] || []
      this.selectedFilters[categoryId] = [...existingItems, itemId]
      return this.executeSearch(this.selectedFilters)
    },
    onUncheck(categoryId, itemId) {
      const existingItems = this.selectedFilters[categoryId] || []
      this.selectedFilters[categoryId] = existingItems.filter(
        item => item !== itemId
      )
      return this.executeSearch(this.selectedFilters)
    },
    onDateChange(dates) {
      this.selectedFilters[this.publisherDateExternalId] = dates
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
    datesRangeFilter() {
      return this.selectedFilters[this.publisherDateExternalId] || [null, null]
    },
    hasDatesRangeFilter() {
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
    filterableCategories() {
      // Return categories that build the filter tree
      const visibleCategories = this.filterCategories.filter(
        category => !category.is_hidden
      )

      visibleCategories.map(category => {
        if (category.children) {
          category.children = this.cleanupFilterItems(category.children)
        }
      })

      return visibleCategories
    }
  }
}
