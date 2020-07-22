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
      accept: 'image/jpeg,image/gif,image/png'
    }
  },
  watch: {},
  methods: {
    onFileChange(e) {
      const files = e.target.files || e.dataTransfer.files
      if (!files.length) return
      this.$emit('add_image', files[0])
      this.createImage(files[0])
    },
    createImage(file) {
      const reader = new FileReader()
      const that = this

      reader.onload = e => {
        that.image = e.target.result
        that.$emit('preview_url', e.target.result)
      }
      reader.readAsDataURL(file)
    },
    removeImage: function() {
      this.$emit('remove_image')
      this.image = null
      this.$refs.file.value = null
    }
  },
  computed: {
    imagePath() {
      return this.image !== null ? this.image : this.imagesrc
    }
  }
}
