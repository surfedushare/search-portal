import _ from 'lodash';
import injector from 'vue-inject';
import { validateID, validateParams } from './_helpers';


const $log = injector.get('$log');


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
    getPublicCommunities(state) {
      return (user) => {
        if(!state.communities) {
          return [];
        }
        return _.filter(state.communities.results, (community) => {
          return community.publish_status === 'PUBLISHED' ||
            user && user.communities.indexOf(community.id) >= 0 && community.publish_status !== 'DRAFT'
        })
      }
    },
    getUserCommunities(state) {
      return (user) => {
        if(!state.communities || _.isNil(user)) {
          return [];
        }
        return _.filter(state.communities.results, (community) => {
          return user.communities.indexOf(community.id) >= 0;
        })
      }
    },
    getCommunityInfo(state) {
      return (user) => {
        if (_.isEmpty(state.community_info)) {
          return state.community_info;
        } else if (state.community_info.publish_status === 'PUBLISHED') {
          return state.community_info;
        } else if(user && user.communities.indexOf(state.community_info.id)) {
          return state.community_info;
        }
      }
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
      if (validateParams(params)) {
        const communities = await this.$axios.$get('communities/', { params });
        commit('SET_COMMUNITIES', communities);
        return communities;
      } else {
        $log.error('Validate error: ', { params });
      }
    },
    async putCommunities({ commit }, { id, data = {} } = {}) {
      if (validateID(id) && validateParams(data)) {
        const communities = await this.$axios.$put(`communities/${id}/`, data);
        commit('SET_COMMUNITIES', communities);
        return communities;
      } else {
        $log.error('Validate error: ', { id, data });
      }
    },
    async getCommunity({ commit }, id) {
      if (validateID(id)) {
        const community_info = await this.$axios.$get(`communities/${id}/`);
        commit('SET_COMMUNITY', community_info);
      } else {
        $log.error('Validate error: ', id);
      }
    },
    async getCommunityThemes({ commit }, id) {
      if (validateID(id)) {
        const community_themes = await this.$axios.$get(
          `communities/${id}/themes/`
        );
        commit('SET_COMMUNITY_THEMES', community_themes);
      } else {
        $log.error('Validate error: ', id);
      }
    },
    async getCommunityDisciplines({ commit }, id) {
      if (validateID(id)) {
        const community_disciplines = await this.$axios.$get(
          `communities/${id}/disciplines/`
        );
        commit('SET_COMMUNITY_DISCIPLINES', community_disciplines);
      } else {
        $log.error('Validate error: ', id);
      }
    },
    async getCommunityCollections({ commit }, id) {
      if (validateID(id)) {
        commit('SET_COMMUNITY_COLLECTIONS_LOADING', true);
        const community_collections = await this.$axios.$get(
          `communities/${id}/collections/`
        );
        commit('SET_COMMUNITY_COLLECTIONS', community_collections);
        commit('SET_COMMUNITY_COLLECTIONS_LOADING', false);
      } else {
        $log.error('Validate error: ', id);
      }
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
      if (validateParams(data)) {
        const collection = await this.$axios.$post(`collections/`, data);
        commit('ADD_COMMUNITY_COLLECTION', collection);
        return collection;
      } else {
        $log.error('Validate error: ', data);
      }
    },
    async setCommunityCollection({ commit }, { id, data }) {
      if (validateID(id) && validateParams(data)) {
        const community_collections = await this.$axios.$post(
          `communities/${id}/collections/`,
          data
        );

        commit('EXTEND_COMMUNITY_COLLECTION', community_collections);
        return community_collections;
      } else {
        $log.error('Validate error: ', { id, data });
      }
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
