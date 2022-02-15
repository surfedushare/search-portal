<template>
  <div class="dropdown-container">
    <label class="dropdown-container__label">{{ label }}:</label>

    <div class="dropdown-container__select" :data-test="'filter_' + field" @click="onToggle">
      <span
        role="textbox"
        :class="{ 'bold': selectedFilters !== defaultOption }"
      >{{ selectedFilters }}</span>
      <div class="dropdown-container__selector"></div>
    </div>

    <ul v-show="visible" class="dropdown-container__dropdown">
      <li v-for="filter in filters" :key="filter.external_id" :value="filter.external_id">
        <input
          v-model="filter.selected"
          type="checkbox"
          :data-test="'filter_' + field + '_' + filter.external_id"
        />
        {{ filter.title_translations[$i18n.locale] }}
      </li>
    </ul>
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
    visible: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    selectedFilters(filter) {
      const selection = this.filters
        .filter(filter => filter.selected)
        .map(filter => filter.value);
      const filterNames = this.filters
        .filter(filter => filter.selected)
        .map(filter => filter.title_translations[this.$i18n.locale].toLowerCase());

      this.$emit('update:selection', { field: this.field, selection })
      return filterNames?.length == 0 ? filter.defaultOption : filterNames.join(", ");
    }
  },
  methods: {
    onToggle() {
      this.$emit('toggle', { field: this.field })
    },
  },
}
</script>

<style lang="less" scoped>
@import "../../variables";
.dropdown-container {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  z-index: 10;
  position: relative;

  &__dropdown {
    display: grid;
    grid-auto-flow: column;
    grid-template-rows: repeat(6, auto);
    grid-auto-columns: max-content;
    column-gap: 2rem;
    position: absolute;
    top: 80px;
    background-color: @grey;
    list-style: none;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
    margin-left: -10px;
    min-width: 200px;
  }

  &__label {
    display: block;
    width: 100%;
    height: 1.5rem;
  }

  &__selector {
    position: relative;
    -webkit-transform: translate(0, -100%) rotate(90deg);
    transform: translate(0, -100%) rotate(90deg);
    width: 14px;
    height: 14px;
    left: 8px;
    top: 20px;
    background: url("/images/arrow-text-grey.svg") 50% 50% / contain no-repeat;
    &:hover {
      background: url("/images/arrow-text-green.svg") 50% 50% / contain
        no-repeat;
    }
  }

  &__select {
    position: relative;
    display: flex;
    span {
      text-overflow: ellipsis;
      font-family: "nunito";
      font-size: 16px;
      border: none;
      outline: none;
      padding: 0;
      caret-color: transparent;
      max-width: 180px;
      display: inline-block;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      &.bold {
        font-weight: bolder;
      }
    }
  }
}
</style>
