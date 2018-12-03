import { mapGetters } from 'vuex';
import Search from '~/components/FilterCategories/Search/index.vue';
import PopularList from '~/components/Communities/PopularList';
import Materials from '~/components/Materials';
import Themes from '~/components/Themes';
import Disciplines from '~/components/Disciplines';

export default {
  name: 'theme',
  props: [],
  components: {
    Search,
    PopularList,
    Materials,
    Themes,
    Disciplines
  },
  mounted() {
    this.$store.dispatch('searchMaterials', {
      page_size: 2,
      search_text: []
    });
    this.$store.dispatch('getTheme', this.$route.params.id);
    this.$store.dispatch('getThemeDisciplines', this.$route.params.id);
    this.$store.dispatch('getThemeCommunities', this.$route.params.id);
    this.$store.dispatch('getThemeCollections', this.$route.params.id);
  },
  data() {
    return {};
  },
  methods: {},
  computed: {
    ...mapGetters([
      'theme',
      'themeDisciplines',
      'themeCommunities',
      'themeCollections',
      'materials'
    ])
    // themesList() {
    //   if (this.material) {
    //     return this.themes.results.filter(theme => {
    //       if (this.material.themes.indexOf(theme.title) >= 0) {
    //         return theme;
    //       }
    //     });
    //   } else if (this.themes) {
    //     return this.themes.results;
    //   }
    //   return false;
    // }
  }
};
