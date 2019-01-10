export default {
  state: {
    communities: null,
    community_info: {},
    community_themes: null,
    community_disciplines: null,
    community_collections: null,
    community_collections_loading: null
  },
  getters: {
    communities(state) {
      return state.communities;
    },
    community_info(state) {
      return state.community_info;
    },
    community_themes(state) {
      return state.community_themes;
    },
    community_disciplines(state) {
      return state.community_disciplines;
    },
    community_collections(state) {
      return state.community_collections;
    },
    community_collections_loading(state) {
      return state.community_collections_loading;
    }
  },
  actions: {
    async getCommunities({ commit }, { params = {} } = {}) {
      const communities = await this.$axios.$get('communities/', { params });
      commit('SET_COMMUNITIES', communities);
      return communities;
    },
    async putCommunities({ commit }, { id, data = {} } = {}) {
      console.log(data, id);
      const communities = await this.$axios.$put(`communities/${id}/`, data);
      commit('SET_COMMUNITIES', communities);
      return communities;
    },
    async getCommunity({ commit }, id) {
      const community_info = await this.$axios.$get(`communities/${id}/`);
      commit('SET_COMMUNITY', community_info);
    },
    async getCommunityThemes({ commit }, id) {
      const community_themes = await this.$axios.$get(
        `communities/${id}/themes/`
      );
      commit('SET_COMMUNITY_THEMES', community_themes);
    },
    async getCommunityDisciplines({ commit }, id) {
      const community_disciplines = await this.$axios.$get(
        `communities/${id}/disciplines/`
      );
      commit('SET_COMMUNITY_DISCIPLINES', community_disciplines);
    },
    async getCommunityCollections({ commit }, id) {
      commit('SET_COMMUNITY_COLLECTIONS_LOADING', true);
      const community_collections = await this.$axios.$get(
        `communities/${id}/collections/`
      );
      commit('SET_COMMUNITY_COLLECTIONS', community_collections);
      commit('SET_COMMUNITY_COLLECTIONS_LOADING', false);
    },
    async getCommunityCollectionsNextPage({ commit, state }) {
      commit('SET_COMMUNITY_COLLECTIONS_LOADING', true);
      const community_collections = await this.$axios.$get(
        state.community_collections.next
      );

      commit('SET_COMMUNITY_COLLECTIONS_NEXT', community_collections);
      commit('SET_COMMUNITY_COLLECTIONS_LOADING', false);
    },
    async postCommunityCollection({ state, commit }, data) {
      const collection = await this.$axios.$post(`collections/`, data);
      commit('ADD_COMMUNITY_COLLECTION', collection);
      return collection;
    },
    async setCommunityCollection({ commit }, { id, data }) {
      const community_collections = await this.$axios.$post(
        `communities/${id}/collections/`,
        data
      );

      commit('EXTEND_COMMUNITY_COLLECTION', community_collections);
      return community_collections;
    }
  },
  mutations: {
    SET_COMMUNITIES(state, payload) {
      state.communities = payload;
    },
    SET_COMMUNITY(state, payload) {
      state.community_info = payload;
    },
    SET_COMMUNITY_DISCIPLINES(state, payload) {
      state.community_disciplines = payload;
    },
    SET_COMMUNITY_THEMES(state, payload) {
      state.community_themes = payload;
    },
    SET_COMMUNITY_COLLECTIONS(state, payload) {
      state.community_collections = payload;
    },
    SET_COMMUNITY_COLLECTIONS_NEXT(state, payload) {
      state.community_collections = {
        ...state.community_collections,
        next: payload.next,
        results: [...state.community_collections.results, ...payload.results]
      };
    },
    ADD_COMMUNITY_COLLECTION(state, payload) {
      const results = state.community_collections.results || [];
      state.community_collections = {
        ...state.community_collections,
        results: [payload, ...results]
      };
    },
    EXTEND_COMMUNITY_COLLECTION(state, payload) {
      const results = state.community_collections.results || [];
      const payloadItem = payload[0];

      state.community_collections = {
        ...state.community_collections,
        results: results.map(item => {
          if (item.id === payloadItem.id) {
            return payloadItem;
          }
          return item;
        })
      };
    },
    SET_COMMUNITY_COLLECTIONS_LOADING(state, payload) {
      state.community_collections_loading = payload;
    }
  }
};
