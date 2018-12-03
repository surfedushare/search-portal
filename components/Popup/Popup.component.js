export default {
  name: 'popup',
  props: ['isShow', 'close', 'auto_width'],
  mounted() {
    document.body.addEventListener('keyup', this.closeOnEsc);
  },
  data() {
    return {
      show: this.isShow,
      width_auto: this.auto_width ? 'auto' : 'fixed'
    };
  },
  methods: {
    closeOnEsc(e) {
      if (e.keyCode === 27) {
        this.onClose();
      }
    },
    onClose() {
      if (!this.disableClose) {
        if (this.close) {
          this.close();
        } else {
          this.show = !this.show;
        }
        document.body.removeEventListener('keyup', this.closeOnEsc);
      }
    }
  },
  computed: {},
  watch: {
    isShow(isShow) {
      this.show = isShow;
    },
    auto_width(auto_width) {
      this.width_auto = auto_width ? 'auto' : 'fixed';
    }
  }
};
