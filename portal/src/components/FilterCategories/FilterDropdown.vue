<template>
  <div class="dropdown-container">
    <label>{{ label }}:</label>
    <select v-model="selection">
      <option selected>
        {{ defaultOption }}
      </option>
      <option
        v-for="filter in filters"
        :key="filter.external_id"
        :value="filter.external_id"
      >
        {{ filter.title_translations[$i18n.locale] }}
      </option>
    </select>
  </div>
</template>

<script>
export default {
  name: 'FilterDropdown',
  props: {
    label: {
      type: String,
      default: '',
    },
    field: {
      type: String,
      default: '',
    },
    defaultOption: {
      type: String,
      default: '',
    },
    filters: {
      type: Array,
      default: Array,
    },
  },
  data() {
    return {
      selection: this.defaultOption,
    }
  },
  watch: {
    selection(newSelection) {
      if (newSelection === this.defaultOption) {
        this.$emit('update:selection', { field: this.field, values: null })
        return
      }
      const selectedFilter = this.filters.find((filter) => {
        return filter.external_id === newSelection
      })
      const values = selectedFilter.children.reduce(
        (acc, child) => {
          acc.push(child.external_id)
          return acc
        },
        [newSelection]
      )
      this.$emit('update:selection', { field: this.field, values })
    },
  },
}
</script>

<style lang="less" scoped>
.dropdown-container {
  label {
    display: block;
  }
}
</style>
