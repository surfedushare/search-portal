export default {
  state: {
    filters: null
  },
  getters: {
    filters(state) {
      return state.materials;
    }
  },
  actions: {
    async getFilters({ commit }) {
      const filters = await this.$axios.$get('filters/');
      commit('SET_FILTERS', filters);
    },
    async postFilter({ commit }, data) {
      const filter = await this.$axios.$post('filters/', data);
      commit('EXTEND_FILTERS', filter);
    }
  },
  mutations: {
    SET_FILTERS(state, payload) {
      state.filters = payload;
    },
    EXTEND_FILTERS(state, payload) {
      state.filters = payload;
    }
  }
};
