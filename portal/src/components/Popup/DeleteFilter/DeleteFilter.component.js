import Popup from '~/components/Popup'
export default {
  name: 'delete-filter',
  props: ['is-show', 'close', 'collection', 'deletefunction'],
  components: {
    Popup,
  },
  mounted() {},
  data() {
    return {
      formData: {
        title: null,
      },
    }
  },
  methods: {
    deleteFilter() {
      this.deletefunction()
    },
  },
  computed: {},
}
