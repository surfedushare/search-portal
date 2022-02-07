<template>
  <section class="search_bar">
    <PreSearchFilters class="search_bar__filters" @update:filter="onUpdateFilter" />
    <SearchTerm class="search_bar__term" @onSearch="searchMaterials" />
  </section>
</template>

<script>
import PreSearchFilters from '@/components/Search/PreSearchFilters'
import SearchTerm from '@/components/Search/SearchTerm'
import { isNull } from 'lodash'
import numeral from 'numeral'
import { mapGetters } from 'vuex'

export default {
  name: 'SearchBar',
  components: {
    SearchTerm,
    PreSearchFilters
  },
  data() {
    return {
      searchText: '',
      filters: {},
    }
  },
  computed: {
    ...mapGetters({
      filterCategories: 'filter_categories',
      materials: 'materials',
      allCommunities: 'allCommunities',
      statistic: 'statistic',
    }),
    numberOfMaterials() {
      return numeral(this.statistic.value).format('0,0').replace(',', '.')
    },
  },
  methods: {
    getFilterOptions(external_id) {
      if (this.filterCategories) {
        const filterCategory = this.filterCategories.find(
          (category) => category.external_id === external_id
        )

        if (filterCategory) {
          return {
            name: filterCategory.title_translations[this.$i18n.locale],
            options: filterCategory.children,
          }
        }
      }

      return null
    },
    searchMaterials(searchText) {
      const searchRequest = {
        search_text: searchText || '',
        filters: this.filters,
        page_size: 10,
        page: 1,
        demo: this.$root.isDemoEnvironment()
      }
      this.$emit('onSearch', searchRequest)
    },
    onUpdateFilter(filter) {
      if (isNull(filter.selection)) {
        delete this.filters[filter.field]
        return
      }
      this.filters[filter.field] = filter.selection
    },
  },
}
</script>

<style lang="less">
@import "../../variables";
.search_bar {
  margin-bottom: 60px;
  position: relative;
  display: flex;
  justify-content: space-between;
  z-index: 10;
  background: white;
  height: 92px;
  border-radius: 20px;
  box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
  margin-top: -18px;
  &__term {
    display: flex;
  }
  &__filters {
    display: flex;
    justify-content: space-between;
    margin-left: 1rem;
    margin-top: 1rem;
  }
}
</style>
