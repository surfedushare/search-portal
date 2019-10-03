import { mapGetters } from 'vuex';
import StarRating from './../StarRating';
import _ from 'lodash';

export default {
  name: 'materials',
  props: {
    materials: {
      default: false
    },
    'items-in-line': {
      type: Number,
      default: 4
    },
    'items-length': {
      type: [Number, String],
      default: 'auto'
    },
    loading: {
      type: Boolean,
      default: false
    },
    contenteditable: {
      type: Boolean,
      default: false
    },
    value: {
      // type: Array,
      // default: []
    }
  },
  components: {
    StarRating
  },
  mounted() {
    this.$store.dispatch('getFilterCategories');
  },
  data() {
    return {
      selected_materials: this.value || []
    };
  },
  methods: {
    getTitleTranslation( community, language ) {
      if (!_.isNil(community.title_translations) && !_.isEmpty(community.title_translations)){
        return community.title_translations[language];
      }
      return community.name
      },
    /**
     * Set material on click
     * @param material - {Object}
     */
    setMaterial(material) {
      this.$store.commit('SET_MATERIAL', material);
    },
    /**
     * Select material
     * @param material - {Object}
     */
    selectMaterial(material) {
      let selected_materials = this.value.slice(0);

      if (selected_materials.indexOf(material.external_id) === -1) {
        selected_materials.push(material.external_id);
      } else {
        selected_materials = selected_materials.filter(
          item => item !== material.external_id
        );
      }
      this.$emit('input', selected_materials);
    }
  },
  watch: {
    value(value) {
      this.selected_materials = value;
    }
  },
  computed: {
    ...mapGetters([
      'disciplines',
      'materials_loading'
    ]),
    current_loading() {
      return this.materials_loading || this.loading;
    },
    /**
     * Extend to the material fields "disciplines" & "educationallevels"
     * @returns {*}
     */
    extended_materials() {
      const {
        materials,
        disciplines,
        selected_materials
      } = this;
      let arrMaterials;
      if (materials && disciplines) {
        if (materials.records) {
          arrMaterials = materials.records;
        } else {
          arrMaterials = materials;
        }
        let self = this;
        return arrMaterials.map(material => {
          return Object.assign(
            {
              selected: selected_materials.indexOf(material.external_id) !== -1
            },
            material,
            {
              disciplines: material.disciplines.reduce((prev, id) => {
                const item = disciplines[id];

                if (item) {
                  prev.push(item);
                }

                return prev;
              }, []),
              description:
                material.description && material.description.length > 200
                  ? material.description.slice(0, 200) + '...'
                  : material.description,
              educationallevels: material.educationallevels.reduce(
                (prev, id) => {
                  const item = self.$store.getters.getCategoryById(id);

                  if (item) {
                    prev.push(item);
                  }

                  return prev;
                },
                []
              )
            }
          );
        });
      }

      return false;
    }
  }
};
