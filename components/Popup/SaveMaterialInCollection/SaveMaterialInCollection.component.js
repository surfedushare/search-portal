import { mapGetters } from 'vuex';
import Popup from './../../Popup';
export default {
  name: 'save-material-in-collection',
  props: ['isShow', 'close', 'material'],
  components: {
    Popup
  },
  mounted() {
    this.$store.dispatch('getMyCollections');
  },
  data() {
    return {
      collection: null
    };
  },
  methods: {
    onSaveMaterial() {
      this.$store.dispatch('setMaterialInMyCollection', {
        collection_id: this.collection,
        data: [
          {
            external_id: this.material.external_id
          }
        ]
      });
    }
  },
  computed: {
    ...mapGetters(['my_collections'])
  }
};
