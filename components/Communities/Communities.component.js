import BreadCrumbs from '~/components/BreadCrumbs';
import Search from '~/components/FilterCategories/Search';
import { mapGetters } from 'vuex';
import _ from 'lodash';

export default {
  name: 'communities',
  props: [],
  components: {
    Search,
    BreadCrumbs
  },
  mounted() {
    this.$store.dispatch('getCommunities');
  },
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
    },
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
    ...mapGetters(['communities'])
  }
};
