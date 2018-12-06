export default {
  state: {
    my_collections: false,
    my_collection: false
  },
  getters: {
    my_collections(state) {
      return state.my_collections;
    },
    my_collection(state) {
      return state.my_collection;
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
    async getMyCollection({ state, commit }, id) {
      if (!state.my_collection) {
        const collection = await this.$axios.$get(`collections/${id}/`);
        commit('SET_MY_COLLECTION', collection);
        return collection;
      }
      return state.my_collection;
    },
    async setMaterialInMyCollection(
      { state, commit },
      { collection_id, data }
    ) {
      const material = await this.$axios.$post(
        `collections/${collection_id}/materials/`,
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
    SET_MY_COLLECTION(state, payload) {
      state.my_collection = payload;
    },
    SET_MATERIAL_TO_MY_COLLECTION(state, payload) {
      // state.my_collections = payload;
    }
  }
};
