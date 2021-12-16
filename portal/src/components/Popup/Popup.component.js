export default {
  name: 'popup',
  props: ['isShow', 'close', 'auto_width'],
  mounted() {
    document.body.addEventListener('keyup', this.closeOnEsc)
  },
  data() {
    return {
      show: this.isShow,
      width_auto: this.auto_width ? 'auto' : 'fixed',
    }
  },
  methods: {
    /**
     * Close popup on press Escape button
     * @param e - Event
     */
    closeOnEsc(e) {
      if (e.keyCode === 27) {
        this.onClose()
      }
    },
    /**
     * Close popup
     */
    onClose() {
      if (!this.disableClose) {
        if (this.close) {
          this.close()
        } else {
          this.show = !this.show
        }
        document.body.removeEventListener('keyup', this.closeOnEsc)
      }
    },
  },
  computed: {},
  watch: {
    /**
     * Watcher on change the "isShow" field
     * @param isShow - Boolean
     */
    isShow(isShow) {
      this.show = isShow
    },
    /**
     * Watcher on change the "auto_width" field
     * @param auto_width - String
     */
    auto_width(auto_width) {
      this.width_auto = auto_width ? 'auto' : 'fixed'
    },
  },
}
