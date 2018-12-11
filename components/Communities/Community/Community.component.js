import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import Search from '~/components/FilterCategories/Search';
import Themes from '~/components/Themes';
import Disciplines from '~/components/Disciplines';
import Collections from '~/components/Collections';
import Materials from '~/components/Materials';
import { generateSearchMaterialsQuery } from '../../_helpers';

export default {
  name: 'community',
  props: [],
  components: {
    Search,
    BreadCrumbs,
    Themes,
    Disciplines,
    Collections,
    Materials
  },
  mounted() {
    const { community } = this.$route.params;
    this.$store.dispatch('getCommunity', community);
    this.$store.dispatch('getCommunityThemes', community);
    this.$store.dispatch('getCommunityDisciplines', community);
    this.$store.dispatch('getCommunityCollections', community);
    this.$store.dispatch('searchMaterials', {
      page_size: 4,
      search_text: []
    });
  },
  data() {
    return {};
  },
  methods: {
    searchInCommunity(data) {
      console.log(
        11111,
        generateSearchMaterialsQuery(
          data,
          `/communities/${this.$route.params.community}/search/`
        )
      );
    }
  },
  computed: {
    ...mapGetters([
      'community_info',
      'community_disciplines',
      'community_themes',
      'community_collections',
      'materials'
    ])
  }
};
