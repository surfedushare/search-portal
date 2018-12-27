import Popup from '~/components/Popup';
export default {
  name: 'add-collection',
  props: ['is-show', 'close', 'is-shared', 'submit-method'],
  components: {
    Popup
  },
  mounted() {},
  data() {
    return {
      saved: false,
      submitting: false,
      formData: {
        title: null,
        is_shared: this.isShared || false
      }
    };
  },
  methods: {
    /**
     * The save collection event
     */
    onSaveCollection() {
      this.submitting = true;
      this.$store
        .dispatch(this.submitMethod || 'postMyCollection', this.formData)
        .then(collection => {
          this.saved = true;
          this.submitting = false;
          if (this.$listeners.submitted) {
            this.$emit('submitted', collection);
          }
        });
    }
  },
  computed: {}
};
