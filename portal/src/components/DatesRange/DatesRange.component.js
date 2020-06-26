import Datepicker from 'vuejs-datepicker'
import ClickOutside from 'vue-click-outside'
import { formatDate } from '~/store/modules/_helpers'
export default {
  name: 'dates-range',
  props: ['value', 'hideSelect', 'inline', 'theme', 'disableFutureDays', 'datesFilter'],
  components: {
    Datepicker
  },
  mounted() {
    // prevent click outside event with popupItem.
    this.popupItem = this.$el
  },
  data() {
    const { datesFilter } = this
    return {
      opened: false,
      disabledDates: {},
      disabled: {},
      format: 'yyyy-MM-dd',
      formData: {
        start_date: datesFilter.start_date ? new Date(datesFilter.start_date) : null,
        end_date: datesFilter.end_date ? new Date(datesFilter.end_date) : null
      }
    }
  },
  directives: {
    ClickOutside
  },
  methods: {
    /**
     * Toggling the popup visibility
     */
    toggle() {
      this.opened = !this.opened
    },
    /**
     * Hiding popup
     */
    hide() {
      this.opened = false
    },
    onSelectedStartDate(date) {
      this.formData.start_date = date
      this.emitDates()
    },
    onSelectedEndDate(date) {
      this.formData.end_date = date
      this.emitDates()
    },
    emitDates() {
      const startDate = this.formData.start_date ? formatDate(this.formData.start_date, 'YYYY-MM-DD') : null
      const endDate = this.formData.end_date ? formatDate(this.formData.end_date, 'YYYY-MM-DD') : null
      this.$emit('input', {
        start_date: startDate,
        end_date: endDate
      })
    }
  },
  computed: {}
}
