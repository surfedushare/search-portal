import {
  formatDate,
  validateSearch,
  validateParams,
  validateIDString,
  decodeAuthor
} from './_helpers'
import injector from 'vue-inject'
import axios from '~/axios'

const $log = injector.get('$log')

function generateSearchParams(search) {
  const { filters = {} } = search
  const filterArray = Object.keys(filters).map(key => {
    return { external_id: key, items: filters[key] }
  })

  return {
    ...search,
    filters: filterArray
  }
}

export default {
  state: {
    materials: null,
    did_you_mean: {},
    material: null,
    material_loading: null,
    material_communities: null,
    materials_keywords: null,
    materials_loading: false,
    materials_in_line: 1
  },
  getters: {
    materials(state) {
      return state.materials
    },
    did_you_mean(state) {
      return state.did_you_mean
    },
    material(state) {
      return state.material
    },
    material_loading(state) {
      return state.material_loading
    },
    material_communities(state) {
      return state.material_communities
    },
    materials_keywords(state) {
      return state.materials_keywords
    },
    materials_loading(state) {
      return state.materials_loading
    },
    materials_in_line(state) {
      return state.materials_in_line
    }
  },
  actions: {
    async getMaterial({ commit }, { id, params }) {
      if (validateIDString(id)) {
        commit('SET_MATERIAL_LOADING', true)
        const { data: material } = await axios.get(`materials/${id}/`, {
          params
        })
        decodeAuthor(material)
        commit('SET_MATERIAL', material)
        commit('SET_MATERIAL_LOADING', false)
      } else {
        return await axios.get('materials/', { params }).then(res => res.data)
      }
    },
    async setMaterialSocial({ commit }, { id, params }) {
      if (validateParams(params)) {
        // commit('SET_MATERIAL', null);
        commit('SET_MATERIAL_LOADING', true)
        const { data: material } = await axios.get(`materials/${id}/`, {
          params
        })
        commit('SET_MATERIAL', material)
        commit('SET_MATERIAL_LOADING', false)
        return material
      } else {
        $log.error('Validate error: ', { id, params })
      }
    },
    async getMaterialShare({ commit }, params) {
      if (validateParams(params)) {
        // commit('SET_MATERIAL', null);
        const { data: material } = await axios.get(`materials/`, { params })
        commit('SET_MATERIAL', material)
      } else {
        $log.error('Validate error: ', params)
      }
    },
    async getMaterials({ commit }) {
      const { data: materials } = await axios.get('materials/')
      commit('SET_MATERIALS', materials)
    },
    async getMaterialCommunities({ commit }, { params }) {
      if (validateParams(params)) {
        const { data: communities } = await axios.get('communities/', {
          params
        })
        commit('SET_MATERIAL_COMMUNITIES', communities)
      } else {
        $log.error('Validate error: ', { params })
      }
    },
    async setMaterialRating(context, params) {
      return await axios.post('rate_material/', {
        params
      })
    },
    async setApplaudMaterial(context, { external_id }) {
      if (validateIDString(external_id)) {
        return await axios.post('applaud_material/', {
          params: {
            external_id: external_id
          }
        })
      } else {
        $log.error('Validate error: ', external_id)
      }
    },
    async searchMaterials({ commit, state }, search) {
      if (validateSearch(search)) {
        commit('SET_MATERIALS_LOADING', true)
        const { data: materials } = await axios.post(
          'materials/search/',
          generateSearchParams(search)
        )
        materials.search_text = search.search_text
        materials.active_filters = search.filters
        materials.ordering = search.ordering
        state.did_you_mean = materials.did_you_mean
        commit('SET_MATERIALS', materials)
        commit('SET_MATERIALS_LOADING', false)
        return materials
      } else {
        $log.error('Validate error: ', search)
      }
    },
    async searchNextPageMaterials({ commit }, search) {
      if (validateSearch(search)) {
        commit('SET_MATERIALS_LOADING', true)
        const { data: materials } = await axios.post(
          'materials/search/',
          generateSearchParams(search)
        )
        commit('SET_NEXT_PAGE_MATERIALS', materials)
        commit('SET_MATERIALS_LOADING', false)
      } else {
        $log.error('Validate error: ', search)
      }
    },
    async searchMaterialsKeywords({ commit }, { params }) {
      const { data: keywords } = await axios.get('keywords/', { params })
      commit('SET_MATERIALS_KEYWORDS', keywords)

      return keywords
    },
    async searchMaterialsInLine({ commit }, count) {
      commit('SET_MATERIALS_IN_LINE', count)

      return count
    },
    async getSetMaterials(context, { external_id }) {
      if (validateIDString(external_id)) {
        return await axios
          .get('materials/set/', {
            params: {
              external_id: external_id
            }
          })
          .then(res => res.data)
      } else {
        $log.error('Validate error: ', external_id)
      }
    }
  },
  mutations: {
    SET_MATERIALS(state, payload) {
      const records = payload.records || payload
      records.forEach(record => {
        record.date = formatDate(record.publish_datetime)
        decodeAuthor(record)
      })
      state.materials = Object.assign({}, payload, {
        records: records.map(record => {
          return Object.assign(
            { date: formatDate(record.publish_datetime) },
            record
          )
        })
      })
    },
    SET_NEXT_PAGE_MATERIALS(state, payload) {
      const records = state.materials.records || []
      state.materials = Object.assign({}, state.materials, payload, {
        records: [
          ...records,
          ...payload.records.map(record => {
            return Object.assign(
              { date: formatDate(record.publish_datetime) },
              record
            )
          })
        ]
      })
    },
    SET_MATERIAL(state, payload) {
      state.material = Object.assign(
        { date: formatDate(payload.publish_datetime) },
        payload
      )
    },
    SET_MATERIAL_COMMUNITIES(state, payload) {
      state.material_communities = payload
    },
    SET_MATERIALS_KEYWORDS(state, payload) {
      state.materials_keywords = payload
    },
    SET_MATERIALS_LOADING(state, payload) {
      state.materials_loading = payload
    },
    SET_MATERIAL_LOADING(state, payload) {
      state.material_loading = payload
    },
    SET_MATERIALS_IN_LINE(state, payload) {
      state.materials_in_line = payload
    }
  }
}
