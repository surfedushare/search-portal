import { mapGetters } from 'vuex';
import Search from '~/components/FilterCategories/Search';
import BreadCrumbs from '~/components/BreadCrumbs';
import Materials from '~/components/Materials';

export default {
  props: {
    title: "",
    content: "",
    breadcrumb_items: [],
    logo_src: {default: "/images/pictures/image_home.jpg", type: String},
    featured_image: "",
    website_url: "",
  },
  components: {
    Search,
    BreadCrumbs,
    Materials
  },
  data() {
    return {
      search: {
        search_text: [],
      }
    };
  },
  computed: {
    ...mapGetters(['materials']),
  },
  mounted() {
    this.$store.dispatch('searchMaterials', {
      page_size: 4,
      search_text: [],
      return_filters: false,
    });
  }
};
