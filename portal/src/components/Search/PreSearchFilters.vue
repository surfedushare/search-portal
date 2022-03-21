<template>
  <div v-if="dropdownData" class="presearchfilters" tabindex="-1">
    <FilterDropdown
      v-for="dropdown in dropdowns"
      :key="dropdown.field"
      :label="dropdown.label"
      :field="dropdown.field"
      :default-option="dropdown.defaultOption"
      :visible="dropdown.visible"
      :filters="dropdownData && dropdownData[dropdown.field] ? dropdownData[dropdown.field].children : []"
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
  name: 'PreSearchFilters',
  components: {
    FilterDropdown,
  },
  data() {
    return {
      dropdowns: [
        {
          field: 'technical_type',
          label: 'searching-for-a',
          defaultOption: 'material',
          visible: false
        },
        {
          field: THEME_CATEGORY_FILTER_FIELD,
          label: 'about',
          defaultOption: 'all-themes',
          visible: false
        },
        {
          field: 'lom_educational_levels',
          label: 'for',
          defaultOption: 'all-levels',
          visible: false
        },
        {
          field: 'language.keyword',
          label: 'in',
          defaultOption: 'dutch-or-english',
          visible: false
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
    document.addEventListener('click', this.onClick);
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
  beforeDestroy() {
    document.removeEventListener('click', this.onClick);
  },
  methods: {
    onClick(event) {
      if (!(event.target?.className?.includes('dropdown-container')
        || event.target?.className?.includes('filter_'))
        || event.target?.type == 'search'
        || event.target?.type == 'submit') {
        this.dropdowns.map(dd => dd.visible = false)
      }
    },
    onSelection(selection) {
      this.$emit('update:filter', selection)
    },
    onToggle(dropdown) {
      this.dropdowns.map(dd => dd.field !== dropdown.field ? dd.visible = false : dd.visible = !dd.visible);
    },
  },
}
</script>

<style lang="less" scoped>
@import "../../variables";
.presearchfilters {
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: 1fr 1fr 1fr 1fr 115px;
  grid-gap: 20px;
  height: 80px;
  padding: 15px 24px;
  @media @mobile-ls {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    min-height: 160px;
  }
  @media @mobile {
    grid-auto-flow: row;
    grid-template-columns: 100%;
    min-height: 310px;
    width: 100%;
  }
}
</style>

