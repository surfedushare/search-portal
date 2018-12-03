import { mapGetters } from 'vuex';
import { debounce } from './../../_helpers';
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
    value: {
      type: Object,
      default: () => ({
        page_size: 10,
        page: 1,
        filters: [{ external_id: null }],
        search_text: []
      })
    }
  },
  mounted() {
    this.$store.dispatch('getFilterCategories');
  },
  data() {
    return {
      filter: {},
      active_category_id: null,
      formData: {
        ...this.value
      }
    };
  },
  methods: {
    onSearch(search, loading) {
      loading(true);
      this.search(loading, search, this);
    },
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
      // this.$store.dispatch('searchMaterials', this.formData)
      this.$router.push({
        path: '/materials/search/',
        query: Object.assign({}, this.formData, {
          filters: JSON.stringify(this.formData.filters),
          search_text: JSON.stringify(this.formData.search_text)
        })
      });
      this.$emit('input', this.formData);
    }
  },
  watch: {
    active_category(category) {
      if (category) {
        // this.formData.filters[0].external_id = category.external_id;
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
    }
  },
  computed: {
    ...mapGetters(['filter_categories', 'materials_keywords']),

    active_category() {
      const { filter_categories, hideFilter } = this;
      if (filter_categories && filter_categories.results && !hideFilter) {
        const { external_id } = this.formData.filters[0];
        if (external_id) {
          return filter_categories.results.find(
            item => item.external_id === external_id
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
    keywords() {
      return this.materials_keywords || [];
    }
  }
};
