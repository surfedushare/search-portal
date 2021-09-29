import { isNil } from 'lodash'
import injector from 'vue-inject'
import axios from '~/axios'

const $log = injector.get('$log')

export default {
  state: {
    user: null,
    user_loading: null,
    is_authenticated: false,
    auth_flow_token: null,
    api_token: null
  },
  getters: {
    user(state) {
      return state.user
    },
    user_loading(state) {
      return state.user_loading
    },
    isAuthenticated(state) {
      return state.is_authenticated
    },
    my_collections(state) {
      return state.user.collections || []
    },
    user_permission_notifications(state) {
      if (isNil(state.user)) {
        return []
      }
      return state.user.permissions.filter(permission => {
        return permission.is_notification_only && isNil(permission.is_allowed)
      })
    },
    auth_flow_token(state) {
      return state.auth_flow_token
    },
    api_token(state) {
      try {
        return localStorage.getItem('surf_token') || null
      } catch (error) {
        $log.info('Unable to use localStorage: ' + error)
      }
      return state.api_token
    },
    getLoginLink() {
      return route => {
        let currentUrl = route.path + window.location.search
        if (process.env.VUE_APP_SURFCONEXT_BYPASS) {
          return '/' + 'login/success?continue=' + currentUrl
        }
        let nextUrl = encodeURIComponent(
          '/login/success?continue=' + encodeURIComponent(currentUrl)
        )
        return '/login/surf-conext/?next=' + nextUrl
      }
    },
    hasGivenCommunityPermission(state) {
      if (isNil(state.user) || isNil(state.user.permissions)) {
        return false
      }
      return state.user.permissions.some(
        permission => permission.type === 'Communities' && permission.is_allowed
      )
    }
  },
  actions: {
    async getUser({ commit }) {
      commit('USER_LOADING', true)
      const { data: user } = await axios.get('users/me/')
      commit('SET_USER', user)
      commit('USER_LOADING', false)
      $log.setIsStaff(user.is_staff)
    },
    async postUser({ commit, state }) {
      commit('USER_LOADING', true)
      await axios.post('users/me/', state.user)
      commit('SET_USER', state.user)
      commit('USER_LOADING', false)
    },
    async deleteUser() {
      return await axios.post(`users/delete-account/`)
    },
    async authenticate({ commit }, { token }) {
      if (!token) {
        return
      }
      commit('API_TOKEN', token)
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
      commit('AUTHENTICATE', true)
      commit('USER_LOADING', true)
      await this.dispatch('getUser')
      commit('USER_LOADING', false)
    },
    async logout({ commit }, payload) {
      commit('API_TOKEN', null)
      delete axios.defaults.headers.common['Authorization']
      commit('SET_USER', null)
      commit('AUTHENTICATE', false)
      $log.setIsStaff(null)
      if (payload && payload.fully) {
        window.location = '/logout'
      }
    }
  },
  mutations: {
    SET_USER(state, payload) {
      state.user = payload
    },
    USER_LOADING(state, payload) {
      state.user_loading = payload
    },
    AUTHENTICATE(state, value) {
      state.is_authenticated = value
    },
    AUTH_FLOW_TOKEN(state, token) {
      state.auth_flow_token = token
    },
    API_TOKEN(state, payload) {
      state.api_token = payload || ''
      try {
        localStorage.setItem('surf_token', state.api_token)
      } catch (error) {
        $log.info('Unable to use localStorage: ' + error)
      }
    }
  }
}
