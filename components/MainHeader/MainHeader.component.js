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
      let currentUrl = this.$route.path;
      if(process.env.VUE_APP_SURFCONEXT_BYPASS) {
        return '/' + 'login/success?continue=' + currentUrl;
      }
      let backendUrl = process.env.VUE_APP_BACKEND_URL;
      let frontendUrl = process.env.VUE_APP_FRONTEND_URL;
      let nextUrl = frontendUrl + 'login/success?continue=' + currentUrl;
      return backendUrl + 'login/surf-conext/?next=' + nextUrl;
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
      this.$store.dispatch('logout');
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
