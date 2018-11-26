export default {
  name: 'checkbox',
  mounted() {},
  props: [
    'value',
    'required',
    'label',
    'id',
    'name',
    'emit_root',
    'error',
    'hasError',
    'data',
    'large'
  ],
  data() {
    return {
      inputVal: this.value,
      focused: false
    };
  },
  watch: {
    /**
     * Watcher for v-model
     * @param value
     */
    value(value) {
      this.inputVal = value;
    }
  },
  methods: {
    /**
     * Event: change
     */
    change() {
      const inputVal = !this.value;
      if (this.emit_root) {
        this.$root.$emit('input', { data: this.data, value: inputVal });
      } else {
        this.$emit('input', inputVal);
      }
    }
  },
  computed: {}
};
