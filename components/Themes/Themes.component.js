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
      if (themes && themes.results && themes.results.length) {
        return themes.results;
      }
      return themes;
    }
  }
};
