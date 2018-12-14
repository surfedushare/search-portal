import BreadCrumbs from '~/components/BreadCrumbs';
import DirectSearch from '~/components/FilterCategories/DirectSearch';

export default {
  name: 'collection',
  props: {
    collection: {
      default: false
    },
    contenteditable: {
      default: false
    },
    setEditable: {
      default: false
    },
    changeViewType: {
      default: false
    },
    'items-in-line': {
      default: 4
    }
  },
  components: {
    BreadCrumbs,
    DirectSearch
  },
  mounted() {
    const { collection } = this;
    if (collection) {
      this.setTitle(collection.title);
    }
    this.href = window.location.href;
  },
  data() {
    return {
      href: '',
      collection_title: null,
      search: {}
    };
  },
  methods: {
    setTitle(title) {
      this.collection_title = title;
      if (this.$refs.title) {
        this.$refs.title.innerText = title;
      }
    },
    onChangeTitle() {
      this.setTitle(this.$refs.title.innerText);
    },
    resetData() {
      this.setTitle(this.collection.title);
    },
    deleteCollection(id) {
      this.$store.dispatch('deleteMyCollection', id).then(() => {
        this.$router.push('/my/collections/');
      });
    }
  },
  computed: {},
  watch: {
    search(search) {
      this.$emit('input', search);
    },
    contenteditable(isEditable) {
      const { title } = this.$refs;
      this.$nextTick().then(() => {
        title.focus();
      });
      if (!isEditable) {
        this.resetData();
      }
    },
    collection(collection) {
      if (collection) {
        this.setTitle(collection.title);
      }
    }
  }
};
