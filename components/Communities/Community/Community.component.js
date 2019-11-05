import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import Search from '~/components/FilterCategories/Search';
import Themes from '~/components/Themes';
import Disciplines from '~/components/Disciplines';
import Collections from '~/components/Collections';
import Materials from '~/components/Materials';
import Spinner from '~/components/Spinner';
import Error from '~/components/error';
import _ from 'lodash';

export default {
  name: 'community',
  props: [],
  components: {
    Error,
    Search,
    BreadCrumbs,
    Themes,
    Disciplines,
    Collections,
    Materials,
    Spinner
  },
  mounted() {
    const { community } = this.$route.params;
    this.$store.dispatch('getCommunity', community).finally(() => {
      this.isLoading = false;
    });
    this.$store.dispatch('getCommunityThemes', community);
    this.$store.dispatch('getCommunityDisciplines', community);
    this.$store.dispatch('getCommunityCollections', community);
    this.$store.dispatch('searchMaterials', {
      page_size: 4,
      search_text: []
    });
  },
  data() {
    return {
      isLoading: true,
      isSearch: false,
      search: false
    };
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
    ...mapGetters([
      'community_disciplines',
      'community_themes',

      'community_collections_loading',
      'materials',
      'materials_loading',
      'user',
    ]),
    community_collections() {
      let communityCollections = this.$store.getters.getPublicCollections(this.user);
      return (this.isLoading || !_.isEmpty(communityCollections)) ? communityCollections : null;
    },
    community_info() {
      let communityInfo = this.$store.getters.getCommunityInfo(this.user);
      return (this.isLoading || !_.isEmpty(communityInfo)) ? communityInfo : null;
    }
  }
};
