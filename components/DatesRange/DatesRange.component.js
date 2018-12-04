import Datepicker from 'vuejs-datepicker';
import ClickOutside from 'vue-click-outside';
import { formatDate } from './../../store/modules/_helpers';
export default {
  name: 'dates-range',
  props: ['value'],
  components: {
    Datepicker
  },
  mounted() {
    // prevent click outside event with popupItem.
    this.popupItem = this.$el;
  },
  data() {
    return {
      opened: false,
      disabledDates: {},
      disabled: {},
      format: 'yyyy-MM-dd',
      formData: {
        start_date: null,
        end_date: null
      }
    };
  },
  directives: {
    ClickOutside
  },
  watch: {
    'formData.start_date'(date) {
      this.$emit(
        'input',
        Object.assign({}, this.value, {
          start_date: formatDate(date, 'YYYY-MM-DD')
          // start_date: date
        })
      );
    },
    'formData.end_date'(date) {
      this.$emit(
        'input',
        Object.assign({}, this.value, {
          end_date: formatDate(date, 'YYYY-MM-DD')
          // end_date: date
        })
      );
    }
  },
  methods: {
    toggle() {
      this.opened = !this.opened;
    },

    hide() {
      this.opened = false;
    }
  },
  computed: {}
};
