import Popup from '~/components/Popup'
import StarRating from '~/components/StarRating'
export default {
  name: 'save-rating',
  props: ['value', 'is-show', 'close', 'material'],
  components: {
    Popup,
    StarRating
  },
  mounted() {},
  data() {
    return {
      saved: false,
      submitting: false,
      rating: 0
    }
  },
  methods: {
    onSaveRating() {
      this.submitting = true

      const ratings = JSON.parse(sessionStorage.getItem('ratedMaterials')) || []
      ratings.push(this.material.external_id)
      sessionStorage.setItem('ratedMaterials', JSON.stringify(ratings))

      this.$store
        .dispatch('setMaterialRating', {
          external_id: this.material.external_id,
          star_rating: this.rating
        })
        .then(() => {
          this.$store
            .dispatch('getMaterial', { id: this.$route.params.id })
            .then(() => {
              this.submitting = false
              this.saved = true
              this.rating = 0
            })
        })
    }
  },
  computed: {}
}
