<template>
  <div class="dropdown-container">
    <label class="dropdown-container__label">{{ $t(label) }}:</label>

    <div
      :class="{ active: visible === true }"
      class="dropdown-container__select"
      :data-test="'filter_' + field"
      @click="onToggle"
    >
      <span role="textbox" :class="{ bold: selectedFilters !== $t(defaultOption) }" class="filter_checkbox">{{
        selectedFilters
      }}</span>
      <div class="dropdown-container__selector" :class="{ active: visible === true }"></div>
    </div>

    <ul v-show="visible" class="dropdown-container__dropdown">
      <li v-for="filter in visibleFilters" :key="filter.external_id" :value="filter.external_id">
        <label class="filter_label">
          <input
            v-model="filter.selected"
            type="checkbox"
            :data-test="'filter_' + field + '_' + filter.external_id"
            class="filter_checkbox"
          />
          {{ filter.title_translations[$i18n.locale] }}
        </label>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "FilterDropdown",
  props: {
    label: {
      type: String,
      default: "",
    },
    field: {
      type: String,
      default: "",
    },
    defaultOption: {
      type: String,
      default: "",
    },
    filters: {
      type: Array,
      default: Array,
    },
    visible: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    selectedFilters(filter) {
      const selection = this.filters.filter((filter) => filter.selected).map((filter) => filter.value);
      const filterNames = this.filters
        .filter((filter) => filter.selected)
        .map((filter) => filter.title_translations[this.$i18n.locale].toLowerCase());

      this.$emit("update:selection", { field: this.field, selection });
      return filterNames?.length === 0 ? this.$i18n.t(filter.defaultOption) : filterNames.join(", ");
    },
    visibleFilters() {
      return this.filters.filter((x) => !x.is_hidden).sort();
    },
  },
  methods: {
    onToggle() {
      this.$emit("toggle", { field: this.field });
    },
  },
};
</script>

<style lang="less" scoped>
@import "../../variables";
input {
  appearance: none;
}

input[type="checkbox"]:before {
  content: "";
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 1px solid #686d75;
  border-radius: 2px;
  margin-right: 8px;
  cursor: pointer;
  vertical-align: middle;
  position: relative;
  bottom: 2px;
}

input[type="checkbox"]:hover:before {
  border: 2px solid #008741;
}
input[type="checkbox"]:checked:before {
  background: @green url("../../assets/images/checkmark.svg") 50% 50% / contain no-repeat;
  border: 1px solid #2ca055;
  width: 16px;
  height: 16px;
  margin-right: 8px;
  cursor: pointer;
}

.dropdown-container {
  display: grid;
  grid-auto-flow: row;

  position: relative;
  max-height: 50px;

  &__label {
    display: block;
    width: 100%;
    height: 24px;
    font-weight: 600;
  }

  &__selector {
    position: absolute;
    width: 14px;
    height: 48px;
    right: 12px;
    background: url("../../assets/images/dropdown-arrow-grey.svg") 50% 55% / contain no-repeat;
    &.active {
      background: url("../../assets/images/dropdown-arrow-green.svg") 50% 55% / contain no-repeat;
    }
    &:hover {
      background: url("../../assets/images/dropdown-arrow-green.svg") 50% 55% / contain no-repeat;
    }
  }

  &__select {
    position: relative;
    display: grid;
    grid-auto-flow: column;
    border-radius: 6px;
    background-color: @light-grey;
    max-height: 48px;
    cursor: pointer;

    &.active {
      background-color: @light-grey;
    }
    span {
      text-overflow: ellipsis;
      font-family: "nunito";
      font-size: 16px;
      border: none;
      outline: none;
      padding: 12px;
      caret-color: transparent;
      color: @dark-grey;
      max-width: 90%;
      max-height: 48px;
      height: 48px;
      display: inline-block;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;

      &.bold {
        font-weight: bolder;
      }
    }
  }

  &__dropdown {
    display: grid;
    grid-auto-flow: column;
    grid-template-rows: repeat(6, auto);
    grid-template-columns: auto auto;
    column-gap: 10px;
    z-index: 10;
    position: absolute;
    top: 75px;
    background-color: white;
    list-style: none;
    border-radius: 20px;
    box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
    padding: 20px;
    width: max-content;
    min-width: 100%;
    :first-child:not(:empty) {
      margin: 0;
      min-width: 80px;
    }
    cursor: pointer;
    label {
      display: inline-block;
      color: @black;
      font-weight: 400;
      cursor: pointer;
      vertical-align: text-bottom;
    }
    @media @mobile {
      width: 100%;
      grid-auto-flow: row;
      grid-template-columns: 1fr;
    }
  }
}
</style>
