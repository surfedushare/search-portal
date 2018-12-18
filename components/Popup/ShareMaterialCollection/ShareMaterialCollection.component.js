import Popup from '~/components/Popup';
export default {
  name: 'share-material',
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
      },
      is_shared: this.collection.is_shared
    };
  },
  methods: {
    /**
     * The copy text on clipboard
     */
    onCopy() {
      this.saved = true;
      this.$emit('input', true);
    },
    /**
     * The change shared event
     */
    changeShared() {
      this.$store.dispatch(
        'putMyCollection',
        Object.assign({}, this.collection, { is_shared: this.is_shared })
      );
    }
  },
  computed: {}
};
