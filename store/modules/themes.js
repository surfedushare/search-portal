export default {
  state: {
    themes: null,
    theme: null,
    themeDisciplines: null,
    themeCommunities: null,
    themeCollections: null
  },
  getters: {
    themes(state) {
      return state.themes;
    },
    theme(state) {
      return state.theme;
    },
    themeDisciplines(state) {
      return state.themeDisciplines;
    },
    themeCommunities(state) {
      return state.themeCommunities;
    },
    themeCollections(state) {
      return state.themeCollections;
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
    },
    async getThemeDisciplines({ commit }, id) {
      const themeDisciplines = await this.$axios.$get(
        `themes/${id}/disciplines`
      );
      commit('SET_DISCIPLINES', themeDisciplines);
    },
    async getThemeCommunities({ commit }, id) {
      const themeCommunities = await this.$axios.$get(
        `themes/${id}/communities`
      );
      commit('SET_COMMUNITIES', themeCommunities);
    },
    async getThemeCollections({ commit }, id) {
      const themeCollections = await this.$axios.$get(
        `themes/${id}/community-collections`
      );
      commit('SET_COLLECTIONS', themeCollections);
    }
  },
  mutations: {
    SET_THEMES(state, payload) {
      state.themes = payload;
    },
    SET_THEME(state, payload) {
      state.theme = payload;
    },
    SET_DISCIPLINES(state, payload) {
      state.themeDisciplines = payload;
    },
    SET_COMMUNITIES(state, payload) {
      state.themeCommunities = payload;
    },
    SET_COLLECTIONS(state, payload) {
      state.themeCollections = payload;
    }
  }
};
