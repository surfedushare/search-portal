import { mapGetters } from 'vuex';
import Search from '~/components/FilterCategories/Search';
import PopularList from '~/components/Communities/PopularList';
import Materials from '~/components/Materials';
import Themes from '~/components/Themes';
import Disciplines from '~/components/Disciplines';
import Collections from '~/components/Collections';
import BreadCrumbs from '~/components/BreadCrumbs';

export default {
  name: 'theme',
  props: [],
  components: {
    Search,
    PopularList,
    Materials,
    Themes,
    Disciplines,
    Collections,
    BreadCrumbs
  },
  mounted() {
    this.$store.dispatch('getTheme', this.$route.params.id).then(theme => {
      this.$store.dispatch('searchMaterials', {
        page_size: 2,
        search_text: [],
        filters: [
          { external_id: 'custom_theme.id', items: [theme.external_id] }
        ],
        return_filters: false
      });
    });
    this.$store.dispatch('getThemeDisciplines', this.$route.params.id);
    this.$store.dispatch('getThemeCommunities', {
      id: this.$route.params.id,
      params: { page_size: 2 }
    });
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
      'materials',
      'filter'
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
