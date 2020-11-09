import Popup from '~/components/Popup'
import InputWithCounter from '~/components/InputWithCounter'
import InputLanguageWrapper from '~/components/InputLanguageWrapper'
export default {
  name: 'add-collection',
  props: ['showPopup', 'close', 'submitMethod'],
  components: {
    InputLanguageWrapper,
    InputWithCounter,
    Popup
  },
  mounted() {},
  data() {
    return {
      submitting: false,
      formData: {
        title_nl: null,
        title_en: null
      }
    }
  },
  methods: {
    onSaveCollection() {
      this.submitting = true
      this.$store
        .dispatch(this.submitMethod || 'createCollection', this.formData)
        .then(collection => {
          this.$store.dispatch('getUser')
          if (this.$listeners.submitted) {
            this.$emit('submitted', collection)
          }
        })
        .finally(() => {
          this.close()
          this.submitting = false
        })
    }
  },
  computed: {}
}
