import { mapGetters } from 'vuex'

export default {
  name: 'themes',
  props: [],
  mounted() {
    this.$store.dispatch('getThemes')
  },
  data() {
    return {}
  },
  methods: {},
  computed: {
    ...mapGetters(['themes'])
  }
}
