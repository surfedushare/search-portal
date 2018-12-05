export default {
  state: {
    my_collections: null
  },
  getters: {
    my_collections(state) {
      return state.my_collections;
    }
  },
  actions: {
    async getMyCollections({ state, commit }) {
      if (!state.my_collections) {
        const collections = await this.$axios.$get('collections/', {
          params: { is_owner: true }
        });
        commit('SET_MY_COLLECTIONS', collections);
        return collections;
      }
      return state.my_collections;
    },
    async setMaterialInMyCollection(
      { state, commit },
      { collection_id, data }
    ) {
      const material = await this.$axios.$get(
        `collections/${collection_id}/`,
        data
      );
      commit('SET_MATERIAL_TO_MY_COLLECTION', material);
      return data;
    }
  },
  mutations: {
    SET_MY_COLLECTIONS(state, payload) {
      state.my_collections = payload;
    },
    SET_MATERIAL_TO_MY_COLLECTION(state, payload) {
      // state.my_collections = payload;
    }
  }
};
