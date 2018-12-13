import { mapGetters } from 'vuex';
import StarRating from '~/components/StarRating';
import PopularList from '~/components/Communities/PopularList';
import numeral from 'numeral';
import Themes from '~/components/Themes';
import Keywords from '~/components/Keywords';
import ShareMaterial from '~/components/Popup/ShareMaterial';
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
    SaveRating,
    ShareMaterial
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

      this.setSocialCounters();
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
      isShowShareMaterial: false,
      is_loading_applaud: true,
      is_applauded: false,
      rating: false,
      is_copied: false,
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

    showShareMaterial() {
      this.isShowShareMaterial = true;
    },

    closeShareMaterial() {
      this.isShowShareMaterial = false;
      if (this.is_copied) {
        this.closeSocialSharing('link');
      }
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
    },
    setSocialCounters() {
      const { material } = this;
      const { social_counters } = this.$refs;

      if (material && material.sharing_counters && social_counters) {
        const share = material.sharing_counters.reduce(
          (prev, next) => {
            prev[next.sharing_type] = next;
            return prev;
          },
          {
            linkedin: false,
            twitter: false,
            link: false
          }
        );

        if (share.linkedin) {
          social_counters.querySelector('#linkedin_counter').innerText =
            share.linkedin.counter_value;
        }
        if (share.twitter) {
          social_counters.querySelector('#twitter_counter').innerText =
            share.twitter.counter_value;
        }
        if (share.link) {
          social_counters.querySelector('#url_counter').innerText =
            share.link.counter_value;
        }
      }
    },
    closeSocialSharing(type) {
      this.$store
        .dispatch('setMaterialSocial', {
          id: this.$route.params.id,
          params: {
            shared: type
          }
        })
        .then(() => {
          this.setSocialCounters();
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
    linkedin_counter() {
      const { material } = this;

      if (material) {
        return 2;
      }

      return 0;
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
  },
  watch: {}
};
