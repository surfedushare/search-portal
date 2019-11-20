import _ from 'lodash';


export default {
  state: {
    user: null,
    user_loading: null,
    is_authenticated: false,
    auth_flow_token: null
  },
  getters: {
    user(state) {
      return state.user;
    },
    user_loading(state) {
      return state.user_loading;
    },
    isAuthenticated(state) {
      return state.is_authenticated;
    },
    my_collections(state) {
      return state.user.collections || [];
    },
    user_permission_notifications(state) {
      if(_.isNil(state.user)) {
        return [];
      }
      return _.filter(state.user.permissions, (permission) => {
        return permission.is_notification_only && _.isNil(permission.is_allowed) ;
      });
    },
    auth_flow_token(state) {
      return state.auth_flow_token;
    },
    getLoginLink(state) {
      return (route) => {
        let currentUrl = route.path + window.location.search;
        if(process.env.VUE_APP_SURFCONEXT_BYPASS) {
          return '/' + 'login/success?continue=' + currentUrl;
        }
        let backendUrl = process.env.VUE_APP_BACKEND_URL;
        let frontendUrl = process.env.VUE_APP_FRONTEND_URL;
        let nextUrl = frontendUrl + 'login/success?continue=' + encodeURIComponent(currentUrl);
        return backendUrl + 'login/surf-conext/?next=' + nextUrl;
      }
    }
  },
  actions: {
    async getUser({ commit }) {
      commit('USER_LOADING', true);
      const user = await this.$axios.$get('users/me/', {withCredentials: true});
      commit('SET_USER', user);
      commit('USER_LOADING', false);
    },
    async postUser({ commit, state }) {
      commit('USER_LOADING', true);
      await this.$axios.$post('users/me/', state.user, {withCredentials: true});
      commit('SET_USER', state.user);
      commit('USER_LOADING', false);
    },
    async authenticate({ commit }, { token }) {
      localStorage.setItem('surf_token', token);
      this.$axios.setHeader('Authorization', `Token ${token}`);
      commit('AUTHENTICATE', true);
      commit('USER_LOADING', true);
      await this.dispatch('getUser');
      commit('USER_LOADING', false);
    },
    async logout({ commit }, { fully }) {
      localStorage.removeItem('surf_token');
      this.$axios.setHeader('Authorization', false);
      commit('SET_USER', null);
      commit('AUTHENTICATE', false);
      if(fully) {
        window.location = process.env.VUE_APP_BACKEND_URL + 'logout'
      }
    }
  },
  mutations: {
    SET_USER(state, payload) {
      state.user = payload;
    },
    USER_LOADING(state, payload) {
      state.user_loading = payload;
    },
    AUTHENTICATE(state, value) {
      state.is_authenticated = value;
    },
    AUTH_FLOW_TOKEN(state, token) {
      state.auth_flow_token = token;
    }
  }
};
