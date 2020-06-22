import { generateSearchMaterialsQuery } from './../../_helpers'
import { mapGetters } from 'vuex'
export default {
  name: 'navigation',
  props: ['materials', 'material'],
  components: {},
  mounted() {},
  data() {
    return {}
  },
  methods: {
    generateSearchMaterialsQuery,
    /**
     * Set material on click
     * @param material - {Object}
     */
    setMaterial(material) {
      this.$store.commit('SET_MATERIAL', material)
    }
  },
  computed: {
    ...mapGetters(['materials_loading']),
    /**
     * Generating the navigation links
     * @returns {
     *   prev: {Object},
     *   filter: {Object},
     *   next: {Object},
     * }
     */
    links() {
      const { materials, material, materials_loading } = this
      if (materials) {
        const { records } = materials
        if (records && records.length && material) {
          const materialIndex = records.findIndex(
            record => record.external_id === material.external_id
          )

          if (materialIndex !== -1) {
            const { page_size, page, records_total } = materials

            if (
              records_total > page_size * page &&
              materialIndex + 1 === page * page_size &&
              !materials_loading
            ) {
              this.$store.dispatch(
                'searchNextPageMaterials',
                Object.assign(
                  {},
                  {
                    filters: materials.active_filters,
                    page: page + 1,
                    page_size: materials.page_size,
                    search_text: materials.search_text,
                    ordering: materials.ordering
                  }
                )
              )
            }
            return {
              prev: materialIndex ? records[materialIndex - 1] : null,
              filter:
                this.generateSearchMaterialsQuery({
                  filters: materials.active_filters,
                  page: 1,
                  page_size: materials.page_size,
                  search_text: materials.search_text,
                  ordering: materials.ordering
                }) || null,
              next: records[materialIndex + 1]
            }
          }
        }
      }
      return {
        prev: null,
        filter: null,
        next: null
      }
    }
  }
}
