import { mapGetters } from 'vuex'
import Popup from './../../Popup'
export default {
  name: 'save-material-in-collection',
  props: ['isShow', 'close', 'material'],
  components: {
    Popup
  },
  data() {
    return {
      collection: null,
      submitting: false
    }
  },
  methods: {
    /**
     * Save material
     */
    onSaveMaterial() {
      this.submitting = true
      this.$store
        .dispatch('addMaterialToCollection', {
          collection_id: this.collection,
          data: [
            {
              external_id: this.material.external_id
            }
          ]
        })
        .then(() => {
          this.$store
            .dispatch('getMaterial', { id: this.$route.params.id })
            .then(() => {
              this.submitting = false
              this.close()
            })
        })
    }
  },
  computed: {
    ...mapGetters(['my_collections'])
  }
}
