import { mapGetters } from 'vuex';
import themes from '../../store/modules/themes';

export default {
  name: 'themes',
  props: ['material'],
  mounted() {},
  data() {
    return {};
  },
  methods: {},
  computed: {
    ...mapGetters(['themes']),
    themesList() {
      if (this.material) {
        return this.themes.results.filter(theme => {
          if (this.material.themes.indexOf(theme.title) >= 0) {
            return theme;
          }
        });
      } else if (this.themes) {
        return this.themes.results;
      }
      return false;
    }
  }
};
