import ClickOutside from 'vue-click-outside';
export default {
  name: 'multiselect',
  props: ['value', 'placeholder', 'items', 'disabled'],
  mounted() {},
  data() {
    const ids = this.value;
    return {
      opened: false,
      elements: this.items.map(item => ids.indexOf(item.id) !== -1)
    };
  },
  directives: {
    ClickOutside
  },
  methods: {
    /**
     * Toggling the popup visibility
     */
    toggle() {
      this.opened = !this.opened;
    },
    /**
     * Hide the popup
     */
    hide() {
      this.opened = false;
    },

    /**
     * Get current items array on change item checking
     */
    onChange($event, item) {
      let items = [];
      if ($event.target.checked) {
        items = [...this.value, item.id];
      } else {
        items = this.value.filter(el => el !== item.id);
      }

      this.$emit('input', items);
    }
  }
};
