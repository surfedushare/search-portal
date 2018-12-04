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
    onNameChanged() {
      this.$emit('input', this.formData);
    }
  },
  computed: {}
};
