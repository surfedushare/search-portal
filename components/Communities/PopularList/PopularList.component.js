export default {
  name: 'popular-list',
  props: ['type', 'communities'],
  mounted() {},
  data() {
    return {};
  },
  methods: {
    setCommunity(community) {
      this.$store.commit('SET_COMMUNITY', community);
    }
  },
  computed: {
    computed_communities() {
      const { communities } = this;
      if (communities) {
        if (communities.results) {
          return communities.results;
        }

        return communities;
      }

      return false;
    }
  }
};
