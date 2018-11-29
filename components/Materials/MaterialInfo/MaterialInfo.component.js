import StarRating from '~/components/StarRating';
import PopularList from '~/components/Communities/PopularList';
import Themes from '~/components/Themes';
import Keywords from '~/components/Keywords';
export default {
  name: 'material-info',
  props: {
    material: {}
  },
  components: {
    StarRating,
    Themes,
    PopularList,
    Keywords
  },
  mounted() {},
  data() {
    return {};
  },
  methods: {},
  computed: {}
};
