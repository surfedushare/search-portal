<template>
  <div tabindex="-1" @focusout="onFocusOut">
    <FilterDropdown
      v-for="dropdown in dropdowns"
      :key="dropdown.field"
      :label="dropdown.label"
      :field="dropdown.field"
      :default-option="dropdown.defaultOption"
      :state="dropdown.state"
      :filters="dropdownData ? dropdownData[dropdown.field].children : []"
      @toggle="onToggle"
      @update:selection="onSelection"
    />
  </div>
</template>

<script>
import FilterDropdown from '@/components/FilterCategories/FilterDropdown'
import { THEME_CATEGORY_FILTER_FIELD } from '@/constants'
import { keyBy } from 'lodash'
import { mapGetters } from 'vuex'

export default {
  name: 'SearchDomain',
  components: {
    FilterDropdown,
  },
  data() {
    return {
      dropdowns: [
        {
          field: 'technical_type',
          label: this.$i18n.t('searching-for-a'),
          defaultOption: this.$i18n.t('material'),
          state: false
        },
        {
          field: THEME_CATEGORY_FILTER_FIELD,
          label: this.$i18n.t('about'),
          defaultOption: this.$i18n.t('all-themes'),
          state: false
        },
        {
          field: 'language.keyword',
          label: this.$i18n.t('in'),
          defaultOption: this.$i18n.t('dutch-or-english'),
          state: false
        },
        {
          field: 'lom_educational_levels',
          label: this.$i18n.t('for'),
          defaultOption: this.$i18n.t('all-levels'),
          state: false
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
    onSelection(selection) {
      this.$emit('update:filter', selection)
    },
    onToggle(dropdown) {
      this.dropdowns.map(dd => dd.field !== dropdown.field ? dd.state = false : dd.state = !dd.state);
    },
    onFocusOut(event) {
      const element = event.target;
      if (!element.contains(event.relatedTarget) && event.relatedTarget?.className !== 'main__info_search__domain' && event.relatedTarget?.type !== 'checkbox') {
        this.dropdowns.map(dd => dd.state = false);
      }
    }
  },
}
</script>

<style lang="less">
@import "../../variables";
</style>

