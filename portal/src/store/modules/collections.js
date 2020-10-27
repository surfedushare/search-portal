import injector from 'vue-inject'
import {
  validateID,
  validateIDString,
  validateParams,
  decodeAuthor
} from './_helpers'
import axios from '~/axios'

const $log = injector.get('$log')

export default {
  state: {
    collection: false,
    collection_materials: false,
    collection_materials_loading: false
  },
  getters: {
    collection(state) {
      return state.collection
    },
    collection_materials(state) {
      return state.collection_materials
    },
    collection_materials_loading(state) {
      return state.collection_materials_loading
    }
  },
  actions: {
    async getCollection({ commit }, id) {
      if (validateID(id)) {
        const { data: collection } = await axios.get(`collections/${id}/`)
        commit('SET_COLLECTION', collection)
        return collection
      } else {
        $log.error('Validate error: ', id)
      }
    },
    async setCollectionSocial({ commit }, { id, params }) {
      if (validateID(id) && validateParams(params)) {
        const { data: collection } = await axios.get(`collections/${id}/`, {
          params
        })
        commit('SET_COLLECTION', collection)
        return collection
      } else {
        $log.error('Validate error: ', { id, params })
      }
    },
    async putMyCollection({ commit }, data) {
      if (validateID(data.id) && validateParams(data)) {
        const { data: collection } = await axios.put(
          `collections/${data.id}/`,
          data
        )
        commit('SET_COLLECTION', collection)
        return collection
      } else {
        $log.error('Validate error: ', data)
      }
    },
    async checkMaterialInCollection(context, id) {
      if (validateIDString(id)) {
        return await axios
          .get('collections/', {
            params: {
              material_id: id
            }
          })
          .then(res => res.data)
      } else {
        $log.error('Validate error: ', id)
      }
    },
    async deleteMyCollection(context, id) {
      if (validateID(id)) {
        return await axios.delete(`collections/${id}/`).then(res => res.data)
      } else {
        $log.error('Validate error: ', id)
      }
    },
    async postMyCollection(context, data) {
      if (validateParams(data)) {
        return await axios.post(`collections/`, data).then(res => res.data)
      } else {
        $log.error('Validate error: ', data)
      }
    },
    async setMaterialInMyCollection(context, { collection_id, data }) {
      if (validateID(collection_id) && validateParams(data)) {
        return await axios
          .post(`collections/${collection_id}/materials/`, data)
          .then(res => res.data)
      } else {
        $log.error('Validate error: ', { collection_id, data })
      }
    },
    async removeMaterialFromMyCollection(context, { collection_id, data }) {
      if (validateID(collection_id) && validateParams(data)) {
        return axios
          .delete(`collections/${collection_id}/materials/`, {
            data
          })
          .then(res => res.data)
      } else {
        $log.error('Validate error: ', { collection_id, data })
      }
    },
    async getMaterialInMyCollection({ commit }, { id, params }) {
      if (validateIDString(id) && validateParams(params)) {
        commit('SET_MATERIAL_TO_COLLECTION_LOADING', true)
        const { data: materialsInfo } = await axios.get(
          `collections/${id}/materials/`,
          {
            params: {
              ...params,
              timestamp: Date.now()
            }
          }
        )
        commit('SET_MATERIAL_TO_COLLECTION', materialsInfo)
        commit('SET_MATERIAL_TO_COLLECTION_LOADING', false)
        return materialsInfo
      } else {
        $log.error('Validate error: ', { id, params })
      }
    },
    async getNextMaterialInMyCollection({ commit }, { id, params }) {
      if (validateIDString(id) && validateParams(params)) {
        commit('SET_MATERIAL_TO_COLLECTION_LOADING', true)
        const { data: materialsInfo } = await axios.get(
          `collections/${id}/materials/`,
          {
            params: {
              ...params,
              timestamp: Date.now()
            }
          }
        )
        commit('SET_NEXT_PAGE_MATERIAL_TO_COLLECTION', materialsInfo)
        commit('SET_MATERIAL_TO_COLLECTION_LOADING', false)
      } else {
        $log.error('Validate error: ', { id, params })
      }
    }
  },
  mutations: {
    SET_COLLECTION(state, payload) {
      state.collection = payload
    },
    SET_MATERIAL_TO_COLLECTION(state, payload) {
      const records = payload.records || payload
      records.forEach(decodeAuthor)
      state.collection_materials = payload
    },
    SET_MATERIAL_TO_COLLECTION_LOADING(state, payload) {
      state.collection_materials_loading = payload
    },
    SET_NEXT_PAGE_MATERIAL_TO_COLLECTION(state, payload) {
      const records = state.collection_materials.records || []
      payload.records.forEach(decodeAuthor)

      state.collection_materials = Object.assign(
        {},
        state.collection_materials,
        payload,
        { records: [...records, ...payload.records] }
      )
    }
  }
}
