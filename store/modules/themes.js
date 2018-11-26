export default {
  state: {
    themes: null
  },
  getters: {
    themes(state) {
      return state.themes;
    }
  },
  actions: {
    async getThemes({ commit }) {
      const themes = await this.$axios.$get('themes/');
      commit('SET_THEMES', themes);
    }
  },
  mutations: {
    SET_THEMES(state, payload) {
      state.themes = payload;
    }
  }
};
