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
    toggleSubMenu() {
      console.log('menu', this.isShowSubMenu);
      this.isShowSubMenu = !this.isShowSubMenu;
      this.$store.dispatch('setSubMenuShow', this.isShowSubMenu);
    },
    closeSubMenu(hide = false) {
      this.isShowSubMenu = false;
      if (hide === true) {
        this.hideMenu();
      }
    },
    hideMenu() {
      this.$store.commit('SET_HEADER_MENU_STATE', false);
    }
  },
  watch: {
    show_sub_menu(show_sub_menu) {
      this.isShowSubMenu = show_sub_menu;
    }
  },
  computed: {
    ...mapGetters(['themes', 'show_header_menu', 'show_sub_menu'])
  }
};
