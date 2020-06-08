import { mapGetters } from 'vuex';
import { generateSearchMaterialsQuery } from '../_helpers';
import DatesRange from '~/components/DatesRange';
import _ from 'lodash';


export default {
  name: 'filter-categories',
  components: { DatesRange },
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
      const { categories, publisherdate } = this;
      if (categories) {
        let filters = [];

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
  computed: {
    ...mapGetters([
      'filter_categories',
      'isAuthenticated',
      'materials'
    ]),
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
