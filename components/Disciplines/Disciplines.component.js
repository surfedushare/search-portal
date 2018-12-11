import { generateSearchMaterialsQuery } from '../_helpers';

export default {
  name: 'disciplines',
  props: ['disciplines', 'theme'],
  mounted() {},
  data() {
    return {};
  },
  methods: {
    /**
     * Generate link URL
     * @param discipline
     * @returns {{path, query}}
     */
    generateLink(discipline) {
      const theme = this.theme;
      const filters = [
        {
          external_id: 'lom.classification.obk.discipline.id',
          items: [discipline.external_id]
        }
      ];
      if (theme) {
        filters.push({
          external_id: 'custom_theme.id',
          items: [theme.external_id]
        });
      }
      return generateSearchMaterialsQuery({
        page: 1,
        page_size: 10,
        filters: filters,
        search_text: [],
        return_filters: false
      });
    }
  },
  computed: {}
};
