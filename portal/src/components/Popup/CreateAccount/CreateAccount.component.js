import { isNil } from 'lodash'
import Popup from '~/components/Popup'

export default {
  name: 'create-account',
  props: ['showPopup', 'close', 'user'],
  components: {
    Popup
  },
  data() {
    return {
      isSubmitting: false
    }
  },
  methods: {
    onCreateAccount() {
      this.isSubmitting = true
      const accountPermission = this.user.permissions.find(
        permission => permission['type'] === 'Communities'
      )
      accountPermission.is_allowed = true
      this.$store
        .dispatch('postUser')
        .then(() => {
          const authFlowToken = this.$store.getters.auth_flow_token
          if (!isNil(authFlowToken)) {
            this.$store.commit('AUTH_FLOW_TOKEN', null)
            window.location =
              '/complete/surf-conext/?partial_token=' + authFlowToken
          }
        })
        .finally(() => {
          this.isSubmitting = false
          this.$router.push('/')
        })
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
        return null
      }
    }
  }
}
