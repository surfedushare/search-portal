import { mapGetters } from 'vuex';

export default {
  name: 'menu-block',
  props: [],
  mounted() {},
  data() {
    return {
      isShowSubMenu: false
    };
  },
  methods: {
    /**
     * Toggling visibility the submenu
     */
    toggleSubMenu() {
      this.isShowSubMenu = !this.isShowSubMenu;
      this.$store.dispatch('setSubMenuShow', this.isShowSubMenu);
    },
    /**
     * Close the submenu
     */
    closeSubMenu(hide = false) {
      this.isShowSubMenu = false;
      if (hide === true) {
        this.hideMenu();
      }
    },
    /**
     * Hide the submenu
     */
    hideMenu() {
      this.$store.commit('SET_HEADER_MENU_STATE', false);
    }
  },
  watch: {
    /**
     * Watcher on changing the 'show_sub_menu' field
     * @param show_sub_menu - Boolean
     */
    show_sub_menu(show_sub_menu) {
      this.isShowSubMenu = show_sub_menu;
    }
  },
  computed: {
    ...mapGetters(['themes', 'show_header_menu', 'show_sub_menu'])
  }
};
