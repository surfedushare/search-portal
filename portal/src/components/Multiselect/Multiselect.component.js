import ClickOutside from 'vue-click-outside'

export default {
  name: 'MultiSelect',
  props: ['value', 'placeholder', 'items', 'disabled', 'select', 'deselect'],
  data() {
    return {
      opened: false
    }
  },
  directives: {
    ClickOutside
  },
  computed: {
    orderedItems() {
      return [...this.items].sort((a, b) => a.title.localeCompare(b.title))
    }
  },
  methods: {
    isSelected(item) {
      return this.value.some(id => id === item.id)
    },
    toggle() {
      this.opened = !this.opened
    },
    hide() {
      this.opened = false
    },

    onChange($event, item) {
      if ($event.target.checked) {
        this.$emit('select', item.id)
      } else {
        this.$emit('deselect', item.id)
      }
    }
  }
}
