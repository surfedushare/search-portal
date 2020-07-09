import Popup from '~/components/Popup'
export default {
  name: 'create-account',
  props: ['is-show', 'close', 'user'],
  components: {
    Popup
  },
  methods: {
    onCreateAccount() {
      // 1. set community permission
      // 2. login
      // this.$router.push(this.$store.getters.getLoginLink(this.$route))
      // 3. close popup
      this.close()
    },
    continueWithoutAccount() {
      this.$router.push('/')
    }
  },
  computed: {
    communityPermission() {
      if (this.user && this.user.permissions) {
        return this.user.permissions.find(
          permission => permission.type === 'Communities'
        )
      } else {
        return {}
      }
    }
  }
}
