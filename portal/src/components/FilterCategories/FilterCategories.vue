<template>
  <section class="filter-categories">
    <h3 class="filter-categories__title">{{ $t('Filter') }}</h3>

    <div v-if="selectionFilterItems.length" class="filter-categories__links">
      <p class="filter-categories__reset">{{ $t('Selected-filters') }}</p>
      <a href="/materials/search/" @click.prevent="resetFilter">({{ $t('Reset-filters') }})</a>
    </div>
    <ul data-test="selected_filters" class="selected-filters">
      <li v-for="filter in selectionFilterItems" :key="filter.id">
        <span>
          {{ filter.parent.title_translations[$i18n.locale] }}:&nbsp;
          <b>{{ filter.title_translations[$i18n.locale] }}</b>
        </span>
        <button
          class="remove-icon"
          @click="onUncheck(filter.parent.external_id, filter.external_id)"
        ></button>
      </li>
    </ul>

    <div class="filter-categories__items">
      <ul v-if="filterableCategories.length" class="filter-categories__items_wrapper">
        <template v-for="category in filterableCategories">
          <DatesRange
            v-if="category.external_id === publisherDateExternalId"
            :key="category.external_id"
            :data-test="category.external_id"
            :category="category"
            :dates="datesRangeFilter()"
            :inline="true"
            :disable-future-days="true"
            theme="min"
            @input="onDateChange"
          />

          <FilterCategory
            v-else-if="hasVisibleChildren(category)"
            :key="category.id"
            :data-test="category.external_id"
            :category="category"
            @check="onCheck"
            @uncheck="onUncheck"
          />
        </template>
      </ul>
    </div>
  </section>
</template>

<script>
import { flatMap, isEqual } from 'lodash'
import DatesRange from '~/components/DatesRange'
import { generateSearchMaterialsQuery } from '../_helpers'
import FilterCategory from './FilterCategory.vue'


