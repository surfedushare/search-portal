export default {
  state: {
    user: null,
    user_loading: null
  },
  getters: {
    user(state) {
      return state.user;
    },
    user_loading(state) {
      return state.user_loading;
    },
    isAuthenticated(state) {
      return !!state.user;
    },
    my_collections(state) {
      return state.user.collections || [];
    }
  },
  actions: {
    async getUser({ commit }) {
      commit('USER_LOADING', true);
      const user = await this.$axios.$get('users/me/');
      commit('SET_USER', user);
      commit('USER_LOADING', false);
    },
    async login({ commit }, { token }) {
      commit('USER_LOADING', true);
      localStorage.setItem('surf_token', token);
      this.$axios.setHeader('Authorization', `Token ${token}`);
      await this.dispatch('getUser');
      commit('USER_LOADING', false);
    },
    async logout({ commit }) {
      localStorage.removeItem('surf_token');
      this.$axios.setHeader('Authorization', false);
      commit('SET_USER', null);
      window.location = process.env.VUE_APP_BACKEND_URL + 'logout'
    }
  },
  mutations: {
    SET_USER(state, payload) {
      state.user = payload;
    },
    USER_LOADING(state, payload) {
      state.user_loading = payload;
    }
  }
};
