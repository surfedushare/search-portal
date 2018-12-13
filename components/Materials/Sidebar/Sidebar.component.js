import { mapGetters } from 'vuex';
import SaveMaterialInCollection from './../../Popup/SaveMaterialInCollection';
import AddCollection from './../../Popup/AddCollection';

export default {
  name: 'sidebar',
  props: {
    material: {}
  },
  components: {
    SaveMaterialInCollection,
    AddCollection
  },
  mounted() {
    this.$store.dispatch('getMyCollections');
  },
  data() {
    return {
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
    onSaveMaterial() {
      this.submitting = true;

      this.$store
        .dispatch('setMaterialInMyCollection', {
          collection_id: this.collection,
          data: [
            {
              external_id: this.material.external_id
            }
          ]
        })
        .then(() => {
          this.$store
            .dispatch('getMaterial', this.$route.params.id)
            .then(() => {
              this.submitting = false;
            });
        });
    }
  },
  computed: {
    ...mapGetters([
      'isAuthenticated',
      'my_collections',
      'material_communities'
    ]),
    collection() {
      const { my_collections } = this;
      if (my_collections && my_collections.results.length) {
        console.log(1111, my_collections.results);
      }
      return '';
    }
  }
};
