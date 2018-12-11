import Popup from '~/components/Popup';
export default {
  name: 'add-collection',
  props: ['is-show', 'close'],
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
    onSaveCollection() {
      this.submitting = true;
      this.$store.dispatch('postMyCollection', this.formData).then(() => {
        this.saved = true;
        this.submitting = false;
      });
    }
  },
  computed: {}
};
