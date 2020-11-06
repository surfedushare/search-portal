import draggable from 'vuedraggable'
import { mapGetters } from 'vuex'
import StarRating from '../../StarRating'

export default {
  name: 'sortable-materials',
  components: {
    draggable,
    StarRating
  },
  props: {
    materials: {
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
    'content-editable': {
      type: Boolean,
      default: false
    }
  },
  methods: {
    handleMaterialClick(material) {
      this.$router.push(
        this.localePath({
          name: 'materials-id',
          params: { id: material.external_id }
        })
      )
    },
    deleteFromCollection(material) {
      const { id } = this.$route.params
      this.$store
        .dispatch('removeMaterialFromMyCollection', {
          collection_id: id,
          data: [{ external_id: material.external_id }]
        })
        .then(() => {
          Promise.all([
            this.$store.dispatch('getMaterialInMyCollection', {
              id,
              params: { page: 1, page_size: 10 }
            }),
            this.$store.dispatch('getCollection', id)
          ]).then(() => null)
        })
    },
    shortenDescriptions(records) {
      if (!records) {
        return []
      }
      return records.map(record => {
        if (record.description && record.description.length > 200) {
          record.description = record.description.slice(0, 200) + '...'
        }
        return record
      })
    }
  },
  computed: {
    ...mapGetters(['materials_loading', 'getMyList']),
    current_loading() {
      return this.materials_loading || this.loading
    },
    myList: {
      get() {
        return this.getMyList.length === 0
          ? this.shortenDescriptions(this.materials.records)
          : this.getMyList
      },
      set(value) {
        const { id } = this.$route.params
        this.$store.commit('UPDATE_MY_LIST', value, id)
        const materials = this.getMyList.map(material => ({ external_id: material.external_id }))
        this.$store.dispatch('removeMaterialFromMyCollection', {
            collection_id: id,
            data: materials
          }).then(() => {
            this.$store.dispatch('setMaterialInMyCollection', {
              collection_id: id,
              data: materials
            })
        })

      }
    },
  }
}
