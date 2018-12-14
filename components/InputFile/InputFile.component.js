export default {
  name: 'input-file',
  mounted() {},
  props: {
    imagesrc: {
      default: false
    },
    title: {
      default: ''
    },
    refinput: {
      default: 'file'
    }
  },
  data() {
    return {
      image: null,
      imageText: null,
      imageLink: null,
      accept: 'image/jpeg,image/gif,image/png'
    };
  },
  watch: {},
  methods: {
    onFileChange(e) {
      let files = e.target.files || e.dataTransfer.files;
      if (!files.length) return;
      this.createImage(files[0]);
      console.log(files[0]);
      this.imageText = files[0].name;
    },
    createImage(file) {
      let image = new Image();
      let reader = new FileReader();
      let that = this;

      reader.onload = e => {
        that.image = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    removeImage: function(e) {
      this.image = '';
      this.imageText = '';
      this.imageLink = '';
    }
  },
  computed: {
    imagePath() {
      this.imageLink = this.image;
      return this.imageLink !== null ? this.imageLink : this.imagesrc;
    },
    imagePathTxt() {
      return this.imageText !== null ? this.imageText : this.imagesrc;
    }
  }
};
