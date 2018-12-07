import Popup from '~/components/Popup';
import StarRating from '~/components/StarRating';
export default {
  name: 'save-rating',
  props: ['value', 'is-show', 'close', 'material'],
  components: {
    Popup,
    StarRating
  },
  mounted() {},
  data() {
    return {
      saved: false,
      submitting: false,
      rating: 0
    };
  },
  methods: {
    /**
     * Save rating
     */
    onSaveRating() {
      this.submitting = true;
      this.$store.dispatch('setMaterialRating', this.rating).then(() => {
        this.$store.dispatch('getMaterial', this.$route.params.id).then(() => {
          this.submitting = false;
          this.saved = true;
        });
      });
    }
  },
  computed: {}
};
