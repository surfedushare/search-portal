import { mapGetters } from 'vuex'
import Menu from './Menu'
import LanguageSwitch from './LanguageSwitch'
import Feedback from '../Feedback/Feedback'

export default {
  name: 'main-header',
  props: [],
  components: {
    LanguageSwitch,
    Menu,
    Feedback
  },
  methods: {
    logout() {
      this.$store.dispatch('logout', { fully: true })
    },
    toggleMobileMenu() {
      this.$store.commit('SET_HEADER_MENU_STATE', !this.show_header_menu)
    },
    hideMobileMenu() {
      this.$store.commit('SET_HEADER_MENU_STATE', false)
    },
    acknowledgeNotification(notificationType) {
      let notification = this.user_permission_notifications.find(
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
    ]),
    supportLink() {
      return this.$i18n.locale === 'nl'
        ? 'https://wiki.surfnet.nl/display/EDS/edusources'
        : 'https://wiki.surfnet.nl/pages/viewpage.action?pageId=55345575'
    }
  }
}
