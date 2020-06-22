import { mapGetters } from 'vuex'
import _ from 'lodash'
import StarRating from '~/components/StarRating'
import PopularList from '~/components/Communities/PopularList'
import numeral from 'numeral'
import Themes from '~/components/Themes'
import Keywords from '~/components/Keywords'
import SaveRating from '~/components/Popup/SaveRating'
import { generateSearchMaterialsQuery, validateHREF } from './../../_helpers'

export default {
  name: 'material-info',
  props: ['material'],
  components: {
    StarRating,
    Themes,
    PopularList,
    Keywords,
    SaveRating
  },
  mounted() {
    this.$store
      .dispatch('getApplaudMaterial', {
        external_id: this.material.external_id
      })
      .then(applaud => {
        this.is_applauded = !!applaud.count
        this.is_loading_applaud = false
      })

    this.href = validateHREF(window.location.href)
  },
  data() {
    return {
      href: '',
      shared_link: false,
      isShow: false,
      is_loading_applaud: true,
      is_applauded: false,
      rating: false,
      rating_given: this.isMaterialRated(this.material.external_id),
      is_copied: false,
      formData: {
        page_size: 10,
        page: 1,
        filters: [],
        search_text: []
      }
    }
  },
  methods: {
    generateSearchMaterialsQuery,
    /**
     * Show the popup "Save rating"
     */
    showPopupSaveRating() {
      this.isShow = true
    },
    /**
     * Close the popup "Save rating"
     */
    closePopupSaveRating() {
      this.isShow = false
    },
    /**
     * Check in sessionStorage if material has been rated by the current user"
     * @param external_id of material - String
     */
    isMaterialRated(materialId) {
      const ratings = sessionStorage.getItem('ratedMaterials')
      const parsedRatings = ratings !== null ? JSON.parse(ratings) : []
      return parsedRatings.includes(materialId)
    },
    /**
     * Saving the applaud for material
     * @param material - Object
     */
    setApplaudMaterial(material) {
      this.is_loading_applaud = true
      this.$store
        .dispatch('setApplaudMaterial', {
          external_id: material.external_id
        })
        .then(() => {
          this.is_applauded = true
          this.$store
            .dispatch('getMaterial', { id: this.$route.params.id })
            .then(() => {
              this.is_loading_applaud = false
            })
        })
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'themes']),
    /**
     * generate author URL
     * @returns {{path, query}}
     */
    authorUrl() {
      if (this.material) {
        this.formData.author = this.material.author
        return this.generateSearchMaterialsQuery(this.formData)
      }
    },
    /**
     * Get formatted 'number_of_views'
     * @returns String
     */
    counted() {
      return numeral(this.material.view_count).format('0a')
    },
    /**
     * get material themes
     * @returns {*}
     */
    material_themes() {
      const { material, themes } = this

      if (material && themes) {
        const material_themes = material.themes

        return {
          results: themes.results.filter(theme => {
            return material_themes.indexOf(theme.external_id) !== -1
          })
        }
      }

      return false
    }
  },
  watch: {
    /**
     * If the material changes, it is checked if the material has been rated
     */
    material: function() {
      const { material } = this
      if (!_.isNil(material)) {
        this.rating_given = this.isMaterialRated(material.external_id)
      }
    }
  }
}
