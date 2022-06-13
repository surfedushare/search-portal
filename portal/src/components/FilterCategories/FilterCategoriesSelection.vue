<template>
  <section class="filter-categories-selection">
    <v-chip
      v-for="filter in selectionFilterItems"
      :key="filter.id"
      close
      @click:close="onClose(filter.parent.external_id, filter.external_id)"
    >
      <span>
        {{ filter.parent.title_translations[$i18n.locale] }}:&nbsp;
        <b>{{ filter.title_translations[$i18n.locale] }}</b>
      </span>
    </v-chip>
    <v-btn v-show="selectionFilterItems.length" @click="resetFilter">{{ $t('Reset-filters') }}</v-btn>
  </section>
</template>

<script>
import { flatMap, isEqual, isEmpty } from 'lodash'


export default {
  name: 'FilterCategoriesSelection',
  props: {
    'materials': {
      type: Object,
      default: () => ({
      }),
    },
    'selectedFilters': {
      type: Object,
      default: () => ({}),
    }
  },
  computed: {
    selectionFilterItems() {
      if (isEmpty(this.selectedFilters)) {
        return []
      }
      return flatMap(this.selectedFilters, (filter_ids, categoryId) => {
        const cat = this.materials?.filter_categories?.find((category) => {
          return category.external_id === categoryId
        })
        const results = filter_ids.map((filter_id) => {
          return cat?.children.find((child) => {
            child.parent = cat
            return child.external_id === filter_id
          })
        })
        return results.filter((rsl) => rsl);
      })
    },
  },
  methods: {
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
    onClose(categoryId, itemId) {
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
  },
}
</script>

<style lang="less" scoped>
@import "../../variables.less";

.filter-categories-selection {
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

      @media @tablet,
      @mobile {
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
