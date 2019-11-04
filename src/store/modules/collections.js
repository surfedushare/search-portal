import {
  formatDate,
  validateID,
  validateIDString,
  validateParams,
  decodeAuthor
} from './_helpers';


export default {
  state: {
    my_collections: false,
    my_collection: false,
    my_collection_materials: false,
    my_collection_materials_loading: false,
    my_collections_loading: false
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
    },
    my_collections_loading(state) {
      return state.my_collections_loading;
    }
  },
  actions: {
    async getMyCollections({ state, commit }) {
      commit('SET_MY_COLLECTIONS_LOADING', true);
      const collections = await this.$axios.$get('collections/', {
        params: {
          timestamp: Date.now(),
          is_owner: true
        }
      });
      commit('SET_MY_COLLECTIONS', collections);
      commit('SET_MY_COLLECTIONS_LOADING', false);
      return collections;
    },
    async getMyCollectionsNextPage({ state, commit }) {
      commit('SET_MY_COLLECTIONS_LOADING', true);
      const collections = await this.$axios.$get(state.my_collections.next, {
        params: {
          timestamp: Date.now(),
          is_owner: true
        }
      });

      commit('SET_MY_COLLECTIONS_NEXT', collections);
      commit('SET_MY_COLLECTIONS_LOADING', false);
      return collections;
    },
    async getMyCollection({ state, commit }, id) {
      if (validateID(id)) {
        const collection = await this.$axios.$get(`collections/${id}/`);
        commit('SET_MY_COLLECTION', collection);
        return collection;
      } else {
        console.error('Validate error: ', id);
      }
    },
    async setCollectionSocial({ commit }, { id, params }) {
      if (validateID(id) && validateParams(params)) {
        const collection = await this.$axios.$get(`collections/${id}/`, {
          params
        });
        commit('SET_MY_COLLECTION', collection);
        return collection;
      } else {
        console.error('Validate error: ', { id, params });
      }
    },
    async putMyCollection({ state, commit }, data) {
      if (validateID(data.id) && validateParams(data)) {
        const collection = await this.$axios.$put(
          `collections/${data.id}/`,
          data
        );
        commit('SET_MY_COLLECTION', collection);
        return collection;
      } else {
        console.error('Validate error: ', data);
      }
    },
    async checkMaterialInCollection({ state, commit }, id) {
      if (validateIDString(id)) {
        const collection = await this.$axios.$get('collections/', {
          params: {
            is_owner: true,
            material_id: id
          }
        });
        return collection;
      } else {
        console.error('Validate error: ', id);
      }
    },
    async deleteMyCollection({ state, commit }, id) {
      if (validateID(id)) {
        const collection = await this.$axios.$delete(`collections/${id}/`);
        commit('DELETE_MY_COLLECTION', id);
        return collection;
      } else {
        console.error('Validate error: ', id);
      }
    },
    async postMyCollection({ state, commit }, data) {
      if (validateParams(data)) {
        const collection = await this.$axios.$post(`collections/`, data);
        commit('ADD_MY_COLLECTION', collection);
        return collection;
      } else {
        console.error('Validate error: ', data);
      }
    },
    async setMaterialInMyCollection(
      { state, commit },
      { collection_id, data }
    ) {
      if (validateID(collection_id) && validateParams(data)) {
        const material = await this.$axios.$post(
          `collections/${collection_id}/materials/`,
          data
        );
        commit('SET_MATERIAL_TO_MY_COLLECTION', material);
        return data;
      } else {
        console.error('Validate error: ', { collection_id, data });
      }
    },
    async removeMaterialFromMyCollection(
      { state, commit },
      { collection_id, data }
    ) {
      if (validateID(collection_id) && validateParams(data)) {
        return this.$axios.$delete(`collections/${collection_id}/materials/`, {
          data
        });
      } else {
        console.error('Validate error: ', { collection_id, data });
      }
    },
    async getMaterialInMyCollection({ state, commit }, { id, params }) {
      if (validateIDString(id) && validateParams(params)) {
        commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', true);
        const materialsInfo = await this.$axios.$get(
          `collections/${id}/materials/`,
          {
            params: {
              ...params,
              timestamp: Date.now()
            }
          }
        );
        commit('SET_MATERIAL_TO_MY_COLLECTION', materialsInfo);
        commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', false);
        return materialsInfo;
      } else {
        console.error('Validate error: ', { id, params });
      }
    },
    async searchMaterialInMyCollection({ state, commit }, { id, params }) {
      if (validateIDString(id) && validateParams(params)) {
        commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', true);
        const materials = await this.$axios.$post(
          `collections/${id}/search/`,
          params
        );
        commit('GET_MATERIAL_TO_MY_COLLECTION', materials);
        commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', false);
        return materials;
      } else {
        console.error('Validate error: ', { id, params });
      }
    },
    async getNextPeMaterialInMyCollection({ state, commit }, { id, params }) {
      if (validateIDString(id) && validateParams(params)) {
        commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', true);
        const materials = await this.$axios.$get(
          `collections/${id}/materials/`,
          {
            params
          }
        );
        commit('SET_NEXT_PAGE_MATERIALS_TO_MY_COLLECTION', materials);
        commit('SET_MATERIAL_TO_MY_COLLECTION_LOADING', false);
        return materials;
      } else {
        console.error('Validate error: ', { id, params });
      }
    }
  },
  mutations: {
    SET_MY_COLLECTIONS(state, payload) {
      state.my_collections = payload;
    },
    SET_MY_COLLECTIONS_NEXT(state, payload) {
      state.my_collections = {
        ...state.my_collections,
        next: payload.next,
        results: [...state.my_collections.results, ...payload.results]
      };
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
      const records = payload.records || payload;
      records.forEach(decodeAuthor);
      state.my_collection_materials = payload;
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
    SET_MY_COLLECTIONS_LOADING(state, payload) {
      state.my_collections_loading = payload;
    },
    SET_MATERIAL_TO_MY_COLLECTION_LOADING(state, payload) {
      state.my_collection_materials_loading = payload;
    }
  }
};
