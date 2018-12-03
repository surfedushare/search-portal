import Datepicker from 'vuejs-datepicker';
export default {
  name: 'dates-range',
  props: [],
  components: {
    Datepicker
  },
  mounted() {},
  data() {
    return {
      disabledDates: {},
      disabled: {},
      format: 'yyyy-MM-dd',
      formData: {
        start_date: null,
        end_date: null
      }
    };
  },
  methods: {},
  computed: {}
};
