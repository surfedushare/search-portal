import draggable from 'vuedraggable'
import Spinner from './../../Spinner'
import DeleteCollection from '~/components/Popup/DeleteCollection'
import CollectionCard from '../CollectionCard/CollectionCard'

export default {
  name: 'SortableCollections',
  components: { draggable, Spinner, DeleteCollection, CollectionCard },
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
      selectedCollectionId: '',
      isShowDeleteCollection: false
    }
  },
  methods: {
    sortByPosition(collections) {
      return collections.sort((a, b) => (a.position > b.position ? 1 : -1))
    },
    deleteCollectionPopup(collection) {
      this.isShowDeleteCollection = true
      this.selectedCollectionId = collection.id
    },
    deleteCollection() {
      this.$store
        .dispatch('deleteMyCollection', this.selectedCollectionId)
        .then(() => this.closeDeleteCollection())
    },
    closeDeleteCollection() {
      const { community } = this.$route.params
      this.$store.dispatch('getCommunityCollections', community)
      this.isShowDeleteCollection = false
    }
  },
  computed: {
    myCollections: {
      get() {
        if (this.collections) {
          return this.sortByPosition(this.collections)
        } else {
          return []
        }
      },
      set(values) {
        const orderedList = values.map((value, index) => {
          value.position = index
          return value
        })
        const collections = orderedList.map(collection => {
          return {
            id: collection.id,
            title_nl: collection.title_nl,
            title_en: collection.title_en,
            position: collection.position
          }
        })
        this.$store.dispatch('updateCommunityCollections', {
          id: this.$route.params.community,
          data: collections
        })
      }
    }
  }
}
