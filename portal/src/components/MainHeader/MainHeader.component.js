import { mapGetters } from 'vuex'
import Menu from './Menu'
import CreateAccount from '~/components/Popup/CreateAccount'

export default {
  name: 'main-header',
  props: [],
  components: {
    Menu,
    CreateAccount
  },
  data() {
    return {
      isShow: false
    }
  },
  methods: {
    getLoginLink() {
      return this.$store.getters.getLoginLink(this.$route)
    },
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
      let notification = this.user_permission_notifications.find(notification => {
          return notification.type === notificationType
        }
      )
      notification.is_allowed = true
      this.$store.dispatch('postUser')
    },
    switchLanguage(language) {
      this.$i18n.locale = language
    },
    showPopupCreateAccount() {
      this.isShow = true
    },
    closePopupCreateAccount() {
      this.isShow = false
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
