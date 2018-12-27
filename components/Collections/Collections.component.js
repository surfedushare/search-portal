import Spinner from './../Spinner';

export default {
  name: 'collections',
  props: {
    collections: {
      default: false
    },
    'items-in-line': {
      type: Number,
      default: 4
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  components: { Spinner },
  mounted() {},
  data() {
    return {};
  },
  methods: {
    /**
     * Set my collection on click
     * @param collection - {Object}
     */
    setMyCollection(collection) {
      this.$store.commit('SET_MATERIAL_TO_MY_COLLECTION', false);
      this.$store.commit('SET_MY_COLLECTION', collection);
    }
  },
  computed: {}
};
