import { mapGetters } from 'vuex';
import Menu from './Menu';
export default {
  name: 'main-header',
  props: [],
  components: {
    Menu
  },
  mounted() {},
  data() {
    return {};
  },
  methods: {
    getLoginLink() {
      return `${this.$axios.defaults.baseURL}/login/?redirect_url=${
        window.location
      }`;
    },
    logout() {
      this.$store.dispatch('logout').then(() => {
        // location.reload();
        window.location = process.env.logoutURL;
      });
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'user'])
  }
};