export default {
  name: 'FilterCategories',
  components: { DatesRange, FilterCategory },
  props: {
    'materials': {
      type: Object,
      default: () => ({
      }),
    },
    'defaultFilter': {
      type: Object,
      default: () => ({
      }),
    },
    'selectedFilters': {
      type: Object,
      default: () => ({
      }),
    }
  },
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
  computed: {
    selectionFilterItems() {
      if (
        !this.selectedFilters
      ) {
        return []
      }
      return flatMap(this.selectedFilters, (filter_ids, categoryId) => {

        const cat = this.materials.filter_categories?.find((category) => {
          return category.external_id === categoryId
        })
        const results = filter_ids.map((filter_id) => {
          return cat?.children.find((child) => {
            child.parent = cat
            return child.external_id === filter_id
          })
        })
        const filters = results.filter((rsl) => {
          return rsl
        })
        return filters;
      })
    },
    filterableCategories() {
      if (!this.materials.filter_categories) {
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

        category.children = category.children?.filter(
          (child) => !child.is_hidden && child.count > 0
        )

        category.children = category.children.map((child) => {
          const selected = this.selectedFilters[category.external_id] || []
          child.selected = selected.includes(child.external_id)
          return child
        })
        return category
      })

      if (this.materials.records.length === 0) {
        return filterableCategories
      } else {
        return filterableCategories.filter((category) => {
          return (
            category.children.length >= 2 ||
            category.children.some((child) => {
              return child.selected
            })
          )
        })
      }

    },
  },
  methods: {
    generateSearchMaterialsQuery,
    hasVisibleChildren(category) {
      if (this.materials.records.length === 0) {
        return true
      }
      if (!category.children.length) {
        return false
      }
      return category.children.some((child) => {
        return !child.is_hidden
      })
    },
    childExternalIds(categoryId, itemId) {
      // he
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

      return item.children?.reduce(iterator, [item.external_id])
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
      if (isEqual(route.query, this.$route.query)) {
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
}
</script>

<style lang="less" scoped>
@import "../../variables.less";

.filter-categories {
  &--loading {
    opacity: 0.5;
    pointer-events: none;
  }

  &__title {
    margin: 0 0 9px;
  }

  &__links {
    margin: 0 0 17px;
    display: flex;
    width: 100%;
    justify-content: space-between;
    p {
      font-family: @second-font;
      font-size: 16px;
      font-weight: bold;
      color: @green;
    }
  }

  &__reset {
    &:before {
      content: "";
      display: inline-block;
      vertical-align: middle;
      width: 13px;
      height: 13px;
      background: url("../../assets/images/filters.svg") 50% 50% no-repeat;
      background-size: contain;
      margin: -3px 4px 0 0;
    }
  }
  .selected-filters {
    padding-left: 0;
    margin-bottom: 17px;
  }
  .selected-filters li {
    display: flex;
    justify-content: space-between;
    .remove-icon {
      width: 23px;
      height: 23px;
      margin-right: 3px;
      border: none;
      background: url(../../assets/images/close-black.svg) 50% 50% no-repeat;
      background-size: 23px 23px;
    }
  }

  &__select {
    margin: 0 0 23px;
  }

  &__item_title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    word-break: break-word;

    &:after {
      content: "";
      display: inline-block;
      width: 20px;
      height: 20px;
      flex-shrink: 0;
      margin: 2px 5px 0 20px;
      background: url("../../assets/images/plus-black.svg") 50% 50% / contain no-repeat;
    }

    &--hide:after {
      background: url("../../assets/images/min-black.svg") 50% 50% / contain no-repeat;
    }
  }

  &__item--full-visible &__item_title {
    border-bottom: 1px solid @light-grey;
    padding-bottom: 6px;
    &:after {
      display: none;
    }
  }

  &__items {
    padding: 0 15px 0 0;
    margin: 0 -15px 0 0;
    list-style: none;
    overflow-x: hidden;

    &--no-scroll {
      max-height: inherit;
    }

    &_wrapper {
      padding: 0;
      margin: 0;
      list-style: none;
      width: 100%;
      overflow: visible;
      box-sizing: border-box;
    }

    &--masonry {
      display: flex;
      flex-wrap: wrap;
    }
  }

  &__item {
    padding: 0 0 2px;
    margin: 0 0 19px;
    list-style: none;
    border-bottom: 1px solid @light-grey;
  }

  &__item--full-visible {
    border-bottom: none;
  }

  &__items--masonry &__item {
    width: 25%;
  }

  &__subitems {
    padding: 16px 0;
    margin: 0;
    list-style: none;
  }

  &__subitem {
    padding: 3px 0;
    margin: 0;
    list-style: none;
    display: block;
    width: 100%;

    &_icon {
      &.cc-by {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/sa-black.svg") no-repeat 23px 0;
        background-size: contain;
      }
      &.cc-by-nc,
      &.cc-by-nc-sa {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/nc-black.svg") no-repeat 23px 0,
          url("../../assets/images/sa-black.svg") no-repeat 46px 0;
        background-size: contain;
      }
      &.cc-by-nd {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/nd-black.svg") no-repeat 23px 0;
        background-size: contain;
      }
      &.cc-by-sa {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/nc-black.svg") no-repeat 23px 0;
        background-size: contain;
      }
      &.cc-by-nc-nd {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/nc-black.svg") no-repeat 23px 0,
          url("../../assets/images/nd-black.svg") no-repeat 46px 0;
        background-size: contain;
      }

      height: 20px;
      margin: 6px 0 3px;
      width: 100%;
      display: block;
      background-size: contain;

      @media @tablet, @mobile {
        margin-bottom: 25px;
      }

      &--inline {
        display: inline-block;
        width: 70px;
        vertical-align: bottom;
        margin: 0;
      }
    }

    input {
      margin: 5px 10px 0;
    }

    label {
      cursor: pointer;
    }

    &--show-more {
      padding-top: 10px;
      padding-left: 10px;
      font-size: 14px;

      a {
        text-decoration: underline;

        &:hover {
          text-decoration: none;
        }
      }
    }
  }

  .category-children {
    margin-left: 20px;
    padding-left: 0;
    border-left: 1px solid lightgray;
    li {
      padding-left: 20px;
    }
  }

  .filter-checkbox {
    display: flex;
    flex-direction: row;
  }
}
</style>
