import { mapGetters } from 'vuex';

export default {
  name: 'filter-categories',
  props: [],
  mounted() {},
  data() {
    return {};
  },
  methods: {},
  computed: {
    ...mapGetters(['filter_categories'])
  }
};
