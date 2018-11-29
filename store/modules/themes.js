export default {
  state: {
    themes: null,
    theme: null
  },
  getters: {
    themes(state) {
      return state.themes;
    },
    theme(state) {
      return state.theme;
    }
  },
  actions: {
    async getThemes({ commit }) {
      const themes = await this.$axios.$get('themes/');
      commit('SET_THEMES', themes);
    },
    async getTheme({ commit }, id) {
      const theme = await this.$axios.$get(`themes/${id}`);
      commit('SET_THEME', theme);
    }
  },
  mutations: {
    SET_THEMES(state, payload) {
      state.themes = payload;
    },
    SET_THEME(state, payload) {
      state.theme = payload;
    }
  }
};
