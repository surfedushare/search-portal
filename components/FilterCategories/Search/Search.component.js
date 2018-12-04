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
    'active-category-external-id': {
      type: String
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
      filter: {},
      active_category_id: null,
      formData: {
        ...this.value
      },
      dates_range: {
        start_date: null,
        end_date: null
      }
    };
  },
  methods: {
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
    onSubmit() {
      this.$router.push(generateSearchMaterialsQuery(this.formData));
      this.$emit('input', this.formData);
    },
    onChangeCategory(event) {
      this.formData.filters = [
        {
          ...this.formData.filters[0],
          external_id: event.target.value
        }
      ];
    }
  },
  watch: {
    active_category(category) {
      if (category) {
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
    },
    dates_range(dates_range) {
      this.formData.filters[0].items = [
        dates_range.start_date,
        dates_range.end_date
      ];
    }
  },
  computed: {
    ...mapGetters(['filter_categories', 'materials_keywords']),

    /**
     * Get the active category
     * @returns {*} - false or active category
     */
    active_category() {
      const { filter_categories, hideFilter, activeCategoryExternalId } = this;

      if (filter_categories && filter_categories.results && !hideFilter) {
        const { external_id } = this.formData.filters[0];
        const current_external_id = external_id || activeCategoryExternalId;
        if (current_external_id) {
          return filter_categories.results.find(
            item => item.external_id === current_external_id
          );
        }
        if (external_id !== null) {
          this.formData.filters[0].external_id =
            filter_categories.results[0].external_id;
        }
        return filter_categories.results[0];
      }
      return false;
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
