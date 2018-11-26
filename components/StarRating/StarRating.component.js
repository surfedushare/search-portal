export default {
  name: 'star-rating',
  props: {
    name: String,
    type: {
      type: String,
      default: function() {
        return 'default';
      }
    },
    value: null,
    id: String,
    counter: [String, Number],
    disabled: Boolean,
    required: Boolean
  },
  mounted() {},
  data() {
    return {
      temp_value: this.value,
      ratings: [1, 2, 3, 4, 5]
    };
  },
  methods: {
    /**
     * MouseOver on star items
     * @param index - index of element
     */
    star_over(index) {
      if (!this.disabled) {
        this.temp_value = index;
      }
    },

    /**
     * MouseOut on star items
     */
    star_out() {
      if (!this.disabled) {
        return (this.temp_value = this.value);
      }
    },

    /**
     * Set v-model value
     * @param value
     */
    setValue(value) {
      if (!this.disabled) {
        this.$emit('input', value);
      }
    }
  },
  computed: {},
  watch: {
    value(value) {
      this.temp_value = value;
    }
  }
};
