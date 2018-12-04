import BreadCrumbs from '~/components/BreadCrumbs';
import Search from '~/components/FilterCategories/Search/index.vue';
import { mapGetters } from 'vuex';

export default {
  name: 'communities',
  props: [],
  components: {
    Search,
    BreadCrumbs
  },
  mounted() {
    this.$store.dispatch('getCommunities');
  },
  data() {
    return {};
  },
  methods: {},
  computed: {
    ...mapGetters(['communities'])
  }
};
