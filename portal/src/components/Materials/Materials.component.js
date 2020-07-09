import { mapGetters } from 'vuex'
import StarRating from './../StarRating'
import _ from 'lodash'

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
    getTitleTranslation(community, language) {
      if (
        !_.isNil(community.title_translations) &&
        !_.isEmpty(community.title_translations)
      ) {
        return community.title_translations[language]
      }
      return community.name
    },
    /**
     * Set material on click
     * @param material - {Object}
     */
    setMaterial(material) {
      this.$store.commit('SET_MATERIAL', material)
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
