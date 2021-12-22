import Popup from '~/components/Popup'
import { validateHREF } from '~/components/_helpers'
export default {
  name: 'share-collection',
  props: ['is-show', 'close', 'collection', 'value'],
  components: {
    Popup,
  },
  mounted() {
    this.link = validateHREF(window.location.href)
  },
  data() {
    return {
      saved: false,
      link: false,
      submitting: false,
      formData: {
        title: null,
      },
    }
  },
  methods: {
    /**
     * The copy text on clipboard
     */
    onCopy() {
      this.saved = true
      this.$emit('input', true)
    },
  },
  computed: {},
}
