import Popup from '~/components/Popup';
export default {
  name: 'add-filter',
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
    onSaveFilter() {
      this.submitting = true;
      this.$store.dispatch('postMyFilter', this.formData).then(() => {
        this.saved = true;
        this.submitting = false;
      });
    }
  },
  computed: {}
};
