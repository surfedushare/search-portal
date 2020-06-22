export default {
  state: {
    show_sub_menu: false
  },
  getters: {
    show_sub_menu(state) {
      return state.show_sub_menu
    }
  },
  actions: {
    setSubMenuShow({ commit }, is_show) {
      commit('SET_HEADER_SUB_MENU_STATE', is_show)
    }
  },
  mutations: {
    SET_HEADER_SUB_MENU_STATE(state, payload) {
      state.show_sub_menu = payload
    }
  }
}
