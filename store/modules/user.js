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
    }
  },
  actions: {
    async getUser({ commit }) {
      const user = await this.$axios.$get('users/me/');
      commit('SET_USER', user);
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
      const user = await this.$axios.$get('logout/');

      commit('SET_USER', null);
      return user;
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
