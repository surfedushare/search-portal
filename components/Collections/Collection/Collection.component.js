import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import DirectSearch from '~/components/FilterCategories/DirectSearch';

export default {
  name: 'collection',
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
    return {
      contenteditable: true
    };
  },
  methods: {},
  computed: {
    collection_title() {
      return this.collection ? this.collection.title : false;
    }
  }
};
