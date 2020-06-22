export default {
  state: {
    show_header_menu: false
  },
  getters: {
    show_header_menu(state) {
      return state.show_header_menu
    }
  },
  actions: {},
  mutations: {
    SET_HEADER_MENU_STATE(state, payload) {
      state.show_header_menu = payload
    }
  }
}
