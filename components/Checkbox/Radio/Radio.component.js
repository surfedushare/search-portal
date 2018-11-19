export default {
  name: 'radio',
  model: {
    prop: 'modelValue',
    event: 'input'
  },
  props: {
    id: {
      type: String,
      default: function() {
        return 'radio-id-' + this._uid
      }
    },
    name: {
      type: String,
      default: null
    },
    value: {
      default: ''
    },
    modelValue: {
      default: undefined
    },
    className: {
      type: String,
      default: null
    },
    checked: {
      type: Boolean,
      default: false
    },
    alignCenter: {
      type: Boolean,
      default: false
    },
    required: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    model: {}
  },
  computed: {
    state() {
      if (this.modelValue === undefined) {
        return this.checked
      }
      return this.modelValue === this.value
    }
  },
  methods: {
    onChange() {
      this.toggle()
    },
    toggle() {
      this.$emit('input', this.state ? '' : this.value)
    }
  },
  watch: {
    checked(newValue) {
      if (newValue !== this.state) {
        this.toggle()
      }
    }
  },
  mounted() {
    if (this.checked && !this.state) {
      this.toggle()
    }
  }
}
