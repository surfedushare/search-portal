export default {
  state: {
    filters: null,
    active_filter: null
  },
  getters: {
    filters(state) {
      return state.filters;
    },
    active_filter(state) {
      return state.active_filter;
    }
  },
  actions: {
    async getFilters({ commit }) {
      const filters = await this.$axios.$get('filters/');
      commit('SET_FILTERS', filters);
    },
    async getFilter({ commit }, { id }) {
      const filter = await this.$axios.$get(`filters/${id}/`);
      commit('SET_FILTER', filter);
    },
    async postFilter({ commit }, { title, items }) {
      const { filters } = items;
      const external_ids = filters.map(item => item.external_id);

      const resp = this.getters['filter_categories'].results.reduce(
        (filter, category) => {
          const { external_id, items } = category;
          const index = external_ids.indexOf(external_id);
          if (index !== -1) {
            const filter_items = filters[index].items;

            filter.items.push(
              ...items.reduce((arr, item) => {
                if (filter_items.indexOf(item.external_id) !== -1) {
                  arr.push({ category_item_id: item.id });
                }
                return arr;
              }, [])
            );

            if (external_id === 'lom.lifecycle.contribute.publisherdate') {
              filter.start_date = filter_items[0];
              filter.end_date = filter_items[1];
            }
          }
          return filter;
        },
        {
          title,
          items: [],
          search_text: items.search_text
        }
      );
      const filter = await this.$axios.$post('filters/', resp);
      commit('EXTEND_FILTERS', filter);
    },
    setActiveFilter({ commit }, filter) {
      commit('EXTEND_FILTERS', filter);
    }
  },
  mutations: {
    SET_FILTERS(state, payload) {
      state.filters = payload;
    },
    SET_FILTER(state, payload) {
      state.filters = state.filters.map(filter => {
        if (filter.id === payload.id) {
          return payload;
        }
        return filter;
      });
    },
    EXTEND_FILTERS(state, payload) {
      state.filters = [...state.filters, payload];
    }
  }
};
