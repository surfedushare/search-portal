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
    darkStars: {
      type: Boolean,
      default: false
    },
    hideCounter: {
      type: Boolean,
      default: false
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
      temp_value: Math.round(this.value),
      ratings: [1, 2, 3, 4, 5],
      types: [
        this.$t('Not-judged'),
        this.$t('Bad'),
        this.$t('Tevreden'),
        this.$t('Normal'),
        this.$t('Good'),
        this.$t('Perfect')
      ]
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
