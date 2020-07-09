import _ from 'lodash'
import { mapGetters } from 'vuex'
import Menu from './Menu'
import LanguageSwitch from './LanguageSwitch'

export default {
  name: 'main-header',
  props: [],
  components: {
    LanguageSwitch,
    Menu
  },
  methods: {
    /**
     * generate login URL
     * @returns {string}
     */
    getLoginLink() {
      return this.$store.getters.getLoginLink(this.$route)
    },
    /**
     * logout event
     */
    logout() {
      this.$store.dispatch('logout', { fully: true })
    },

    /**
     * Toggling visibility the mobile menu
     */
    toggleMobileMenu() {
      this.$store.commit('SET_HEADER_MENU_STATE', !this.show_header_menu)
    },

    /**
     * hide mobile menu
     */
    hideMobileMenu() {
      this.$store.commit('SET_HEADER_MENU_STATE', false)
    },
    acknowledgeNotification(notificationType) {
      let notification = _.find(
        this.user_permission_notifications,
        notification => {
          return notification.type === notificationType
        }
      )
      notification.is_allowed = true
      this.$store.dispatch('postUser')
    }
  },
  computed: {
    ...mapGetters([
      'isAuthenticated',
      'user',
      'show_header_menu',
      'user_permission_notifications',
      'hasMessages',
      'getMessageLevels',
      'getLevelIcon',
      'getMessagesContent'
    ])
  }
}
