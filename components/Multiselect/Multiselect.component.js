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
    toggle() {
      this.opened = !this.opened;
    },

    hide() {
      this.opened = false;
    },

    onChange($event, item) {
      let items = [];
      if ($event.target.checked) {
        items = [...this.value, item.id];
      } else {
        items = this.value.filter(el => el !== item.id);
      }

      console.log(11111, items);

      this.$emit('input', items);
    }
  },
  computed: {
    first_checked_item() {
      const { value, items } = this;
      if (value && value[0] && items) {
        const id = value[0].id || value[0];

        return items.find(item => item.id === id);
      }

      return false;
    }
  }
};
