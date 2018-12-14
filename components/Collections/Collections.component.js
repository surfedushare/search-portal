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
    setMyCollection(collection) {
      this.$store.commit('SET_MY_COLLECTION', collection);
    }
  },
  computed: {}
};
