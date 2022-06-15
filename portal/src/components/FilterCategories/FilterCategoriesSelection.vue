<template>
  <section class="filter-categories-selection">
    <v-chip
      v-for="filter in selectionFilterItems"
      :key="filter.id"
      close
      outlined
      @click:close="onClose(filter.parent.external_id, filter.external_id)"
    >
      <span>
        {{ filter.parent.title_translations[$i18n.locale] }}:&nbsp;
        <b>{{ filter.title_translations[$i18n.locale] }}</b>
      </span>
    </v-chip>
    <v-btn
      v-show="selectionFilterItems.length"
      outlined
      depressed
      @click="resetFilter">{{ $t('Reset-filters') }}
    </v-btn>
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

  margin: 25px auto 0;
  padding: 0 25px;
  max-width: 1296px;

  .v-chip {
    margin-right: 10px;
  }

}
</style>
