import { mapGetters } from 'vuex';
import StarRating from '~/components/StarRating';
import PopularList from '~/components/Communities/PopularList';
import Themes from '~/components/Themes';
import Keywords from '~/components/Keywords';
import SaveRating from '~/components/Popup/SaveRating';
import { generateSearchMaterialsQuery } from './../../_helpers';
export default {
  name: 'material-info',
  props: ['material'],
  components: {
    StarRating,
    Themes,
    PopularList,
    Keywords,
    SaveRating
  },
  mounted() {},
  data() {
    return {
      isShow: false,
      formData: {
        page_size: 10,
        page: 1,
        filters: [],
        search_text: []
      }
    };
  },
  methods: {
    showPopupSaveRating() {
      this.isShow = true;
    },
    close() {
      this.isShow = false;
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'material_communities', 'themes']),
    authorUrl() {
      if (this.material) {
        this.formData.author = this.material.author;
        return generateSearchMaterialsQuery(this.formData);
      }
    },
    material_themes() {
      const { material, themes } = this;

      if (material && themes) {
        const material_themes = material.themes;

        return {
          results: themes.results.filter(theme => {
            return material_themes.indexOf(theme.external_id) !== -1;
          })
        };
      }

      return false;
    }
  }
};
