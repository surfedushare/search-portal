export default {
  name: 'popular-list',
  props: ['type', 'communities'],
  mounted() {},
  data() {
    return {};
  },
  methods: {},
  computed: {
    computed_communities() {
      const { communities } = this;
      if (communities) {
        if (communities.results && communities.results.length) {
          return communities.results;
        }

        return communities;
      }

      return false;
    }
  }
};
