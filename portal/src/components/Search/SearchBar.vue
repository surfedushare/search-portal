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
    searchMaterials(searchText) {
      const searchRequest = {
        search_text: searchText || '',
        filters: this.filters,
        page_size: 10,
        page: 1,
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
  display: grid;
  grid-auto-flow: row;
  grid-template-rows: repeat(2, auto);
  position: relative;
  z-index: 10;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
  margin-top: -18px;
}
</style>
