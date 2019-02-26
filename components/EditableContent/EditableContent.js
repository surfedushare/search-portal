export default {
  name: 'editable-content',
  components: {},
  props: {
    contenteditable: {
      type: Boolean,
      default: true
    },
    setText: {
      type: Function,
      default: false
    },
    maxlength: {
      type: Number,
      default: 20
    },
    text: {
      type: String
    }
  },
  data() {
    const keys = {
      backspace: 8,
      shift: 16,
      ctrl: 17,
      alt: 18,
      delete: 46,
      cmd: 65,
      leftArrow: 37,
      upArrow: 38,
      rightArrow: 39,
      downArrow: 40
    };

    const utils = {
      special: {},
      navigational: {},
      isSpecial(e) {
        return typeof this.special[e.keyCode] !== 'undefined';
      },
      isNavigational(e) {
        return typeof this.navigational[e.keyCode] !== 'undefined';
      }
    };

    utils.special[keys['backspace']] = true;
    utils.special[keys['shift']] = true;
    utils.special[keys['ctrl']] = true;
    utils.special[keys['alt']] = true;
    utils.special[keys['delete']] = true;
    utils.special[keys['cmd']] = true;

    utils.navigational[keys['upArrow']] = true;
    utils.navigational[keys['downArrow']] = true;
    utils.navigational[keys['leftArrow']] = true;
    utils.navigational[keys['rightArrow']] = true;

    return {
      keys,
      utils
    };
  },
  computed: {
    computed_text() {
      return this.text.slice(0, this.maxlength);
    }
  },
  mounted() {},
  watch: {
    contenteditable(isEditable) {
      if (isEditable) {
        this.$nextTick().then(() => {
          this.$refs.text.focus();
        });
      }
    }
  },
  methods: {
    onChange() {
      if (this.setText) {
        this.setText(this.$refs.text.innerText);
      }
    },
    onChangeLength(event) {
      const { utils, maxlength } = this;
      let len = event.target.innerText.trim().length;
      let hasSelection = false;
      let selection = window.getSelection();
      let isSpecial = utils.isSpecial(event);
      let isNavigational = utils.isNavigational(event);

      if (selection) {
        hasSelection = !!selection.toString();
      }

      if (isSpecial || isNavigational) {
        return true;
      }

      if (len >= maxlength && !hasSelection) {
        event.preventDefault();
        return false;
      }
    }
  }
};
