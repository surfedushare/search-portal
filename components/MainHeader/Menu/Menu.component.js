import { mapGetters } from 'vuex';

export default {
  name: 'menu-block',
  props: [],
  mounted() {},
  data() {
    return {
      isShowSubMenu: false
    };
  },
  methods: {
    toggleSubMenu() {
      this.isShowSubMenu = !this.isShowSubMenu;
    },
    closeSubMenu() {
      this.isShowSubMenu = false;
    }
  },
  computed: {
    ...mapGetters(['themes'])
  }
};
