import { generateSearchMaterialsQuery } from '../_helpers';
import _ from 'lodash';

export default {
  name: 'disciplines',
  props: ['disciplines', 'theme'],
  methods: {
    getTitleTranslation( discipline, language ) {
      if (!_.isNil(discipline.title_translations) && !_.isEmpty(discipline.title_translations)){
        return discipline.title_translations[language];
      }
      return discipline.name
    },
    generateSearchMaterialsQuery: generateSearchMaterialsQuery,
    /**
     * Generate link URL
     * @param discipline
     * @returns {{path, query}}
     */
    generateLink(discipline) {
      const filters = [
        {
          external_id: 'lom.classification.obk.discipline.id',
          items: [discipline.external_id]
        }
      ];
      return this.generateSearchMaterialsQuery({
        page: 1,
        page_size: 10,
        filters: filters,
        search_text: [],
        return_filters: false
      });
    }
  }
};
