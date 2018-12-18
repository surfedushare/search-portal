import { mapGetters } from 'vuex';
import { debounce, generateSearchMaterialsQuery } from './../../_helpers';
import DatesRange from './../../DatesRange';
export default {
  name: 'direct-search',
  props: {
    value: {
      type: Object,
      default: () => ({
        page_size: 10,
        page: 1,
        filters: [],
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
      this.$router.push(generateSearchMaterialsQuery(this.formData));
      this.$emit('input', this.formData);
    },
    /**
     * Event on changing the keywords
     */
    setKeywords() {
      this.$emit('input', this.formData);
    },
    /**
     * Event on changing the category
     * @param event
     */
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
    /**
     * Watcher on the active category item
     * @param category - Object
     */
    active_category(category) {
      if (category) {
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
    }
  },
  computed: {
    ...mapGetters(['filter_categories', 'materials_keywords']),

    /**
     * Get keywords
     * @returns {default.getters.materials_keywords|Array}
     */
    keywords() {
      return this.materials_keywords || [];
    }
  }
};
