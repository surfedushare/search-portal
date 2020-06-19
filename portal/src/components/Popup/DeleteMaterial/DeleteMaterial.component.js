import Popup from '~/components/Popup'
export default {
  name: 'delete-material',
  props: ['is-show', 'close', 'collection', 'deletefunction'],
  components: {
    Popup
  },
  mounted() {},
  data() {
    return {
      formData: {
        title: null
      }
    }
  },
  methods: {
    deleteCollection() {
      this.deletefunction()
    }
  },
  computed: {}
}
