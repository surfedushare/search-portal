import Popup from '~/components/Popup';
export default {
  name: 'share-collection',
  props: ['is-show', 'close', 'collection', 'value'],
  components: {
    Popup
  },
  mounted() {
    this.link = window.location.href;
  },
  data() {
    return {
      saved: false,
      link: false,
      submitting: false,
      formData: {
        title: null
      }
    };
  },
  methods: {
    onCopy() {
      this.saved = true;
      this.$emit('input', true);
    }
  },
  computed: {}
};
