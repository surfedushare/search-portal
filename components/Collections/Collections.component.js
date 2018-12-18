export default {
  name: 'collections',
  props: {
    collections: {
      default: false
    },
    'items-in-line': {
      type: Number,
      default: 4
    }
  },
  components: {},
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
      this.$store.commit('SET_MY_COLLECTION', collection);
    }
  },
  computed: {}
};
