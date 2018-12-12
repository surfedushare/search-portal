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
      this.isShowSubMenu = !this.isShowSubMenu;
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
  computed: {
    ...mapGetters(['themes', 'show_header_menu'])
  }
};
