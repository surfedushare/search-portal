import Menu from './Menu';
import { mapGetters } from 'vuex';

export default {
  name: 'main-footer',
  props: [],
  components: {
    Menu
  },
  mounted() {},
  data() {
    return {
      isShowSubMenu: this.show_sub_menu
    };
  },
  methods: {
    /**
     * Toggling visibility the themes menu
     */
    toggleSubMenuThemes() {
      this.isShowSubMenu = !this.isShowSubMenu;
      this.$store.dispatch('setSubMenuShow', this.isShowSubMenu);
    }
  },
  watch: {
    /**
     * §
     * @param show_sub_menu - Boolean
     */
    show_sub_menu(show_sub_menu) {
      this.isShowSubMenu = show_sub_menu;
    }
  },
  computed: {
    ...mapGetters(['show_sub_menu'])
  }
};
