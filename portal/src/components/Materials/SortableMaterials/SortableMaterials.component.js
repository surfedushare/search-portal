import draggable from 'vuedraggable'
import { mapGetters } from 'vuex'
import StarRating from '../../StarRating'
import Material from '../Material/Material'

export default {
  name: 'SortableMaterials',
  components: {
    draggable,
    StarRating,
    Material,
  },
  props: {
    materials: {
      type: Object,
      default: null,
    },
    'items-in-line': {
      type: Number,
      default: 4,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    'content-editable': {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    handleMaterialClick(material) {
      this.$router.push(
        this.localePath({
          name: 'materials-id',
          params: { id: material.external_id },
        })
      )
    },
    deleteFromCollection(material) {
      const { id } = this.$route.params
      this.$store
        .dispatch('removeMaterialFromCollection', {
          collection_id: id,
          data: [{ external_id: material.external_id }],
        })
        .then(() => {
          Promise.all([
            this.$store.dispatch('getCollectionMaterials', id),
            this.$store.dispatch('getCollection', id),
          ]).then(() => null)
        })
    },
    shortenDescriptions(records) {
      if (!records) {
        return []
      }
      return records.map((record) => {
        if (record.description && record.description.length > 200) {
          record.description = record.description.slice(0, 200) + '...'
        }
        return record
      })
    },
    sortByPosition(records) {
      return records.sort((a, b) => (a.position > b.position ? 1 : -1))
    },
  },
  computed: {
    ...mapGetters(['materials_loading']),
    current_loading() {
      return this.materials_loading || this.loading
    },
    myList: {
      get() {
        if (this.materials) {
          return this.sortByPosition(
            this.shortenDescriptions(this.materials.records)
          )
        } else {
          return []
        }
      },
      set(values) {
        const { id } = this.$route.params
        const orderedList = values.map((value, index) => {
          value.position = index
          return value
        })
        const external_ids = values.map((material) => ({
          external_id: material.external_id,
        }))
        const materials = orderedList.map((material) => {
          return {
            external_id: material.external_id,
            position: material.position,
          }
        })
        this.$store
          .dispatch('removeMaterialFromCollection', {
            collection_id: id,
            data: external_ids,
          })
          .then(() => {
            this.$store.dispatch('addMaterialToCollection', {
              collection_id: id,
              data: materials,
            })
          })
      },
    },
  },
}
