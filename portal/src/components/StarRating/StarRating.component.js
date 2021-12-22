export default {
  name: 'star-rating',
  props: {
    type: {
      type: String,
      default: function () {
        return 'default'
      },
    },
    darkStars: {
      type: Boolean,
      default: false,
    },
    hideCounter: {
      type: Boolean,
      default: false,
    },
    value: null,
    counter: [String, Number],
    disabled: Boolean,
    required: Boolean,
  },
  mounted() {},
  data() {
    return {
      avg_rating: this.value,
      ratings: [1, 2, 3, 4, 5],
      types: [
        this.$t('Not-judged'),
        this.$t('Bad'),
        this.$t('Tevreden'),
        this.$t('Normal'),
        this.$t('Good'),
        this.$t('Perfect'),
      ],
    }
  },
  methods: {
    /**
     * MouseOver on star items
     * @param index - index of element
     */
    star_over(index) {
      if (!this.disabled) {
        this.avg_rating = index
      }
    },

    /**
     * MouseOut on star items
     */
    star_out() {
      if (!this.disabled) {
        return (this.avg_rating = this.value)
      }
    },

    /**
     * Set v-model value
     * @param value
     */
    setValue(value) {
      if (!this.disabled) {
        this.$emit('input', value)
      }
    },
  },
  watch: {
    value(value) {
      this.avg_rating = value
    },
  },
}
