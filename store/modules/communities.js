export default {
  state: {
    communities: null
  },
  getters: {
    communities(state) {
      return state.communities
    }
  },
  actions: {
    async getCommunities({ commit }) {
      const communities = await this.$axios.$get('communities/')
      commit('SET_COMMUNITIES', communities)
    }
  },
  mutations: {
    SET_COMMUNITIES(state, payload) {
      state.communities = payload
    }
  }
}
