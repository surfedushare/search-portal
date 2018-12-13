import { formatDate } from './_helpers';

export default {
  state: {
    my_collections: false,
    my_collection: false,
    my_collection_materials: false,
    my_collection_materials_loading: false
  },
  getters: {
    my_collections(state) {
      return state.my_collections;
    },
    my_collection(state) {
      return state.my_collection;
    },
    my_collection_materials(state) {
      return state.my_collection_materials;
    },
    my_collection_materials_loading(state) {
      return state.my_collection_materials_loading;
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
      const collection = await this.$axios.$get(`collections/${id}/`);
      commit('SET_MY_COLLECTION', collection);
      return collection;
    },
    async deleteMyCollection({ state, commit }, id) {
      const collection = await this.$axios.$delete(`collections/${id}/`);
      commit('DELETE_MY_COLLECTION', id);
      return collection;
    },
    async postMyCollection({ state, commit }, data) {
      const collection = await this.$axios.$post(`collections/`, data);
      commit('ADD_MY_COLLECTION', collection);
      return collection;
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
    },
    async getMaterialInMyCollection(
      { state, commit },
      { id, page_size, page }
    ) {
      commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', true);
      const materials = await this.$axios.$get(`collections/${id}/materials/`, {
        params: {
          page_size,
          page
        }
      });
      commit('GET_MATERIAL_TO_MY_COLLECTION', materials);
      commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', false);
      return materials;
    },
    async getNextPeMaterialInMyCollection(
      { state, commit },
      { id, page_size, page }
    ) {
      commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', true);
      const materials = await this.$axios.$get(`collections/${id}/materials/`, {
        params: {
          page_size,
          page
        }
      });
      commit('SET_NEXT_PAGE_MATERIALS_TO_MY_COLLECTION', materials);
      commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', false);
      return materials;
    }
  },
  mutations: {
    SET_MY_COLLECTIONS(state, payload) {
      state.my_collections = payload;
    },
    SET_MY_COLLECTION(state, payload) {
      state.my_collection = payload;
    },
    ADD_MY_COLLECTION(state, payload) {
      state.my_collections = {
        ...state.my_collections,
        results: [payload, ...state.my_collections.results]
      };
    },
    DELETE_MY_COLLECTION(state, id) {
      state.my_collections = {
        ...state.my_collections,
        results: state.my_collections.results
          ? state.my_collections.results.filter(
              collection => collection.id !== id
            )
          : []
      };
    },
    SET_MATERIAL_TO_MY_COLLECTION(state, payload) {
      // state.my_collections = payload;
    },
    GET_MATERIAL_TO_MY_COLLECTION(state, payload) {
      const records = payload.records || payload;
      state.my_collection_materials = Object.assign({}, payload, {
        records: records.map(record => {
          return Object.assign(
            { date: formatDate(record.publish_datetime) },
            record
          );
        })
      });
    },
    SET_NEXT_PAGE_MATERIALS_TO_MY_COLLECTION(state, payload) {
      const records = state.my_collection_materials.records || [];
      state.my_collection_materials = Object.assign({}, payload, {
        records: [
          ...records,
          ...payload.records.map(record => {
            return Object.assign(
              { date: formatDate(record.publish_datetime) },
              record
            );
          })
        ]
      });
    },
    SET_MATERIAL_TO_MY_COLLECTION_LOADING(state, payload) {
      state.my_collection_materials_loading = payload;
    }
  }
};
