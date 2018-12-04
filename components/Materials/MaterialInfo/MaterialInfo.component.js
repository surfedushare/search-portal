import { mapGetters } from 'vuex';
import StarRating from '~/components/StarRating';
import PopularList from '~/components/Communities/PopularList';
import Themes from '~/components/Themes';
import Keywords from '~/components/Keywords';
import { generateSearchMaterialsQuery } from './../../_helpers';
export default {
  name: 'material-info',
  props: ['material'],
  components: {
    StarRating,
    Themes,
    PopularList,
    Keywords
  },
  mounted() {
    this.$store.dispatch('getCommunities', { params: { page_size: 2 } });
  },
  data() {
    return {
      formData: {
        page_size: 10,
        page: 1,
        filters: [],
        search_text: []
      }
    };
  },
  methods: {},
  computed: {
    ...mapGetters(['isAuthenticated', 'communities']),
    authorUrl() {
      if (this.material) {
        this.formData.author = this.material.author;
        return generateSearchMaterialsQuery(this.formData);
      }
    }
  }
};
