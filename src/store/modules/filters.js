import { validateID, validateParams } from './_helpers';

export default {
  state: {
    filters: null,
    active_filter: {
      id: false,
      start_date: null,
      end_date: null
    }
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
    async getFilters({ state, commit }) {
      if (state.filters) {
        return state.filters;
      }
      const filters = await this.$axios.$get('filters/');
      commit('SET_FILTERS', filters);
      return filters;
    },
    async getFilter({ commit }, { id }) {
      if (validateID(id)) {
        if (id && id.length) {
          const filter = await this.$axios.$get(`filters/${id}/`);
          this.dispatch('setActiveFilter', filter);
          commit('MERGE_FILTERS', filter);
        } else {
          commit('SET_FILTER', { id });
        }
      } else {
        console.error('Validate error: ', { id });
      }
    },
    async postMyFilter({ commit }, data) {
      if (validateParams(data)) {
        const filter = await this.$axios.$post(`filters/`, data);
        commit('ADD_MY_FILTER', filter);
      } else {
        console.error('Validate error: ', data);
      }
    },
    async saveMyFilter({ commit }, data) {
      if (validateParams(data)) {
        const filter = await this.$axios.$put(`filters/${data.id}/`, data);
        commit('SET_FILTER', filter);
        this.dispatch('setActiveFilter', filter);
        return filter;
      } else {
        console.error('Validate error: ', data);
      }
    },
    async deleteMyFilter({ commit }, id) {
      if (validateID(id)) {
        await this.$axios.$delete(`filters/${id}/`);
        commit('DELETE_MY_FILTER', id);
        this.dispatch('setActiveFilter', null);
      } else {
        console.error('Validate error: ', id);
      }
    },
    async getDetailFilter({ commit }, { id }) {
      if (validateID(id)) {
        if (id && id.length) {
          const filter = await this.$axios.$get(`filters/${id}/`);
          this.dispatch('setActiveFilter', filter);
          return filter;
        }
      } else {
        console.error('Validate error: ', id);
      }
    },
    async postFilter({ commit }, { title, items, materials_count }) {
      if (validateParams({ title, items, materials_count })) {
        const { filters } = items;
        const external_ids = filters.map(item => item.external_id);

        const resp = this.getters['filter_categories'].results.reduce(
          (filter, category) => {
            const { external_id, items } = category;
            const index = external_ids.indexOf(external_id);
            if (index !== -1) {
              const filter_items = filters[index].items;

              if (filter_items) {
                filter.items.push(
                  ...items.reduce((arr, item) => {
                    if (filter_items.indexOf(item.external_id) !== -1) {
                      arr.push({ category_item_id: item.id });
                    }
                    return arr;
                  }, [])
                );
              }

              if (external_id === 'lom.lifecycle.contribute.publisherdate') {
                filter.start_date = filter_items[0];
                filter.end_date = filter_items[1];
              }
            }
            return filter;
          },
          {
            title,
            materials_count,
            items: [],
            search_text: items.search_text
          }
        );
        const filter = await this.$axios.$post('filters/', resp);
        this.dispatch('setActiveFilter', filter);
        commit('EXTEND_FILTERS', filter);
      } else {
        console.error('Validate error: ', { title, items, materials_count });
      }
    },
    setActiveFilter({ commit }, filter) {
      commit('SET_ACTIVE_FILTER', filter);
    }
  },
  mutations: {
    SET_FILTERS(state, payload) {
      state.filters = payload;
    },
    SET_FILTER(state, payload) {
      const filters = state.filters || [];
      state.filters = filters.reduce(
        (prev, filter) => {
          if (filter.id !== payload.id) {
            prev.push(filter);
          }
          return prev;
        },
        [payload]
      );
    },
    ADD_MY_FILTER(state, payload) {
      state.filters = [payload, ...state.filters];
    },
    DELETE_MY_FILTER(state, id) {
      state.filters = state.filters.filter(filter => filter.id !== id);
    },
    EXTEND_FILTERS(state, payload) {
      state.filters = [...state.filters, payload];
    },
    MERGE_FILTERS(state, payload) {
      state.filters = state.filters.map(filter => {
        if (filter.id === payload.id) {
          return payload;
        }

        return filter;
      });
    },
    SET_ACTIVE_FILTER(state, payload) {
      state.active_filter = payload;
    }
  }
};
