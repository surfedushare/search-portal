import { mapGetters } from 'vuex'
export default {
  name: 'search',
  props: [],
  mounted() {
    this.$store.dispatch('getFilterCategories')
  },
  data() {
    return {
      active_category_id: null
    }
  },
  methods: {},
  computed: {
    ...mapGetters(['filter_categories']),
    active_category() {
      const { filter_categories, active_category_id } = this
      if (filter_categories) {
        if (active_category_id) {
          return filter_categories.find(item => item.id === active_category_id)
        }
        this.active_category_id = filter_categories[0].id
        return filter_categories[0]
      }
      return false
    }
  }
}
