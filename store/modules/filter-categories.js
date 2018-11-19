export default {
  state: {
    filter_categories: null
  },
  getters: {
    filter_categories(state) {
      return state.filter_categories
    }
  },
  actions: {
    async getFilterCategories({ commit }) {
      const filter = await this.$axios.$get('filter-categories/')
      commit('SET_FILTER_CATEGORIES', filter)
    }
  },
  mutations: {
    SET_FILTER_CATEGORIES(state, payload) {
      state.filter_categories = payload
    }
  }
}
