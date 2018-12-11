export default {
  name: 'themes',
  props: ['themes'],
  mounted() {},
  data() {
    return {};
  },
  methods: {},
  computed: {
    currentThemes() {
      const themes = this.themes;
      if (themes) {
        if (themes.results) {
          return themes.results.length ? themes.results : false;
        }
        return themes;
      }
      return false;
    }
  }
};
