import Popup from '~/components/Popup';
export default {
  name: 'add-collection',
  props: ['is-show', 'close', 'submit-method'],
  components: {
    Popup
  },
  mounted() {},
  data() {
    return {
      saved: false,
      submitting: false,
      formData: {
        title: null
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
          this.$store.dispatch('getUser');
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
