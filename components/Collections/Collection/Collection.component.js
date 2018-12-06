import BreadCrumbs from '~/components/BreadCrumbs';
import DirectSearch from '~/components/FilterCategories/DirectSearch';

export default {
  name: 'collections',
  props: {
    collection: {
      default: false
    }
  },
  components: {
    BreadCrumbs,
    DirectSearch
  },
  mounted() {},
  data() {
    return {};
  },
  methods: {},
  computed: {}
};
