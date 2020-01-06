import { mapGetters } from 'vuex';
import { generateSearchMaterialsQuery } from '../_helpers';
import DatesRange from '~/components/DatesRange';
import _ from 'lodash';


export default {
  name: 'filter-categories',
  props: ['showPopupSaveFilter', 'full-filter'],
  components: { DatesRange },
  mounted() {
    if (this.isAuthenticated && !this.fullFilter) {
      this.$store.dispatch('getFilters');
    }
  },
  data() {
    const publisherdate = 'lom.lifecycle.contribute.publisherdate';
    return {
      publisherdate,
      visible_items: 20,
      data: {
        start_date: null,
        end_date: null
      }
    };
  },
  methods: {
    generateSearchMaterialsQuery,
    hasVisibleChildren(category) {
      if(!category.children.length) {
        return false;
      }
      return _.some(category.children, (child) => { return !child.is_hidden; })
    },
    onToggleCategory(category, update = true) {
      category.isOpen = !category.isOpen;
      _.forEach(category.children, (child) => { this.onToggleCategory(child, false); } );
      if(update) {
        this.$forceUpdate();
      }
    },
    onToggleShowAll(category) {
      category.showAll = !category.showAll;
      this.$forceUpdate();
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
          this.data = {
            start_date: publisherdate_item.items[0],
            end_date: publisherdate_item.items[1]
          };
        }

        filters = Object.assign({}, this.value, {
          filters
        });

        this.$router.push(this.generateSearchMaterialsQuery(filters));

        this.$emit('input', filters);

        return filters;
      }
    },
    onChange(event, parent) {
      if(!_.isNil(parent)) {
        parent.selected = !parent.selected;
      }
      this.$store.commit('SET_FILTER_SELECTED', event.target.dataset.categoryId);
      this.executeSearch();
    },
    onDateChange() {
      this.executeSearch();
    },
    executeSearch() {

      let searchText = this.$store.getters.materials.search_text;
      let ordering = this.$store.getters.materials.ordering;
      let searchRequest = {
        search_text: searchText,
        ordering: ordering,
        filters: this.$store.getters.search_filters
      };

      // Execute search
      this.$router.push(this.generateSearchMaterialsQuery(searchRequest));
      this.$emit('input', searchRequest);  // actual search is done by the parent page

    },
    /**
     * Get the full filter info
     * @param e - event
     */
    onFilterSelected(e) {
      this.$store.dispatch('getFilter', { id: e.target.value });
    },
    /**
     * Event the reset filter
     */
    resetFilter() {
      this.$router.push(
        this.generateSearchMaterialsQuery({
          filters: [],
          search_text: this.$store.getters.materials.search_text
        }),
        () => { location.reload(); },
        () => { location.reload(); }
      );
    },
    isShowCategoryItem({ category, item, indexItem }) {
      return (
        !item.is_empty && (category.showAll || indexItem < this.visible_items)
      );
    },
    getTitleTranslation( category, language ) {
      if (!_.isNil(category.title_translations) && !_.isEmpty(category.title_translations)){
        return category.title_translations[language];
      }
      return category.name
    }
  },
  watch: {
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
            search_text: active_filter.search_text || value.search_text || []
          }
        );

        this.$router.push(this.generateSearchMaterialsQuery(filters));

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
    active_filter_id() {
      const { active_filter } = this;
      if (active_filter) {
        return active_filter.id || '';
      }

      return '';
    },
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
                items: item.children.map(
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
      // Return categories which builds the filter tree
      return (this.filter_categories) ?
        _.filter(this.$store.getters.filter_categories.results, {is_hidden: false}) :
        [];
    }
  }
};
