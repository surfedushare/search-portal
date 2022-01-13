import axios from '~/axios'

export default {
  state: {
    themes: null,
    theme: null,
  },
  getters: {
    themes(state) {
      return state.themes
    },
    theme(state) {
      return state.theme
    },
  },
  actions: {
    async getThemes({ commit }) {
      const { data: themes } = await axios.get('themes/', {
        params: { page_size: 100 },
      })
      commit('SET_THEMES', themes)
    },
    async getTheme({ commit }, id) {
      const { data: theme } = await axios.get(`themes/${id}/`)
      commit('SET_THEME', theme)
      return theme
    },
  },
  mutations: {
    SET_THEMES(state, payload) {
      state.themes = payload
    },
    SET_THEME(state, payload) {
      state.theme = payload
    },
  },
}
