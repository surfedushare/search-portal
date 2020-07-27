export default {
  props: {
    title: '',
    content: '',
    logo_src: { default: null, type: String },
    website_url: ''
  },
  computed: {
    logo() {
      return this.logo_src || '/images/pictures/image_home.jpg'
    }
  }
}
