<template>
  <section class="filter-categories-selection" data-test="selected_filters">
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
    <v-btn v-show="selectionFilterItems.length" outlined depressed data-test="reset_filters" @click="resetFilter">
      {{ $t("Reset-filters") }}
    </v-btn>
  </section>
</template>

<script>
import { flatMap, isEmpty } from "lodash";

export default {
  name: "FilterCategoriesSelection",
  props: {
    materials: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    selectionFilterItems() {
      const selectedFilters = this.$store.state.filterCategories.selection;
      if (isEmpty(selectedFilters)) {
        return [];
      }
      return flatMap(selectedFilters, (filter_ids, categoryId) => {
        const cat = this.materials?.filter_categories?.find((category) => {
          return category.external_id === categoryId;
        });
        const results = filter_ids.map((filter_id) => {
          return cat?.children.find((child) => {
            child.parent = cat;
            return child.external_id === filter_id;
          });
        });
        return results.filter((rsl) => rsl);
      });
    },
  },
  methods: {
    onClose(categoryId, itemId) {
      this.$store.commit("DESELECT_FILTER_CATEGORIES", { category: categoryId, selection: [itemId] });
      this.$emit("filter");
    },
    resetFilter() {
      this.$store.commit("RESET_FILTER_CATEGORIES_SELECTION");
      this.$emit("filter");
    },
  },
};
</script>

<style lang="less" scoped>
@import "../../variables.less";

.filter-categories-selection {
  margin: 15px auto 0;
  padding: 0 25px;
  max-width: 1296px;

  .v-chip {
    margin: 10px 10px 0 0;
  }
  .v-btn {
    margin-top: 10px;
  }
}
</style>
