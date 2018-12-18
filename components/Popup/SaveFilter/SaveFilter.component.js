import Popup from '~/components/Popup';
export default {
  name: 'save-filter',
  props: ['value', 'is-show', 'close', 'on-save-filter'],
  components: {
    Popup
  },
  mounted() {},
  data() {
    return {
      formData: this.value
    };
  },
  methods: {
    /**
     * The change name event
     */
    onNameChanged() {
      this.$emit('input', this.formData);
    }
  },
  computed: {}
};
