import _ from 'lodash';


export default {
  state: {
    user: null,
    user_loading: null,
    is_authenticated: false
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
    async login({ commit }, { token }) {
      localStorage.setItem('surf_token', token);
      this.$axios.setHeader('Authorization', `Token ${token}`);
      commit('AUTHENTICATE', true);
      await this.dispatch('getUser');
      commit('USER_LOADING', true);
      commit('USER_LOADING', false);
    },
    async logout({ commit }) {
      localStorage.removeItem('surf_token');
      this.$axios.setHeader('Authorization', false);
      commit('SET_USER', null);
      commit('AUTHENTICATE', false);
      window.location = process.env.VUE_APP_BACKEND_URL + 'logout'
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
    }
  }
};
