import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import Search from '~/components/FilterCategories/Search/index.vue';
import Themes from '~/components/Themes';
import Disciplines from '~/components/Disciplines';
import Collections from '~/components/Collections';
import Materials from '~/components/Materials';

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
    this.$store.dispatch('getCommunity', this.$route.params.id);
    this.$store.dispatch('getCommunityThemes', this.$route.params.id);
    this.$store.dispatch('getCommunityDisciplines', this.$route.params.id);
    this.$store.dispatch('getCommunityCollections', this.$route.params.id);
    this.$store.dispatch('searchMaterials', {
      page_size: 4,
      search_text: []
    });
  },
  data() {
    return {};
  },
  methods: {},
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
