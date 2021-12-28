import { validateID } from './_helpers.js'
import axios from '~/axios'

export default {
  state: {
    themes: null,
    theme: null
  },
  getters: {
    themes(state) {
      return state.themes
    },
    theme(state) {
      return state.theme
    },
    sortedThemes(state) {
      const { themes } = state

      if (themes) {
        return themes.results.slice(0).sort((a, b) => {
          if (a.title < b.title) {
            return -1
          }
          if (a.title > b.title) {
            return 1
          }
          return 0
        })
      }

      return false
    }
  },
  actions: {
    async getThemes({ commit }) {
      const { data: themes } = await axios.get('themes/', {
        params: { page_size: 100 },
      })
      commit('SET_THEMES', themes)
    },
    async getTheme({ commit }, id) {
      if (validateID(id)) {
        const { data: theme } = await axios.get(`themes/${id}/`)
        commit('SET_THEME', theme)
        return theme
      }
    }
  },
  mutations: {
    SET_THEMES(state, payload) {
      state.themes = payload
    },
    SET_THEME(state, payload) {
      state.theme = payload
    }
  },
}
