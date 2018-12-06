import { mapGetters } from 'vuex';
import SaveMaterialInCollection from './../../Popup/SaveMaterialInCollection';

export default {
  name: 'sidebar',
  props: {
    material: {}
  },
  components: {
    SaveMaterialInCollection
  },
  mounted() {
    this.$store.dispatch('getMyCollections');
  },
  data() {
    return {
      submitting: false,
      isShow: false
    };
  },
  methods: {
    getLoginLink() {
      return `${this.$axios.defaults.baseURL}/login/?redirect_url=${
        window.location
      }`;
    },
    close() {
      this.isShow = false;
    },
    addToCollection() {
      this.isShow = true;
    },
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
    ...mapGetters(['isAuthenticated', 'my_collections', 'material_communities'])
  }
};
