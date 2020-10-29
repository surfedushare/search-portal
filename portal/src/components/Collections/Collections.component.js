import Spinner from './../Spinner'
import DeleteCollection from '~/components/Popup/DeleteCollection'

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
      default: true
    }
  },
  data() {
    return {
      selectedCollectionId: '',
      isShowDeleteCollection: false,
    }
  },
  components: { Spinner, DeleteCollection },
  methods: {
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
    },
  }
}
