import Popup from '~/components/Popup';
import StarRating from '~/components/StarRating';
export default {
  name: 'save-rating',
  props: ['value', 'is-show', 'close', 'on-save-rating'],
  components: {
    Popup,
    StarRating
  },
  mounted() {},
  data() {
    return {
      rating: 0
    };
  },
  methods: {},
  computed: {}
};
