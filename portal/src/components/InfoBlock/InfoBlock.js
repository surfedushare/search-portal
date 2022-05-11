export default {
  props: {
    title: "",
    content: "",
    logo_src: { default: null, type: String },
    website_url: "",
  },
  computed: {
    logo() {
      return this.logo_src || "../../assets/images/pictures/hoe-werkt-het.png";
    },
  },
};
