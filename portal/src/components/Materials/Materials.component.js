import { mapGetters } from 'vuex'
import StarRating from './../StarRating'
import Material from './Material/Material'

export default {
  name: 'materials',
  props: {
    materials: {
      default: false
    },
    'items-in-line': {
      type: Number,
      default: 4
    },
    'items-length': {
      type: [Number, String],
      default: 'auto'
    },
    loading: {
      type: Boolean,
      default: false
    },
    contenteditable: {
      type: Boolean,
      default: false
    },
    selectFor: {
      type: String,
      default: 'delete'
    },
    value: {
      // type: Array,
      // default: []
    }
  },
  components: {
    StarRating,
    Material
  },
  data() {
    return {
      selected_materials: this.value || []
    }
  },
  methods: {
    handleMaterialClick(material) {
      if (this.selectFor === 'add') {
        this.$store.commit('SET_MATERIAL', material)
      } else {
        this.$router.push(
          this.localePath({
            name: 'materials-id',
            params: { id: material.external_id }
          })
        )
      }
    },
    selectMaterial(material) {
      if (this.selectFor === 'delete') {
        this.deleteMaterial(material)
      } else {
        this.$emit('input', this.toggleMaterial(material))
      }
    },
    deleteMaterial(material) {
      const { id } = this.$route.params
      this.$store
        .dispatch('removeMaterialFromCollection', {
          collection_id: id,
          data: [{ external_id: material.external_id }]
        })
        .then(() => {
          Promise.all([
            this.$store.dispatch('getCollectionMaterials', id),
            this.$store.dispatch('getCollection', id)
          ]).then(() => null)
        })
    },
    toggleMaterial(material) {
      let selected_materials = this.value.slice(0)

      if (selected_materials.indexOf(material.external_id) === -1) {
        selected_materials.push(material.external_id)
      } else {
        selected_materials = selected_materials.filter(
          item => item !== material.external_id
        )
      }
      return selected_materials
    }
  },
  watch: {
    value(value) {
      this.selected_materials = value
    }
  },
  computed: {
    ...mapGetters(['materials_loading']),
    selectMaterialClass() {
      return this.selectFor === 'delete' ? 'select-delete' : 'select-neutral'
    },
    current_loading() {
      return this.materials_loading || this.loading
    },
    extended_materials() {
      const { materials, selected_materials } = this
      if (materials) {
        const arrMaterials = materials.records ? materials.records : materials

        return arrMaterials.map(material => {
          const description =
            material.description && material.description.length > 200
              ? material.description.slice(0, 200) + '...'
              : material.description

          return {
            ...material,
            selected: selected_materials.indexOf(material.external_id) !== -1,
            description
          }
        })
      }

      return false
    }
  }
}
