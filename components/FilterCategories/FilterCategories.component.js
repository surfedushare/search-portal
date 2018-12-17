import { mapGetters } from 'vuex';
import { generateSearchMaterialsQuery } from '../_helpers';

export default {
  name: 'filter-categories',
  props: ['value', 'showPopupSaveFilter', 'full-filter'],
  components: {},
  mounted() {
    if (this.isAuthenticated && !this.fullFilter) {
      this.$store.dispatch('getFilters');
    }
  },
  data() {
    return {
      publisherdate: 'lom.lifecycle.contribute.publisherdate',
      selected: [],
      show_all: [],
      isShow: false,
      isInit: false,
      visible_items: 10
    };
  },
  methods: {
    /**
     * Open/close filter category
     * @param id filter category
     */
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
     * open/collapse category items
     * @param id filter category
     */
    onToggleShowAll(id) {
      const show_all = [...this.show_all];
      const index = show_all.indexOf(id);
      if (index !== -1) {
        this.show_all = [
          ...show_all.slice(0, index),
          ...show_all.slice(index + 1)
        ];
      } else {
        show_all.push(id);
        this.show_all = show_all;
      }
    },
    /**
     * Set filter for v-model
     * @returns {*} - filters
     */
    setFilter() {
      const { categories, filter, publisherdate } = this;
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

        const publisherdate_item = this.value.filters.find(
          item => item.external_id === publisherdate
        );

        if (publisherdate_item) {
          filters.push({
            external_id: publisherdate,
            items: [...publisherdate_item.items]
          });
        }

        filters = Object.assign({}, this.value, {
          filters
        });

        this.$router.push(generateSearchMaterialsQuery(filters));

        this.$emit('input', filters);

        return filters;
      }
    },
    onChange() {
      this.setFilter();
    },
    /**
     * Get the full filter info
     * @param e - event
     */
    onFilterSelected(e) {
      this.$store.dispatch('getFilter', { id: e.target.value });
    },
    resetFilter() {
      this.$route.push('/materials/search/');
      location.reload();
    },
    isShowCategoryItem({ category, item, indexItem }) {
      return (
        !item.is_empty && (category.show_all || indexItem < this.visible_items)
      );
    }
  },
  watch: {
    /**
     * Watcher on change parent v-model
     * @param value
     */
    value(value) {
      const { isInit } = this;
      if (value && value.filters && !isInit) {
        this.selected = value.filters.map(filter => filter.external_id);
        this.isInit = true;
      }
    },
    /**
     * Watcher on change user authentication
     * @param isAuthenticated
     */
    isAuthenticated(isAuthenticated) {
      if (isAuthenticated && !this.fullFilter) {
        this.$store.dispatch('getFilters');
      }
    },
    /**
     * Generating search query on change the active filter
     * @param active_filter
     */
    active_filter(active_filter) {
      const { filter_categories, publisherdate, value } = this;
      if (active_filter && active_filter.items && filter_categories) {
        const publisherdate_item = filter_categories.results.find(
          item => item.external_id === publisherdate
        );
        const normailze_filter = active_filter.items.reduce((prev, next) => {
          prev[next.category_id] = prev[next.category_id] || [];
          prev[next.category_id].push(next.category_item_id);
          return prev;
        }, {});
        const filters = filter_categories.results.reduce(
          (search, category) => {
            const category_items = normailze_filter[category.id];
            if (category_items) {
              search.filters.push({
                external_id: category.external_id,
                items: category.items
                  .filter(item => category_items.indexOf(item.id) !== -1)
                  .map(item => item.external_id)
              });
            }
            return search;
          },
          {
            page: 1,
            page_size: value.page_size,
            filters: [
              {
                external_id: publisherdate_item.external_id,
                items: [active_filter.start_date, active_filter.end_date]
              }
            ],
            search_text: active_filter.search_text || []
          }
        );

        this.$router.push(generateSearchMaterialsQuery(filters));

        this.$emit('input', filters);
      }
    }
  },
  computed: {
    ...mapGetters([
      'filter_categories',
      'isAuthenticated',
      'filters',
      'active_filter',
      'materials'
    ]),
    /**
     * generate filter items
     * @returns {*}
     */
    filter() {
      const { value, filtered_categories } = this;
      if (value && value.filters && filtered_categories) {
        const filter = value.filters.reduce((prev, next) => {
          prev[next.external_id] = next;

          return prev;
        }, {});

        return filtered_categories.map(item => {
          const current_item = filter[item.external_id];

          return current_item && current_item.items
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
    /**
     * generate filtered categories
     * @returns {*}
     */
    filtered_categories() {
      const { filter_categories, publisherdate } = this;
      if (filter_categories) {
        return filter_categories.results.map(item => {
          return {
            ...item,
            hide: item.external_id === publisherdate
          };
        });
      }
      return false;
    },
    /**
     * generate categories
     * @returns {*}
     */
    categories() {
      const { selected, show_all, filtered_categories, materials } = this;
      if (selected && filtered_categories && materials && materials.filters) {
        const not_empty_ids = materials.filters.reduce((prev, next) => {
          prev.push(...next.items.map(item => item.external_id));
          return prev;
        }, []);

        return Object.assign({}, filtered_categories, {
          results: filtered_categories.map(category => {
            return Object.assign({}, category, {
              selected: selected.indexOf(category.external_id) !== -1,
              show_all: show_all.indexOf(category.id) !== -1,
              items: [
                ...category.items.map(item => {
                  return {
                    ...item,
                    is_empty: not_empty_ids.indexOf(item.external_id) === -1
                  };
                })
              ]
            });
          })
        });
      }
      return false;
    }
  }
};
