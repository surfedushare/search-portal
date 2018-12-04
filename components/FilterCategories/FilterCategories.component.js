import { mapGetters } from 'vuex';

export default {
  name: 'filter-categories',
  props: ['value', 'showPopupSaveFilter'],
  components: {},
  mounted() {
    if (this.isAuthenticated) {
      this.$store.dispatch('getFilters');
    }
  },
  data() {
    return {
      selected: [],
      isShow: false
    };
  },
  methods: {
    onToggleCategory(id) {
      const selected = [...this.selected];
      const index = selected.indexOf(id);
      if (index !== -1) {
        this.selected = [
          ...selected.slice(0, index),
          ...selected.slice(index + 1)
        ];
      } else {
        selected.push(id);
        this.selected = selected;
      }
    },
    /**
     * Set filter for v-model
     * @returns {*} - filters
     */
    setFilter() {
      const { categories, filter } = this;
      if (filter && categories) {
        let filters = filter.reduce((prev, next) => {
          const hasItems = next.items.find(item => item);
          if (hasItems) {
            prev.push({
              external_id: next.external_id,
              items: next.items.reduce((prevChild, nextChild, index) => {
                if (nextChild) {
                  const category = categories.results.find(
                    category => category.external_id === next.external_id
                  );
                  prevChild.push(category.items[index].external_id);
                }
                return prevChild;
              }, [])
            });
          }
          return prev;
        }, []);

        filters = Object.assign({}, this.value, {
          filters
        });

        this.$emit('input', filters);

        return filters;
      }
    },
    onChange() {
      this.setFilter();
    }
  },
  watch: {},
  computed: {
    ...mapGetters(['filter_categories', 'isAuthenticated', 'filters']),
    filter() {
      const { value, filtered_categories } = this;
      if (value && filtered_categories) {
        const filter = value.filters.reduce((prev, next) => {
          prev[next.external_id] = next;

          return prev;
        }, {});

        return filtered_categories.map(item => {
          const current_item = filter[item.external_id];

          return current_item
            ? Object.assign({}, current_item, {
                items: item.items.map(
                  el => current_item.items.indexOf(el.external_id) !== -1
                )
              })
            : Object.assign({}, item, { items: [] });
        });
      }

      return false;
    },
    filtered_categories() {
      const { filter_categories } = this;
      if (filter_categories) {
        return filter_categories.results.filter(
          item => item.external_id !== 'lom.lifecycle.contribute.publisherdate'
        );
      }
      return false;
    },
    categories() {
      const { selected, filtered_categories } = this;
      if (selected && filtered_categories) {
        return Object.assign({}, filtered_categories, {
          results: filtered_categories.map(category => {
            return Object.assign({}, category, {
              selected: selected.indexOf(category.id) !== -1,
              items: [...category.items]
            });
          })
        });
      }
      return false;
    }
  }
};
