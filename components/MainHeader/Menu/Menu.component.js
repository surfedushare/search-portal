import { mapGetters } from 'vuex';
import ClickOutside from 'vue-click-outside';

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
    },

    /**
     * Watcher on route change
     */
    $route() {
      this.closeSubMenu();
    }
  },
  computed: {
    ...mapGetters(['themes', 'show_header_menu', 'show_sub_menu']),
    sortedThemes() {
      const { themes } = this;

      if (themes) {
        return themes.results.slice(0).sort((a, b) => {
          if (a.title < b.title) {
            return -1;
          }
          if (a.title > b.title) {
            return 1;
          }
          return 0;
        });
      }

      return false;
    }
  },

  directives: {
    ClickOutside
  }
};
