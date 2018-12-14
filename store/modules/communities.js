export default {
  state: {
    communities: null,
    community_info: null,
    community_themes: null,
    community_disciplines: null,
    community_collections: null
  },
  getters: {
    communities(state) {
      return state.communities;
    },
    community_info(state) {
      return state.community_info;
    },
    community_themes(state) {
      return state.community_themes;
    },
    community_disciplines(state) {
      return state.community_disciplines;
    },
    community_collections(state) {
      return state.community_collections;
    }
  },
  actions: {
    async getCommunities({ commit }, { params = {} } = {}) {
      const communities = await this.$axios.$get('communities/', { params });
      commit('SET_COMMUNITIES', communities);
      return communities;
    },
    async putCommunities({ commit }, { id, data = {} } = {}) {
      console.log(data, id);
      const communities = await this.$axios.$put(`communities/${id}/`, data);
      commit('SET_COMMUNITIES', communities);
      return communities;
    },
    async getCommunity({ commit }, id) {
      const community_info = await this.$axios.$get(`communities/${id}/`);
      commit('SET_COMMUNITY', community_info);
    },
    async getCommunityThemes({ commit }, id) {
      const community_themes = await this.$axios.$get(
        `communities/${id}/themes/`
      );
      commit('SET_COMMUNITY_THEMES', community_themes);
    },
    async getCommunityDisciplines({ commit }, id) {
      const community_disciplines = await this.$axios.$get(
        `communities/${id}/disciplines/`
      );
      commit('SET_COMMUNITY_DISCIPLINES', community_disciplines);
    },
    async getCommunityCollections({ commit }, id) {
      const community_collections = await this.$axios.$get(
        `communities/${id}/collections/`
      );
      commit('SET_COMMUNITY_COLLECTIONS', community_collections);
    }
  },
  mutations: {
    SET_COMMUNITIES(state, payload) {
      state.communities = payload;
    },
    SET_COMMUNITY(state, payload) {
      state.community_info = payload;
    },
    SET_COMMUNITY_DISCIPLINES(state, payload) {
      state.community_disciplines = payload;
    },
    SET_COMMUNITY_THEMES(state, payload) {
      state.community_themes = payload;
    },
    SET_COMMUNITY_COLLECTIONS(state, payload) {
      state.community_collections = payload;
    }
  }
};
