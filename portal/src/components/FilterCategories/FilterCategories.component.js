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
      const filter = { external_id: categoryId, items: [] }
      const categoryFilter =
        this.selectedFilters.find(f => f.external_id === categoryId) || filter
      const selectedFilters = this.selectedFilters.filter(
        f => f.external_id !== categoryId
      )

      if (e.target.checked) {
        categoryFilter.items = [...categoryFilter.items, itemId]
      } else {
        categoryFilter.items = categoryFilter.items.filter(f => f !== itemId)
      }
      return this.executeSearch([...selectedFilters, categoryFilter])
    },
    onDateChange(dates) {
      const { start_date, end_date } = dates
      const filter = {
        external_id: this.publisherDateExternalId,
        items: [start_date, end_date]
      }
      const filters = this.selectedFilters.filter(
        el => el.external_id !== this.publisherDateExternalId
      )
      this.executeSearch([...filters, filter])
    },
    executeSearch(filters = []) {
      const { ordering, search_text } = this.materials
      let searchRequest = {
        search_text,
        ordering,
        filters
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
      const datesFilter = this.selectedFilters.find(
        item => item.external_id === this.publisherDateExternalId
      )
      if (datesFilter && datesFilter.items) {
        return {
          start_date: datesFilter.items[0] || null,
          end_date: datesFilter.items[1] || null
        }
      }
    },
    hasDatesRangeFilter(cat, selectedFilters) {
      if (cat.external_id !== this.publisherDateExternalId) return false

      const datesFilter = selectedFilters.find(
        item => item.external_id === this.publisherDateExternalId
      )
      return (datesFilter &&
        datesFilter.items &&
        datesFilter.items.some(item => item !== null)
      )
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
      const selectedItems = this.selectedFilters
        .flatMap(filter => filter.items)
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
          if (this.hasDatesRangeFilter(category, this.selectedFilters)) {
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
