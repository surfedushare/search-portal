export default {
  state: {
    materials: null,
    materials_keywords: null
  },
  getters: {
    materials(state) {
      return state.materials
    },
    materials_keywords(state) {
      return state.materials_keywords
    }
  },
  actions: {
    async getMaterials({ commit }) {
      const materials = await this.$axios.$get('materials/')
      commit('SET_MATERIALS', materials)
    },
    async searchMaterials({ commit }, search) {
      const materials = await this.$axios.$post('materials/search/', search)
      commit('SET_MATERIALS', materials)
    },
    async searchMaterialsKeywords({ commit }, search) {
      const keywords = await this.$axios.$get('materials/keywords/', search)
      commit('SET_MATERIALS_KEYWORDS', keywords)
    }
  },
  mutations: {
    SET_MATERIALS(state, payload) {
      state.materials = payload
    },
    SET_MATERIALS_KEYWORDS(state, payload) {
      state.materials_keywords = payload
    }
  }
}
