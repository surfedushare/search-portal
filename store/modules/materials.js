import { formatDate } from './_helpers';

export default {
  state: {
    materials: null,
    material: null,
    material_loading: null,
    material_communities: null,
    materials_keywords: null,
    materials_loading: false,
    materials_in_line: 1
  },
  getters: {
    materials(state) {
      return state.materials;
    },
    material(state) {
      return state.material;
    },
    material_loading(state) {
      return state.material_loading;
    },
    material_communities(state) {
      return state.material_communities;
    },
    materials_keywords(state) {
      return state.materials_keywords;
    },
    materials_loading(state) {
      return state.materials_loading;
    },
    materials_in_line(state) {
      return state.materials_in_line;
    }
  },
  actions: {
    async getMaterial({ commit }, id) {
      // commit('SET_MATERIAL', null);
      commit('SET_MATERIAL_LOADING', true);
      const material = await this.$axios.$get(`materials/${id}/`);
      commit('SET_MATERIAL', material);
      commit('SET_MATERIAL_LOADING', false);
    },
    async setMaterialSocial({ commit }, { id, params }) {
      // commit('SET_MATERIAL', null);
      commit('SET_MATERIAL_LOADING', true);
      const material = await this.$axios.$get(`materials/${id}/`, { params });
      commit('SET_MATERIAL', material);
      commit('SET_MATERIAL_LOADING', false);
      return material;
    },
    async getMaterialShare({ commit }, params) {
      // commit('SET_MATERIAL', null);
      const material = await this.$axios.$get(`materials/`, { params });
      commit('SET_MATERIAL', material);
    },
    async getMaterials({ commit }) {
      const materials = await this.$axios.$get('materials/');
      commit('SET_MATERIALS', materials);
    },
    async getMaterialCommunities({ commit }, { params }) {
      const communities = await this.$axios.$get('communities/', { params });
      commit('SET_MATERIAL_COMMUNITIES', communities);
    },
    async setMaterialRating({ commit }, rating) {
      return await this.$axios.$post('materials/rating/', rating);
    },
    async getMaterialRating({ commit }, id) {
      return await this.$axios.$get('materials/rating/', {
        params: {
          object_id: id
        }
      });
    },
    async setApplaudMaterial({ commit }, { external_id }) {
      return await this.$axios.$post('applaud-materials/', {
        material: {
          external_id: external_id
        }
      });
    },
    async getApplaudMaterial({ commit }, { external_id }) {
      return await this.$axios.$get('applaud-materials/', {
        params: {
          material__external_id: external_id
        }
      });
    },
    async searchMaterials({ commit }, search) {
      commit('SET_MATERIALS_LOADING', true);
      const materials = await this.$axios.$post('materials/search/', search);
      materials.search_text = search.search_text;
      materials.active_filters = search.filters;
      materials.ordering = search.ordering;

      commit('SET_MATERIALS', materials);
      commit('SET_MATERIALS_LOADING', false);
      return materials;
    },
    async searchMaterialsInCommunity({ commit }, { id, search }) {
      commit('SET_MATERIALS_LOADING', true);
      const materials = await this.$axios.$post(
        `communities/${id}/search/`,
        search
      );
      materials.search_text = search.search_text;
      materials.active_filters = search.filters;
      materials.ordering = search.ordering;

      commit('SET_MATERIALS', materials);
      commit('SET_MATERIALS_LOADING', false);
      return materials;
    },
    async searchNextPageMaterials({ commit }, search) {
      commit('SET_MATERIALS_LOADING', true);
      const materials = await this.$axios.$post('materials/search/', search);
      commit('SET_NEXT_PAGE_MATERIALS', materials);
      commit('SET_MATERIALS_LOADING', false);
    },
    async searchNextPageMaterialsCommunity({ commit }, { id, search }) {
      commit('SET_MATERIALS_LOADING', true);
      const materials = await this.$axios.$post(
        `communities/${id}/search/`,
        search
      );
      commit('SET_NEXT_PAGE_MATERIALS', materials);
      commit('SET_MATERIALS_LOADING', false);
    },
    async searchMaterialsKeywords({ commit }, { params }) {
      const keywords = await this.$axios.$get('keywords/', { params });
      commit('SET_MATERIALS_KEYWORDS', keywords);

      return keywords;
    },
    async searchMaterialsInLine({ commit }, count) {
      commit('SET_MATERIALS_IN_LINE', count);

      return count;
    }
  },
  mutations: {
    SET_MATERIALS(state, payload) {
      const records = payload.records || payload;
      state.materials = Object.assign({}, payload, {
        records: records.map(record => {
          return Object.assign(
            { date: formatDate(record.publish_datetime) },
            record
          );
        })
      });
    },
    SET_NEXT_PAGE_MATERIALS(state, payload) {
      const records = state.materials.records || [];
      state.materials = Object.assign({}, payload, {
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
    SET_MATERIAL(state, payload) {
      state.material = Object.assign(
        { date: formatDate(payload.publish_datetime) },
        payload
      );
    },
    SET_MATERIAL_COMMUNITIES(state, payload) {
      state.material_communities = payload;
    },
    SET_MATERIALS_KEYWORDS(state, payload) {
      state.materials_keywords = payload;
    },
    SET_MATERIALS_LOADING(state, payload) {
      state.materials_loading = payload;
    },
    SET_MATERIAL_LOADING(state, payload) {
      state.material_loading = payload;
    },
    SET_MATERIALS_IN_LINE(state, payload) {
      state.materials_in_line = payload;
    }
  }
};
