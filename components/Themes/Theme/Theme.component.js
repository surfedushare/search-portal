import { mapGetters } from 'vuex';
import _ from 'lodash';
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
    return {
      search: {
        filters: [
          {
            external_id: 'lom.technical.format',
            items: []
          }
        ]
      }
    };
  },
  methods: {
    getTitleTranslation( theme, language ) {
      if (!_.isNil(theme.title_translations) && !_.isEmpty(theme.title_translations)){
        return theme.title_translations[language];
      }
      return theme.title
    },
    getDescriptionTranslation( theme, language ) {
      if (!_.isNil(theme.description_translations) && !_.isEmpty(theme.description_translations)){
        return theme.description_translations[language];
      }
      return theme.description
    },
  },
  computed: {
    ...mapGetters([
      'theme',
      'themeDisciplines',
      'themeCommunities',
      'themeCollections',
      'materials',
      'filter'
    ])
  },
  watch: {
    /**
     * Watcher on change the theme object
     * @param theme - Object
     */
    theme(theme) {
      if (theme) {
        this.search.filters.push({
          external_id: 'custom_theme.id',
          items: [theme.external_id]
        });
      }
    }
  }
};
