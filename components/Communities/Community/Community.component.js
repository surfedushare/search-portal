import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import Search from '~/components/FilterCategories/Search';
import Themes from '~/components/Themes';
import Disciplines from '~/components/Disciplines';
import Collections from '~/components/Collections';
import Materials from '~/components/Materials';
import Spinner from '~/components/Spinner';
import _ from 'lodash';

export default {
  name: 'community',
  props: [],
  components: {
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
    return {
      isSearch: false,
      search: false
    };
  },
  methods: {
    /**
     * Search on submit the form
     * @param data - Object
     */
    searchInCommunity(data) {
      const { community } = this.$route.params;

      if (data.search_text && data.search_text.length) {
        this.isSearch = true;
        this.search = data;
        this.$store.dispatch('searchMaterialsInCommunity', {
          id: community,
          search: {
            page_size: 10,
            page: 1,
            search_text: data.search_text
          }
        });
      } else {
        this.isSearch = false;
        this.$store.dispatch('searchMaterials', {
          page_size: 4,
          search_text: []
        });
      }
    },
    /**
     * Load next materials
     */
    loadMore() {
      const { search, materials } = this;
      const { community } = this.$route.params;
      if (materials && search) {
        const { page_size, page, records_total } = materials;

        if (records_total > page_size * page) {
          this.$store.dispatch('searchMaterialsInCommunity', {
            id: community,
            search: {
              page_size: 10,
              page: page + 1,
              search_text: data.search_text
            }
          });
        }
      }
    },
    /**
     * Load next collections
     */
    loadMoreCollections() {
      const { community_collections, community_collections_loading } = this;

      if (community_collections.next && !community_collections_loading) {
        this.$store.dispatch('getCommunityCollectionsNextPage');
      }
    },
    /**
     * Search on clearing the search_text field
     */
    onEmptySearchText() {
      this.isSearch = false;
      this.$store.dispatch('searchMaterials', {
        page_size: 4,
        search_text: []
      });
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
    ...mapGetters([
      'community_info',
      'community_disciplines',
      'community_themes',
      'community_collections',
      'community_collections_loading',
      'materials',
      'materials_loading'
    ])
  }
};
