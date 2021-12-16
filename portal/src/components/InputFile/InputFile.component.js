import ImageCropPopup from '~/components/Popup/ImageCropPopup'

export default {
  name: 'input-file',
  props: {
    imagesrc: {
      default: false,
    },
    title: {
      default: '',
    },
    refinput: {
      default: 'file',
    },
    width: {
      type: Number,
      default: 100,
    },
    height: {
      type: Number,
      default: 50,
    },
  },
  components: {
    ImageCropPopup,
  },
  data() {
    return {
      image: null,
      accept: 'image/jpeg,image/gif,image/png',
      showPopup: false,
    }
  },
  methods: {
    onFileChange(e) {
      const files = e.target.files || e.dataTransfer.files
      if (!files.length) return
      this.openModal(files[0])
    },
    openModal(file) {
      const reader = new FileReader()

      reader.onload = (e) => {
        this.originalImage = e.target.result
        this.name = file.name
        this.showPopup = true
      }
      reader.readAsDataURL(file)
    },
    removeImage: function () {
      this.$emit('remove_image')
      this.image = null
      this.$refs.file.value = null
    },
    onCrop(croppedImage) {
      const file = new File([croppedImage], this.name)
      this.$emit('add_image', file)
    },
    onPreview(preview) {
      this.image = preview
      this.$emit('preview_url', preview)
    },
    closePopup() {
      this.$refs.file.value = null
      this.showPopup = false
    },
  },
  computed: {
    imagePath() {
      return this.image !== null ? this.image : this.imagesrc
    },
  },
}
