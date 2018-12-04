import { generateSearchMaterialsQuery } from '../_helpers';

export default {
  name: 'disciplines',
  props: ['disciplines'],
  mounted() {},
  data() {
    return {};
  },
  methods: {
    generateLink(discipline) {
      return generateSearchMaterialsQuery({
        page: 1,
        page_size: 10,
        filters: [
          {
            external_id: 'lom.classification.obk.discipline.id',
            items: [discipline.external_id]
          }
        ],
        search_text: [],
        return_filters: false
      });
    }
  },
  computed: {}
};
