import _ from 'lodash';
import { mapGetters } from 'vuex';
import Menu from './Menu';


export default {
  name: 'main-header',
  props: [],
  components: {
    Menu
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
    },
    acknowledgeNotification(notificationType) {
      let notification = _.find(this.user_permission_notifications, (notification) => {
        return notification.type === notificationType;
      });
      notification.is_allowed = true;
      this.$store.dispatch('postUser');
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'user', 'show_header_menu', 'user_permission_notifications']),
  }
};
