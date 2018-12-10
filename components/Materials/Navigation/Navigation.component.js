import { generateSearchMaterialsQuery } from './../../_helpers';
export default {
  name: 'navigation',
  props: ['materials', 'material'],
  components: {},
  mounted() {},
  data() {
    return {};
  },
  methods: {},
  computed: {
    links() {
      const { materials, material } = this;
      if (materials) {
        const { records } = materials;
        if (records && records.length && material) {
          const materialIndex = records.findIndex(
            record => record.external_id === material.external_id
          );

          if (materialIndex !== -1) {
            return {
              prev: materialIndex ? records[materialIndex - 1] : null,
              filter:
                generateSearchMaterialsQuery({
                  filters: materials.filters,
                  page: 1,
                  page_size: materials.page_size,
                  search_text: materials.search_text,
                  ordering: materials.ordering
                }) || null,
              next: records[materialIndex + 1]
            };
          }
        }
      }
      return {
        prev: null,
        filter: null,
        next: null
      };
    }
  }
};
