import { mapGetters } from 'vuex'
import StarRating from './../StarRating'

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
    StarRating
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
    /**
     * Select material
     * @param material - {Object}
     */
    selectMaterial(material) {
      let selected_materials = this.value.slice(0)

      if (selected_materials.indexOf(material.external_id) === -1) {
        selected_materials.push(material.external_id)
      } else {
        selected_materials = selected_materials.filter(
          item => item !== material.external_id
        )
      }
      this.$emit('input', selected_materials)
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
          const newDisciplines = material.disciplines.map(discipline => {
            const category = materials.filter_categories.find(
              filter_category =>
                filter_category.external_id ===
                'lom.classification.obk.discipline.id'
            )

            return category.children.find(
              child => child.external_id === discipline
            )
          })
          const description =
            material.description && material.description.length > 200
              ? material.description.slice(0, 200) + '...'
              : material.description

          return {
            ...material,
            selected: selected_materials.indexOf(material.external_id) !== -1,
            disciplines: newDisciplines,
            description
          }
        })
      }

      return false
    }
  }
}
