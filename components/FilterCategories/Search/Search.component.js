import { mapGetters } from 'vuex';
import { debounce, generateSearchMaterialsQuery } from './../../_helpers';
import DatesRange from './../../DatesRange';
export default {
  name: 'search',
  props: {
    'hide-categories': {
      type: Boolean,
      default: false
    },
    'hide-filter': {
      type: Boolean,
      default: false
    },
    'show-selected-category': {
      type: [Boolean, String],
      default: false
    },
    'active-category-external-id': {
      type: String
    },
    placeholder: {
      type: String,
      default: function() {
        return this.$t('Search-by-keywords');
      }
    },
    value: {
      type: Object,
      default: () => ({
        page_size: 10,
        page: 1,
        filters: [{}],
        search_text: []
      })
    }
  },
  mounted() {
    this.$store.dispatch('getFilterCategories');
  },
  components: {
    DatesRange
  },
  data() {
    return {
      showMobileFilter: false,
      filter: {},
      previous_category_id: null,
      active_category_id: null,
      formData: {
        page_size: 10,
        page: 1,
        ...this.value,
        ordering: '-lom.lifecycle.contribute.publisherdate'
      },
      dates_range: {
        start_date: null,
        end_date: null
      }
    };
  },
  methods: {
    generateSearchMaterialsQuery,
    /**
     * search event
     * @param search
     * @param loading
     */
    onSearch(search, loading) {
      loading(true);
      this.search(loading, search, this);
    },
    /**
     * Searching keywords with debounce 350ms
     */
    search: debounce((loading, search, vm) => {
      vm.$store
        .dispatch('searchMaterialsKeywords', {
          params: {
            query: search
          }
        })
        .then(() => {
          loading(false);
        })
        .catch(() => {
          loading(false);
        });
    }, 350),
    /**
     * Submit form
     */
    onSubmit() {
      this.formData.filters = this.$store.getters.search_filters;
      if (this.$listeners.submit) {
        this.$emit('submit', this.formData);
      } else {
        this.$router.push(this.generateSearchMaterialsQuery(this.formData));
        this.$emit('input', this.formData);
      }
    },

    showMobileFilterOptions() {
      this.showMobileFilter = !this.showMobileFilter;
    },

    setOnlyChildSelected(children, childId) {
      // TODO: make this function part of a service and recursively set selected on children
      _.forEach(children, (child) => {
          child.selected = child.external_id === childId;
          _.forEach(child.children, (grantChild) => {
            grantChild.selected = child.selected;
          });
      });
    },

    changeFilterCategory($event) {
      this.setOnlyChildSelected(this.filter_category.children, $event.target.value);
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
    /**
     * Watcher on the active category item
     * @param category - Object
     */
    active_category(category) {
      if (category && this.previous_category_id !== category.external_id) {
        this.previous_category_id = category.external_id;
        // Clearing filters when category changed
        this.formData.filters[0].items = [];
      }
    },
    /**
     * Watcher on the filter item
     * @param category - Object
     */
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
    /**
     * Watcher on the v-model
     * @param value - Object
     */
    value(value) {
      this.formData = {
        ...value
      };
    },
    /**
     * Watcher on the dates_range field
     * @param dates_range - Object
     */
    dates_range(dates_range) {
      this.formData.filters[0].items = [
        dates_range.start_date,
        dates_range.end_date
      ];
    },
    /**
     * Watcher on the formData.search_text field
     * @param search_text - String
     */
    'formData.search_text'(search_text) {
      if (search_text && !search_text.length) {
        this.$emit('onEmptySearchText', true);
      }
    }
  },
  computed: {
    ...mapGetters(['filter_categories', 'materials_keywords']),
    filter_category() {
      const { filter_categories, showSelectedCategory } = this;

      if (filter_categories && filter_categories.results && showSelectedCategory) {
        return filter_categories.results.find(
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
      const { filter_categories, hideFilter, activeCategoryExternalId } = this;

      if (!filter_categories || _.isEmpty(filter_categories.results) || hideFilter) {
        return false
      }
      if(activeCategoryExternalId) {
        let ix = filter_categories.results.findIndex(
          item => item.external_id === activeCategoryExternalId
        );
        return filter_categories.results[ix];
      }
      return filter_categories.results[0];

    },
    /**
     * Get keywords
     * @returns {default.getters.materials_keywords|Array}
     */
    keywords() {
      return this.materials_keywords || [];
    }
  }
};
