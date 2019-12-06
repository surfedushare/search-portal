import injector from 'vue-inject';
import {
  formatDate,
  validateID,
  validateIDString,
  validateParams,
  decodeAuthor
} from './_helpers';


const $log = injector.get('$log');


export default {
  state: {
    collection: false,
    collection_materials: false,
    collection_materials_loading: false,
  },
  getters: {
    collection(state) {
      return state.collection;
    },
    collection_materials(state) {
      return state.collection_materials;
    },
    collection_materials_loading(state) {
      return state.collection_materials_loading;
    }
  },
  actions: {
    async getCollection({ state, commit }, id) {
      if (validateID(id)) {
        const collection = await this.$axios.$get(`collections/${id}/`);
        commit('SET_COLLECTION', collection);
        return collection;
      } else {
        $log.error('Validate error: ', id);
      }
    },
    async setCollectionSocial({ commit }, { id, params }) {
      if (validateID(id) && validateParams(params)) {
        const collection = await this.$axios.$get(`collections/${id}/`, {
          params
        });
        commit('SET_COLLECTION', collection);
        return collection;
      } else {
        $log.error('Validate error: ', { id, params });
      }
    },
    async putMyCollection({ state, commit }, data) {
      if (validateID(data.id) && validateParams(data)) {
        const collection = await this.$axios.$put(
          `collections/${data.id}/`,
          data
        );
        commit('SET_COLLECTION', collection);
        return collection;
      } else {
        $log.error('Validate error: ', data);
      }
    },
    async checkMaterialInCollection({ state, commit }, id) {
      if (validateIDString(id)) {
        return await this.$axios.$get('collections/', {
          params: {
            material_id: id
          }
        });
      } else {
        $log.error('Validate error: ', id);
      }
    },
    async deleteMyCollection({ state, commit }, id) {
      if (validateID(id)) {
        return await this.$axios.$delete(`collections/${id}/`);
      } else {
        $log.error('Validate error: ', id);
      }
    },
    async postMyCollection({ state, commit }, data) {
      if (validateParams(data)) {
        return await this.$axios.$post(`collections/`, data);
      } else {
        $log.error('Validate error: ', data);
      }
    },
    async setMaterialInMyCollection(
      { state, commit },
      { collection_id, data }
    ) {
      if (validateID(collection_id) && validateParams(data)) {
        await this.$axios.$post(`collections/${collection_id}/materials/`, data);
      } else {
        $log.error('Validate error: ', { collection_id, data });
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
        $log.error('Validate error: ', { collection_id, data });
      }
    },
    async getMaterialInMyCollection({ state, commit }, { id, params }) {
      if (validateIDString(id) && validateParams(params)) {
        commit('SET_MATERIAL_TO_COLLECTION_LOADING', true);
        const materialsInfo = await this.$axios.$get(
          `collections/${id}/materials/`,
          {
            params: {
              ...params,
              timestamp: Date.now()
            }
          }
        );
        commit('SET_MATERIAL_TO_COLLECTION', materialsInfo);
        commit('SET_MATERIAL_TO_COLLECTION_LOADING', false);
        return materialsInfo;
      } else {
        $log.error('Validate error: ', { id, params });
      }
    }
  },
  mutations: {
    SET_COLLECTION(state, payload) {
      state.collection = payload;
    },
    SET_MATERIAL_TO_COLLECTION(state, payload) {
      const records = payload.records || payload;
      records.forEach(decodeAuthor);
      state.collection_materials = payload;
    },
    SET_MATERIAL_TO_COLLECTION_LOADING(state, payload) {
      state.collection_materials_loading = payload;
    }
  }
};
