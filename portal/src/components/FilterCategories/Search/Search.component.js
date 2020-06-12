import { mapGetters } from "vuex";
import { VueAutosuggest } from "vue-autosuggest";
import { generateSearchMaterialsQuery } from "./../../_helpers";
import _, { debounce } from "lodash";

export default {
  name: "search",
  props: {
    "hide-categories": {
      type: Boolean,
      default: false
    },
    "hide-filter": {
      type: Boolean,
      default: false
    },
    "show-selected-category": {
      type: [Boolean, String],
      default: false
    },
    "active-category-external-id": {
      type: String
    },
    placeholder: {
      type: String,
      default: function() {
        return this.$t("Search-by-keywords");
      }
    },
    value: {
      type: Object,
      default: () => ({
        page_size: 10,
        page: 1,
        filters: [{}],
        search_text: null
      })
    }
  },
  mounted() {
    this.$store.dispatch("getFilterCategories");
  },
  data() {
    return {
      searchText: this.value.search_text,
      suggestions: [],

      // TODO: remove?
      showMobileFilter: false,
      filter: {},
      previous_category_id: null,
      active_category_id: null,

      formData: {
        ...this.value,
        page_size: 10,
        page: 1,
        ordering: null
      }
    };
  },
  components: {
    VueAutosuggest
  },
  methods: {
    onInputChange(query) {
      this.searchSuggestions(query, this);
    },
    searchSuggestions: debounce(async function(search) {
      if (!search) {
        this.suggestions = [];
        return;
      }

      const keywords = await this.$axios.$get("keywords/", {
        params: { query: search }
      });

      this.suggestions = [{ data: keywords }];
    }, 350),
    onSelectSuggestion(result) {
      if (result) {
        this.emitSearch(result.item);
      } else if (this.searchText) {
        this.emitSearch(this.searchText);
      }
    },
    onSubmit() {
      if (!this.searchText) {
        return;
      }

      const { filter_categories_loading } = this.$store.state.filterCategories;

      if (filter_categories_loading) {
        filter_categories_loading.then(() => this.emitSearch(this.searchText));
      } else {
        this.emitSearch(this.searchText);
      }
    },
    emitSearch(searchText) {
      this.formData.search_text = searchText;
      this.formData.filters = this.$store.getters.search_filters;
      this.$router.push(this.generateSearchMaterialsQuery(this.formData));
      this.$emit("input", this.formData);
    },

    // TODO: needed?
    getTitleTranslation(filter_category, language) {
      if (
        !_.isNil(filter_category.title_translations) &&
        !_.isEmpty(filter_category.title_translations)
      ) {
        return filter_category.title_translations[language];
      }
      return filter_category.name;
    },
    generateSearchMaterialsQuery,
    showMobileFilterOptions() {
      this.showMobileFilter = !this.showMobileFilter;
    },

    setOnlyChildSelected(children, childId) {
      // TODO: make this function part of a service and recursively set selected on children
      _.forEach(children, child => {
        child.selected = child.external_id === childId;
        _.forEach(child.children, grantChild => {
          grantChild.selected = child.selected;
        });
      });
    },

    changeFilterCategory($event) {
      this.setOnlyChildSelected(
        this.filter_category.children,
        $event.target.value
      );
      // const { external_id } = this.filter_category;
      // const current_filter = this.formData.filters.find(
      //   filter => filter.external_id === external_id
      // );
      // if (current_filter) {
      //   this.formData.filters = this.formData.filters.map(filter => {
      //     if (filter.external_id === external_id) {
      //       return {
      //         external_id: this.filter_category.external_id,
      //         items: [$event.target.value]
      //       };
      //     }
      //
      //     return filter;
      //   });
      // } else {
      //   this.formData.filters = [
      //     ...this.formData.filters,
      //     {
      //       external_id: this.filter_category.external_id,
      //       items: [$event.target.value]
      //     }
      //   ];
      // }
    }
  },
  watch: {
    active_category(category) {
      if (category && this.previous_category_id !== category.external_id) {
        this.previous_category_id = category.external_id;
        // Clearing filters when category changed
        this.formData.filters[0].items = [];
      }
    },
    filter: {
      handler(filter) {
        if (filter) {
          this.formData.filters[0].items = Object.keys(filter).filter(
            item => filter[item]
          );
        }
      },
      deep: true
    },
    value(value) {
      this.formData = {
        ...value
      };
      this.searchText = value.search_text;
    }
  },
  computed: {
    ...mapGetters({
      filterCategories: "filter_categories",
      keywords: "materials_keywords"
    }),
    autosuggestInputProps: function() {
      return {
        placeholder: this.placeholder,
        id: "autosuggest__input",
        class: {
          "with-dropdown": this.suggestions.length > 0
        }
      };
    },
    autosuggestClasses: function() {
      return {
        "with-dropdown": this.suggestions.length > 0
      };
    },
    filter_category() {
      const { filterCategories, showSelectedCategory } = this;

      if (
        filterCategories &&
        filterCategories.results &&
        showSelectedCategory
      ) {
        return filterCategories.results.find(
          category => category.external_id === showSelectedCategory
        );
      }

      return false;
    },
    /**
     * Get the active category
     * @returns {*} - false or active category
     */
    active_category() {
      const { filterCategories, hideFilter, activeCategoryExternalId } = this;

      if (
        !filterCategories ||
        _.isEmpty(filterCategories.results) ||
        hideFilter
      ) {
        return false;
      }
      if (activeCategoryExternalId) {
        let ix = filterCategories.results.findIndex(
          item => item.external_id === activeCategoryExternalId
        );
        return filterCategories.results[ix];
      }
      return filterCategories.results[0];
    }
  }
};
