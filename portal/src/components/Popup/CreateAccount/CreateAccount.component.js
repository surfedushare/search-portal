import Popup from '~/components/Popup'
import {mapGetters} from "vuex";
export default {
  name: 'create-account',
  props: ['value', 'is-show', 'close', 'auto_width'],
  components: {
    Popup
  },
  mounted() {
  },
  data() {
    return {
    }
  },
  methods: {
  },
  computed: {
    ...mapGetters(['user']),
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
