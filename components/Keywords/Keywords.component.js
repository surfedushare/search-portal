import { generateSearchMaterialsQuery } from './../_helpers';
export default {
  name: 'keywords',
  props: ['material'],
  mounted() {},
  data() {
    return {};
  },
  methods: {
    generateSearchMaterialsQuery,
    url(keyword) {
      if (keyword) {
        return this.generateSearchMaterialsQuery({
          search_text: [keyword],
          filters: [],
          ordering: '-lom.lifecycle.contribute.publisherdate',
          page: 1,
          page_size: 10
        });
      }

      return '/';
    }
  },
  computed: {}
};
