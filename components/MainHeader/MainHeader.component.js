import { mapGetters } from 'vuex';
import Menu from './Menu';
import { validateHREF } from '~/components/_helpers';

export default {
  name: 'main-header',
  props: [],
  components: {
    Menu
  },
  mounted() {},
  data() {
    return {};
  },
  methods: {
    /**
     * generate login URL
     * @returns {string}
     */
    getLoginLink() {
      if(process.env.VUE_APP_SURFCONEXT_BYPASS) {
        return;
      }
      return `${
        this.$axios.defaults.baseURL
      }/login/?redirect_url=${validateHREF(window.location.href)}`;
    },
    login () {
      if(process.env.VUE_APP_SURFCONEXT_BYPASS) {
        this.$store.dispatch('login', {token: process.env.VUE_APP_SURFCONEXT_BYPASS});
      }
    },
    /**
     * logout event
     */
    logout() {
      this.$store.dispatch('logout').then(() => {
        // location.reload();
        window.location = process.env.logoutURL;
      });
    },

    /**
     * Toggling visibility the mobile menu
     */
    toggleMobileMenu() {
      this.$store.commit('SET_HEADER_MENU_STATE', !this.show_header_menu);
    },

    /**
     * hide mobile menu
     */
    hideMobileMenu() {
      this.$store.commit('SET_HEADER_MENU_STATE', false);
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'user', 'show_header_menu'])
  }
};
