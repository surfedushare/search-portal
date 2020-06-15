export default {
  name: 'popular-list',
  props: ['type', 'communities'],
  mounted() {},
  data() {
    return {};
  },
  methods: {
    getCommunityDetail(community, language, detail) {
      const communityDetails = community.community_details.find(
        details => details.language_code === language.toUpperCase()
      );
      return communityDetails[detail] || null
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
