export default {
  state: {
    communities: null
  },
  getters: {
    communities(state) {
      return state.communities;
    }
  },
  actions: {
    async getCommunities({ commit }, { params }) {
      const communities = await this.$axios.$get('communities/', { params });
      commit('SET_COMMUNITIES', communities);
    }
  },
  mutations: {
    SET_COMMUNITIES(state, payload) {
      state.communities = payload;
    }
  }
};
