import Datepicker from 'vuejs-datepicker'
import ClickOutside from 'vue-click-outside'
import { formatDate } from '~/store/modules/_helpers'
export default {
  name: 'dates-range',
  props: ['dates', 'inline', 'theme', 'disableFutureDays', 'category'],
  components: {
    Datepicker
  },
  mounted() {
    // prevent click outside event with popupItem.
    this.popupItem = this.$el
  },
  data() {
    const { dates } = this

    const opened = dates.some(date => date !== null)

    return {
      opened,
      disabledDates: {},
      disabled: {},
      format: 'yyyy-MM-dd',
      formData: {
        start_date: dates[0] ? new Date(dates[0]) : null,
        end_date: dates[1] ? new Date(dates[1]) : null
      }
    }
  },
  directives: {
    ClickOutside
  },
  watch: {
    dates(dates) {
      this.formData = {
        start_date: dates[0] ? new Date(dates[0]) : null,
        end_date: dates[1] ? new Date(dates[1]) : null
      }
    }
  },
  methods: {
    toggle() {
      this.opened = !this.opened
    },
    onSelectedStartDate(date) {
      this.dates[0] = date
      this.emitDates()
    },
    onSelectedEndDate(date) {
      this.dates[1] = date
      this.emitDates()
    },
    emitDates() {
      const startDate = this.dates[0]
        ? formatDate(this.dates[0], 'YYYY-MM-DD')
        : null
      const endDate = this.dates[1]
        ? formatDate(this.dates[1], 'YYYY-MM-DD')
        : null
      this.$emit('input', [startDate, endDate])
    }
  }
}
