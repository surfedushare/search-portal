import { flatMap, isEmpty, isEqual } from 'lodash'
import { generateSearchMaterialsQuery } from '../_helpers'
import DatesRange from '~/components/DatesRange'
import FilterCategory from './FilterCategory/FilterCategory'

export default {
  name: 'filter-categories',
  components: { DatesRange, FilterCategory },
  data() {
    const publisherDateExternalId = 'publisher_date'
    return {
      publisherDateExternalId,
      data: {
        start_date: null,
        end_date: null,
      },
    }
  },
  props: ['materials', 'defaultFilter', 'selectedFilters'],
  methods: {
    generateSearchMaterialsQuery,
    hasVisibleChildren(category) {
      if (!category.children.length) {
        return false
      }
      return category.children.some((child) => {
        return !child.is_hidden
      })
    },
    childExternalIds(categoryId, itemId) {
      const category = this.materials.filter_categories.find(
        (category) => category.external_id === categoryId
      )
      const item = category.children.find((item) => item.external_id === itemId)
      const iterator = (memo, item) => {
        if (item.children.length > 0) {
          item.children.forEach((child) => iterator(memo, child))
        }
        memo.push(item.external_id)
        return memo
      }

      return item.children.reduce(iterator, [item.external_id])
    },
    onCheck(categoryId, itemId) {
      const existingItems = this.selectedFilters[categoryId] || []
      if (existingItems.indexOf(itemId) >= 0) {
        return
      }

      const filters = this.childExternalIds(categoryId, itemId)
      this.selectedFilters[categoryId] = [...existingItems, ...filters]

      return this.executeSearch(this.selectedFilters)
    },
    onUncheck(categoryId, itemId) {
      const existingItems = this.selectedFilters[categoryId] || []
      const filters = this.childExternalIds(categoryId, itemId)
      this.selectedFilters[categoryId] = existingItems.filter(
        (item) => !filters.includes(item)
      )
      if (this.selectedFilters[categoryId].length === 0) {
        this.$delete(this.selectedFilters, categoryId)
      }
      if (itemId === this.$route.params.filterId) {
        return this.executeSearch(this.selectedFilters, 'materials-search')
      }
      return this.executeSearch(this.selectedFilters)
    },
    onDateChange(dates) {
      this.selectedFilters[this.publisherDateExternalId] = dates
      this.executeSearch(this.selectedFilters)
    },
    async executeSearch(filters = {}, name = null) {
      name = name || this.$route.name
      const { ordering, search_text } = this.materials
      const searchRequest = {
        search_text,
        ordering,
        filters: { ...filters },
      }
      // Execute search
      const route = this.generateSearchMaterialsQuery(searchRequest, name)
      if(isEqual(route.query, this.$route.query)) {
        return
      }
      await this.$router.push(route)
      this.$emit('input', searchRequest) // actual search is done by the parent page
    },
    resetFilter() {
      this.$emit('reset')
    },
    datesRangeFilter() {
      return this.selectedFilters[this.publisherDateExternalId] || [null, null]
    },
    hasDatesRangeFilter() {
      return this.datesRangeFilter().some((item) => item !== null)
    },
  },
  computed: {
    selectionFilterItems() {
      if (
        !this.materials ||
        !this.materials.filter_categories ||
        !this.selectedFilters
      ) {
        return []
      }
      return flatMap(this.selectedFilters, (items, categoryId) => {
        const category = this.materials.filter_categories.find((category) => {
          return category.external_id === categoryId
        })
        const results = items.map((item) => {
          return category.children.find((child) => {
            child.parent = category
            return child.external_id === item
          })
        })
        return results.filter((rsl) => {
          return rsl
        })
      })
    },
    filterableCategories() {
      if (
        !this.materials ||
        !this.materials.filter_categories ||
        isEmpty(this.materials.records)
      ) {
        return []
      }

      // remove all filters that should not be shown to the users
      let defaultFilterItem = {}
      if (this.defaultFilter) {
        defaultFilterItem =
          this.$store.getters.getCategoryById(
            this.defaultFilter,
            this.$route.meta.filterRoot
          ) || {}
      }
      const visibleCategories = this.materials.filter_categories.filter(
        (category) =>
          !category.is_hidden &&
          category.external_id !== defaultFilterItem.searchId
      )

      // aggregate counts to the highest level
      const filterableCategories = visibleCategories.map((category) => {
        if (category.children) {
          category.children = category.children.map((child) => {
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
          (child) => !child.is_hidden && child.count > 0
        )

        category.children = category.children.map((child) => {
          const selected = this.selectedFilters[category.external_id] || []
          child.selected = selected.includes(child.external_id)
          return child
        })

        return category
      })

      return filterableCategories.filter((category) => {
        return (
          category.children.length >= 2 ||
          category.children.some((child) => {
            return child.selected
          })
        )
      })
    },
  },
}
