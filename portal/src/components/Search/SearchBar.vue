<template>
  <section class="search_bar">
    <PreSearchFilters v-if="enablePreFilters" class="search_bar__filters" @update:filter="onUpdateFilter" />
    <SearchTerm class="search_bar__term" @search="searchMaterials" />
  </section>
</template>

<script>
import PreSearchFilters from "@/components/Search/PreSearchFilters";
import SearchTerm from "@/components/Search/SearchTerm";
import { isNull, forEach } from "lodash";

export default {
  name: "SearchBar",
  components: {
    SearchTerm,
    PreSearchFilters,
  },
  props: {
    enablePreFilters: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      searchText: "",
      filters: {},
    };
  },
  methods: {
    searchMaterials(searchText) {
      forEach(this.filters, (selection, field) => {
        if (selection.length) {
          this.$store.commit("SELECT_FILTER_CATEGORIES", { category: field, selection });
        }
      });
      this.$emit("search", searchText);
    },
    onUpdateFilter(filter) {
      if (isNull(filter.selection)) {
        delete this.filters[filter.field];
        return;
      }
      this.filters[filter.field] = filter.selection;
    },
  },
};
</script>

<style lang="less" scoped>
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
