import { generateSearchMaterialsQuery } from '../_helpers'
import DatesRange from '~/components/DatesRange'
import FilterCategory from './FilterCategory/FilterCategory'

export default {
  name: 'filter-categories',
  components: { DatesRange, FilterCategory },
  data() {
    const publisherDateExternalId = 'lom.lifecycle.contribute.publisherdate'
    return {
      publisherDateExternalId,
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
    childExternalIds(categoryId, itemId) {
      const category = this.filterCategories.find(
        category => category.external_id === categoryId
      )
      const item = category.children.find(item => item.external_id === itemId)
      const iterator = (memo, item) => {
        if (item.children.length > 0) {
          item.children.forEach(child => iterator(memo, child))
        }
        memo.push(item.external_id)
        return memo
      }

      return item.children.reduce(iterator, [item.external_id])
    },
    onCheck(categoryId, itemId) {
      const existingItems = this.selectedFilters[categoryId] || []

      const filters = this.childExternalIds(categoryId, itemId)
      this.selectedFilters[categoryId] = [...existingItems, ...filters]

      return this.executeSearch(this.selectedFilters)
    },
    onUncheck(categoryId, itemId) {
      const existingItems = this.selectedFilters[categoryId] || []
      const filters = this.childExternalIds(categoryId, itemId)
      this.selectedFilters[categoryId] = existingItems.filter(
        item => !filters.includes(item)
      )
      if (this.selectedFilters[categoryId].length === 0) {
        this.$delete(this.selectedFilters, categoryId)
      }
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
    }
  },
  computed: {
    filterableCategories() {
      const visibleCategories = this.filterCategories.filter(
        category => !category.is_hidden
      )

      // aggregate counts to the highest level
      return visibleCategories.map(category => {
        if (category.children) {
          category.children = category.children.map(child => {
            if (child.children.length > 0) {
              child.count = child.children.reduce(
                (memo, c) => memo + c.count,
                0
              )
            }

            return child
          })
        }

        category.children = category.children.filter(
          child => !child.is_hidden && child.count > 0
        )

        category.children = category.children.map(child => {
          const selected = this.selectedFilters[category.external_id] || []
          child.selected = selected.includes(child.external_id)
          return child
        })

        return category
      })
    }
  }
}
