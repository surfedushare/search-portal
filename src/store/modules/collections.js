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
    my_collection: false,
    my_collection_materials: false,
    my_collection_materials_loading: false,
    my_collections_loading: false
  },
  getters: {
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
    async getMyCollection({ state, commit }, id) {
      if (validateID(id)) {
        const collection = await this.$axios.$get(`collections/${id}/`);
        commit('SET_MY_COLLECTION', collection);
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
        commit('SET_MY_COLLECTION', collection);
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
        commit('SET_MY_COLLECTION', collection);
        return collection;
      } else {
        $log.error('Validate error: ', data);
      }
    },
    async checkMaterialInCollection({ state, commit }, id) {
      if (validateIDString(id)) {
        return await this.$axios.$get('collections/', {
          params: {
            is_owner: true,
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
        const material = await this.$axios.$post(
          `collections/${collection_id}/materials/`,
          data
        );
        commit('SET_MATERIAL_TO_MY_COLLECTION', material);
        return data;
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
        $log.error('Validate error: ', { id, params });
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
        $log.error('Validate error: ', { id, params });
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
        $log.error('Validate error: ', { id, params });
      }
    }
  },
  mutations: {
    SET_MY_COLLECTION(state, payload) {
      state.my_collection = payload;
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
    SET_MATERIAL_TO_MY_COLLECTION_LOADING(state, payload) {
      state.my_collection_materials_loading = payload;
    }
  }
};
