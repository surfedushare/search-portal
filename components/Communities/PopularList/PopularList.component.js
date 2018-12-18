export default {
  name: 'popular-list',
  props: ['type', 'communities'],
  mounted() {},
  data() {
    return {};
  },
  methods: {
    /**
     * Set community on click
     * @param community - {Object}
     */
    setCommunity(community) {
      this.$store.commit('SET_COMMUNITY', community);
    }
  },
  computed: {
    /**
     * Checking inputs. If communities have search fields return communities.results
     * @returns Boolean or Array of communities
     */
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
