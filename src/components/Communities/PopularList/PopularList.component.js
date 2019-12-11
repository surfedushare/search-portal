import _ from 'lodash';


export default {
  name: 'popular-list',
  props: ['type', 'communities'],
  mounted() {},
  data() {
    return {};
  },
  methods: {
    getTitleTranslation( community, language ) {
      if (!_.isNil(community.title_translations) && !_.isEmpty(community.title_translations)){
        return community.title_translations[language];
      }
      return community.name
    },
    getDescriptionTranslation( community, language ) {
      if (!_.isNil(community.description_translations) && !_.isEmpty(community.description_translations)){
        return community.description_translations[language];
      }
      return community.description
    },
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
