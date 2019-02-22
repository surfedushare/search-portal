import { mapGetters } from 'vuex';
import { generateSearchMaterialsQuery } from '../_helpers';

export default {
  name: 'disciplines',
  props: ['disciplines', 'theme'],
  mounted() {},
  data() {
    return {};
  },
  methods: {
    generateSearchMaterialsQuery: generateSearchMaterialsQuery,
    /**
     * Generate link URL
     * @param discipline
     * @returns {{path, query}}
     */
    generateLink(discipline) {
      const { theme, all_educationallevels } = this;
      const filters = [
        {
          external_id: 'lom.classification.obk.discipline.id',
          items: [discipline.external_id]
        },
        all_educationallevels
      ];
      if (theme) {
        filters.push({
          external_id: 'custom_theme.id',
          items: [theme.external_id]
        });
      }
      return this.generateSearchMaterialsQuery({
        page: 1,
        page_size: 10,
        filters: filters,
        search_text: [],
        return_filters: false
      });
    }
  },
  computed: {
    ...mapGetters(['all_educationallevels'])
  }
};
