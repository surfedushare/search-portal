<template>
  <div class="presearchfilters" v-if="dropdownData" tabindex="-1" @focusout="onFocusOut">
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
          label: this.$i18n.t('searching-for-a'),
          defaultOption: this.$i18n.t('material'),
          visible: false
        },
        {
          field: THEME_CATEGORY_FILTER_FIELD,
          label: this.$i18n.t('about'),
          defaultOption: this.$i18n.t('all-themes'),
          visible: false
        },
        {
          field: 'lom_educational_levels',
          label: this.$i18n.t('for'),
          defaultOption: this.$i18n.t('all-levels'),
          visible: false
        },
        {
          field: 'language.keyword',
          label: this.$i18n.t('in'),
          defaultOption: this.$i18n.t('dutch-or-english'),
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
      this.dropdowns.map(dd => dd.field !== dropdown.field ? dd.visible = false : dd.visible = !dd.visible);
    },
    onFocusOut(event) {
      const element = event.target;
      if (element.contains(event.relatedTarget)
        && !(event.relatedTarget?.className == 'search_bar__filters' || event.relatedTarget?.type == 'checkbox')
        || event.relatedTarget?.type == 'search'
        || event.relatedTarget?.type == 'submit') {
        this.dropdowns.map(dd => dd.visible = false);
      }
    }
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

