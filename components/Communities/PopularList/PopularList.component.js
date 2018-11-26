import { mapGetters } from 'vuex';

export default {
  name: 'popular-list',
  props: ['page_size'],
  mounted() {
    const { page_size } = this;
    const params = page_size ? { page_size } : { page_size: 3 };
    this.$store.dispatch('getCommunities', { params });
  },
  data() {
    return {};
  },
  methods: {},
  computed: {
    ...mapGetters(['communities'])
  }
};
