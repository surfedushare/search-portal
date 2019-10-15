import { mapGetters } from 'vuex';
import _ from 'lodash';
import Search from '~/components/FilterCategories/Search';
import PopularList from '~/components/Communities/PopularList';
import Materials from '~/components/Materials';
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
    Disciplines,
    Collections,
    BreadCrumbs
  },
  mounted() {

    let themeId = this.$route.params.id;
    this.$store.dispatch('getFilterCategories').then(() => {

      this.$store.dispatch('getTheme', themeId).then(theme => {

        let themeCategory = this.$store.getters.getCategoryById(theme.external_id);
        themeCategory.selected = true;

        this.theme = theme;
        this.$store.dispatch('searchMaterials', {
          page_size: 2,
          search_text: [],
          filters: this.$store.getters.search_filters,
          return_filters: false
        });

      });

    });

    // TODO: all data fetched below is also in the getFilterCategories above
    // We should remove these calls and use the getFilterCategories
    // That means switching from theme.id to theme.external_id
    this.$store.dispatch('getThemeDisciplines', themeId);
    this.$store.dispatch('getThemeCommunities', {
      id: this.$route.params.id,
      params: { page_size: 2 }
    });
    this.$store.dispatch('getThemeCollections', themeId);

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
      },
      theme: null
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
  }
};
