import { without } from 'lodash'
import Spinner from './../Spinner'

export default {
  name: 'collections',
  props: {
    collections: {
      default: false
    },
    'items-in-line': {
      type: Number,
      default: 4
    },
    loading: {
      type: Boolean,
      default: false
    },
    editableContent: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      selection: []
    }
  },
  components: { Spinner },
  methods: {
    selectCollection(collection) {
      collection.selected = !collection.selected
      if (this.selection.indexOf(collection.id) === -1) {
        this.selection.push(collection)
      } else {
        this.selection = without(this.selection, { id: collection.id })
      }
      this.$emit('input', this.selection)
      this.$forceUpdate()
    }
  }
}
