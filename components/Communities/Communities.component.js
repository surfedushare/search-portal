import BreadCrumbs from '~/components/BreadCrumbs';
import Search from '~/components/FilterCategories/Search';
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
  methods: {
    setCommunity(community) {
      this.$store.commit('SET_COMMUNITY', community);
    }
  },
  computed: {
    ...mapGetters(['communities'])
  }
};
