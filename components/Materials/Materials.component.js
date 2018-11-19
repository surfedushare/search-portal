import { mapGetters } from 'vuex'
import StarRating from './../StarRating'

export default {
  name: 'materials',
  props: [],
  components: {
    StarRating
  },
  mounted() {
    this.$store.dispatch('getMaterials')
  },
  data() {
    return {}
  },
  methods: {},
  computed: {
    ...mapGetters(['materials'])
  }
}
