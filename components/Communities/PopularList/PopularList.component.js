import { mapGetters } from 'vuex'

export default {
  name: 'popular-list',
  props: [],
  mounted() {
    this.$store.dispatch('getCommunities')
  },
  data() {
    return {}
  },
  methods: {},
  computed: {
    ...mapGetters(['communities'])
  }
}
