export default {
  state: {
    filter_categories: null,
    disciplines: null,
    educationallevels: null
  },
  getters: {
    filter_categories(state) {
      return state.filter_categories;
    },
    disciplines(state) {
      return state.disciplines;
    },
    educationallevels(state) {
      return state.educationallevels;
    }
  },
  actions: {
    async getFilterCategories({ state, commit }) {
      if (!state.filter_categories) {
        const filter = await this.$axios.$get('filter-categories/');
        commit('SET_FILTER_CATEGORIES', filter);
      }
    }
  },
  mutations: {
    SET_FILTER_CATEGORIES(state, payload) {
      state.filter_categories = payload;
      const disciplines = payload.results.find(
        item => item.external_id.search('discipline.id') !== -1
      );
      state.disciplines = Object.assign({}, disciplines, {
        items: disciplines.items.reduce((prev, next) => {
          prev[next.external_id] = next;
          return prev;
        }, {})
      });
      const educationallevels = payload.results.find(
        item => item.external_id.search('educationallevel.id') !== -1
      );
      state.educationallevels = Object.assign({}, educationallevels, {
        items: educationallevels.items.reduce((prev, next) => {
          prev[next.external_id] = next;
          return prev;
        }, {})
      });
    }
  }
};
