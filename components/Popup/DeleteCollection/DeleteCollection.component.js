import Popup from '~/components/Popup';
export default {
  name: 'delete-collection',
  props: ['is-show', 'close', 'collection', 'value'],
  components: {
    Popup
  },
  mounted() {},
  data() {
    return {
      saved: false,
      submitting: false,
      formData: {
        title: null
      },
      is_shared: this.collection.is_shared
    };
  },
  methods: {
    deleteCollection(id) {
      this.$store.dispatch('deleteMyCollection', id).then(() => {
        this.$router.push('/my/collections/');
      });
    }
  },
  computed: {}
};
