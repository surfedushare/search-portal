import Datepicker from 'vuejs-datepicker';
import ClickOutside from 'vue-click-outside';
import { formatDate } from './../../store/modules/_helpers';
export default {
  name: 'dates-range',
  props: ['value', 'hide-select', 'inline'],
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
        start_date: this.value.start_date || null,
        end_date: this.value.end_date || null
      }
    };
  },
  directives: {
    ClickOutside
  },
  watch: {
    value(value) {
      this.formData = {
        start_date: value.start_date ? new Date(value.start_date) : null,
        end_date: value.end_date ? new Date(value.end_date) : null
      };
    }
  },
  methods: {
    toggle() {
      this.opened = !this.opened;
    },

    hide() {
      this.opened = false;
    },
    /**
     * Emit start date to parent v-model
     * @param date
     */
    onSelectedStartDate(date) {
      this.$emit(
        'input',
        Object.assign({}, this.value, {
          start_date: formatDate(date, 'YYYY-MM-DD')
          // start_date: date
        })
      );
    },
    /**
     * Emit end date to parent v-model
     * @param date
     */
    onSelectedEndDate(date) {
      this.$emit(
        'input',
        Object.assign({}, this.value, {
          end_date: formatDate(date, 'YYYY-MM-DD')
          // end_date: date
        })
      );
    }
  },
  computed: {}
};
