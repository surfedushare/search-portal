import { mapGetters } from 'vuex';
import SaveMaterialInCollection from './../../Popup/SaveMaterialInCollection';
import AddCollection from './../../Popup/AddCollection';
import Multiselect from './../../Multiselect';

export default {
  name: 'sidebar',
  props: {
    material: {}
  },
  components: {
    SaveMaterialInCollection,
    AddCollection,
    Multiselect
  },
  mounted() {
    this.$store.dispatch('getMyCollections');

    this.$store
      .dispatch('checkMaterialInCollection', this.material.external_id)
      .then(collections => {
        const checked_collections = collections.results.map(item => item.id);
        this.my_checked_collections = checked_collections;
        this.checked_collections = checked_collections.slice(0);

        this.$nextTick().then(() => {
          this.full_loading = true;
        });
      });
  },
  data() {
    return {
      full_loading: false,
      collection: '',
      checked_collections: [],
      submitting: false,
      isShowSaveMaterial: false,
      isShowAddCollection: false
    };
  },
  methods: {
    /**
     * generate login URL
     * @returns {string}
     */
    getLoginLink() {
      return `${this.$axios.defaults.baseURL}/login/?redirect_url=${
        window.location
      }`;
    },
    /**
     * Show AddCollection popup
     */
    addCollection() {
      this.isShowAddCollection = true;
    },
    /**
     * Close AddCollection popup
     */
    closeAddCollection() {
      this.isShowAddCollection = false;
    },
    /**
     * Show SaveMaterial popup
     */
    addToCollection() {
      this.isShowSaveMaterial = true;
    },
    /**
     * Close SaveMaterial popup
     */
    closeSaveMaterial() {
      this.isShowSaveMaterial = false;
    },
    /**
     * Triggering event the save material
     */
    onSaveMaterial(collection) {
      this.submitting = true;

      return this.$store.dispatch('setMaterialInMyCollection', {
        collection_id: collection.id || collection,
        data: [
          {
            external_id: this.material.external_id
          }
        ]
      });
    },
    /**
     * Triggering event the remove material
     */
    onRemoveMaterial(collection) {
      this.submitting = true;

      return this.$store.dispatch('removeMaterialFromMyCollection', {
        collection_id: collection.id || collection,
        data: [
          {
            external_id: this.material.external_id
          }
        ]
      });
    }
  },
  computed: {
    ...mapGetters([
      'isAuthenticated',
      'my_collections',
      'material_communities',
      'disciplines',
      'educationallevels'
    ]),
    /**
     * Extend to the material fields "disciplines" & "educationallevels"
     * @returns {*}
     */
    extended_material() {
      const { material, disciplines, educationallevels } = this;
      if (material && disciplines && educationallevels) {
        return Object.assign({}, material, {
          disciplines: material.disciplines.reduce((prev, id) => {
            const item = disciplines.items[id];

            if (item) {
              prev.push(item);
            }

            return prev;
          }, []),
          educationallevels: material.educationallevels.reduce((prev, id) => {
            const item = educationallevels.items[id];

            if (item) {
              prev.push(item);
            }

            return prev;
          }, [])
        });
      }

      return false;
    }
  },
  watch: {
    /**
     * Get checked collection
     * @param collections - Array
     */
    checked_collections(collections) {
      if (this.full_loading) {
        let collections_for_material = {};
        if (collections.length) {
          collections_for_material = collections.reduce(
            (prev, next) => {
              if (this.my_checked_collections.indexOf(next) === -1) {
                prev.add.push(next);
              }
              if (prev.delete.length) {
                prev.delete = prev.delete.filter(item => item !== next);
              }
              return prev;
            },
            {
              add: [],
              delete: this.my_checked_collections.slice(0)
            }
          );
        } else {
          collections_for_material = {
            add: [],
            delete: this.my_checked_collections.slice(0)
          };
        }

        const requests = [];

        if (
          collections_for_material.add &&
          collections_for_material.add.length
        ) {
          collections_for_material.add.forEach(collection => {
            requests.push(this.onSaveMaterial(collection));
          });
        }

        if (
          collections_for_material.delete &&
          collections_for_material.delete.length
        ) {
          collections_for_material.delete.forEach(collection => {
            requests.push(this.onRemoveMaterial(collection));
          });
        }

        Promise.all(requests).then(() => {
          this.$store
            .dispatch('getMaterial', this.$route.params.id)
            .then(() => {
              this.submitting = false;
            });
        });

        this.my_checked_collections = collections.slice(0);
      }
    }
  }
};
