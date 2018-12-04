import { mapGetters } from 'vuex';

export default {
  name: 'sidebar',
  props: {
    material: {}
  },
  components: {},
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
    addToCollection() {
      console.log(1111);
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated'])
  }
};
