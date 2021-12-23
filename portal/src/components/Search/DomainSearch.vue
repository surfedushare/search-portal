<template>
  <div>
    <FilterDropdown
      v-for="dropdown in dropdowns"
      :key="dropdown.field"
      :label="dropdown.label"
      :field="dropdown.field"
      :default-option="dropdown.defaultOption"
      :filters="dropdownData ? dropdownData[dropdown.field].children : []"
      @update:selection="onSelection"
    />
    <Search v-model="searchText" @onSearch="onSearch" />
  </div>
</template>

<script>
import { keyBy } from 'lodash'
import Search from './index'
import { mapGetters } from 'vuex'
import FilterDropdown from '@/components/FilterCategories/FilterDropdown'

export default {
  name: 'SearchDomain',
  components: {
    Search,
    FilterDropdown,
  },
  props: {
    value: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      searchText: this.value,
      dropdowns: [
        {
          field: 'technical_type',
          label: this.$i18n.t('searching-for-a'),
          defaultOption: this.$i18n.t('material'),
        },
        {
          field: 'learning_material_themes',
          label: this.$i18n.t('about'),
          defaultOption: this.$i18n.t('all-themes'),
        },
        {
          field: 'language.keyword',
          label: this.$i18n.t('in'),
          defaultOption: this.$i18n.t('dutch-or-english'),
        },
        {
          field: 'lom_educational_levels',
          label: this.$i18n.t('for'),
          defaultOption: this.$i18n.t('alle niveaus'),
        },
      ],
      dropdownData: null,
    }
  },
  computed: {
    ...mapGetters({
      filterCategories: 'filter_categories',
      getCategoryById: 'getCategoryById',
    }),
  },
  watch: {
    value(value) {
      this.searchText = value
    },
  },
  mounted() {
    this.$store.dispatch('getFilterCategories').then(() => {
      const categories = this.dropdowns.map((dropdown) => {
        return dropdown.field
      })
      this.dropdownData = keyBy(
        categories.map((categoryId) => {
          return this.getCategoryById(categoryId)
        }),
        'external_id'
      )
    })
  },
  methods: {
    onSearch() {
      this.$emit('input', this.searchText)
      this.$emit('onSearch')
    },
    onSelection(selection) {
      this.$emit('update:filter', selection)
    },
  },
}
</script>
