import axios from '~/axios'

export default {
  state: {
    statistic: null
  },
  getters: {
    statistic(state) {
      return state.statistic
    }
  },
  actions: {
    async getStatistic({ commit }) {
      const { data: statistic } = await axios.get('stats/all-materials/')
      commit('GET_STATISTIC', statistic)
    }
  },
  mutations: {
    GET_STATISTIC(state, payload) {
      state.statistic = payload
    }
  }
}
