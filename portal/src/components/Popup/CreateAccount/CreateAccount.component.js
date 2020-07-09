import Popup from '~/components/Popup'
export default {
  name: 'create-account',
  props: ['is-show', 'close', 'user'],
  components: {
    Popup
  },
  data() {
    return {
      is_submitting: false
    }
  },
  mounted() {
  },
  methods: {
    onCreateAccount() {
      const user = {}
      this.$store.commit('SET_USER', user)
      // 1. set community permission
      // 2. login
      // this.$router.push(this.$store.getters.getLoginLink(this.$route))
      // 3. close popup
      //this.isShow = false

      // this.is_submitting = true
      // this.$store
      //   .dispatch('postUser')
      //   .then(() => {
      //     setTimeout(() => {
      //       let authFlowToken = this.$store.getters.auth_flow_token
      //       if (!isNil(authFlowToken)) {
      //         let backendUrl = process.env.VUE_APP_BACKEND_URL
      //         this.$store.commit('AUTH_FLOW_TOKEN', null)
      //         window.location =
      //           backendUrl +
      //           'complete/surf-conext/?partial_token=' +
      //           authFlowToken
      //       }
      //     }, 1000)
      //   })
      //   .finally(() => {
      //     this.is_submitting = false
      //   })
    },
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
