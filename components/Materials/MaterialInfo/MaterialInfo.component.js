import { mapGetters } from 'vuex';
import StarRating from '~/components/StarRating';
import PopularList from '~/components/Communities/PopularList';
import numeral from 'numeral';
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
  mounted() {
    if (this.isAuthenticated) {
      this.$store
        .dispatch('getApplaudMaterial', {
          external_id: this.material.external_id
        })
        .then(applaud => {
          this.is_applauded = !!applaud.count;
          this.is_loading_applaud = false;
        });
      this.$store
        .dispatch('getMaterialRating', this.material.object_id)
        .then(rating => {
          this.rating = rating.records[0];
        });
      // this.$store.dispatch('getMaterialShare', {
      //   id: this.material.object_id,
      //   shared: this.shared_link
      // });
    } else {
      this.is_loading_applaud = false;
    }

    this.href = window.location.href;
  },
  data() {
    return {
      href: '',
      shared_link: false,
      isShow: false,
      is_loading_applaud: true,
      is_applauded: false,
      rating: false,
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
    },

    setApplaudMaterial(material) {
      this.is_loading_applaud = true;
      this.$store
        .dispatch('setApplaudMaterial', {
          external_id: material.external_id
        })
        .then(() => {
          this.is_applauded = true;
          this.$store
            .dispatch('getMaterial', this.$route.params.id)
            .then(() => {
              this.is_loading_applaud = false;
            });
        });
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'material_communities', 'themes']),
    /**
     * generate author URL
     * @returns {{path, query}}
     */
    authorUrl() {
      if (this.material) {
        this.formData.author = this.material.author;
        return generateSearchMaterialsQuery(this.formData);
      }
    },
    contedNumber() {
      return numeral(this.material.number_of_views).format('0a');
    },
    /**
     * get material themes
     * @returns {*}
     */
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
