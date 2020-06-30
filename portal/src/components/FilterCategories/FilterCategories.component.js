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
      if (this.selectedFilters) {
        const datesFilter = this.selectedFilters.find(
          item => item.external_id === this.publisherDateExternalId
        )
        if (datesFilter && datesFilter.items) {
          return {
            start_date: datesFilter.items[0] || null,
            end_date: datesFilter.items[1] || null
          }
        }
      } else return {}
    },
    hasSelectedChildren(cat) {
      return cat.children.filter(child => child.selected === true).length > 0
    },
    hasDatesRangeFilter(selectedFilters) {
      const datesFilter = selectedFilters.find(
        item => item.external_id === this.publisherDateExternalId
      )
      if (datesFilter && datesFilter.items) {
        const items = datesFilter.items.filter(item => item !== null)
        return items.length > 0
      } else return false
    },
    sortFilterItems(items) {
      const nullCounts = items.filter(item => item.count === null)
      const sorted = items
        .filter(item => item.count !== null)
        .sort((a, b) => b.count - a.count)
      return [...sorted, ...nullCounts]
    }
  },
  computed: {
    filtered_categories() {
      // Return categories that build the filter tree
      const filteredCategories = this.filterCategories.filter(
        cat => cat.is_hidden === false
      )

      const selectedItems = this.selectedFilters
        .flatMap(filter => filter.items)
        .filter(filter => filter !== null)

      filteredCategories.map(cat => {
        if (cat.children) {
          const filteredChildren = cat.children.filter(
            child => !child.is_hidden && child.count > 0
          )
          filteredChildren.map(child => {
            child.selected = selectedItems.includes(child.external_id)
            return child
          })
          if (
            this.hasSelectedChildren(cat) ||
            this.hasDatesRangeFilter(this.selectedFilters)
          ) {
            cat.isOpen = true
          }
          cat.showAll = false
          cat.children = this.sortFilterItems(filteredChildren)
        }
      })

      return filteredCategories
    }
  }
}
