import { mapGetters } from 'vuex';
import SaveMaterialInCollection from './../../Popup/SaveMaterialInCollection';

export default {
  name: 'sidebar',
  props: {
    material: {}
  },
  components: {
    SaveMaterialInCollection
  },
  mounted() {},
  data() {
    return {
      isShow: false
    };
  },
  methods: {
    getLoginLink() {
      return `${this.$axios.defaults.baseURL}/login/?redirect_url=${
        window.location
      }`;
    },
    close() {
      this.isShow = false;
    },
    addToCollection() {
      this.isShow = true;
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated'])
  }
};
