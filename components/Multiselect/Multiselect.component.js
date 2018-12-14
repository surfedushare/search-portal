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
        items = [...this.value, item];
      } else {
        items = this.value.filter(el => el !== item.id);
      }

      this.$emit('input', items);
    }
  },
  computed: {}
};
