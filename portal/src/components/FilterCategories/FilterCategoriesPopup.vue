<template>
  <transition name="fade">
    <Popup
      v-if="showPopup"
      :close="close"
      :is-show="showPopup"
      class="popup-content"
    >
      <slot>
        <h2 class="popup__title">
          {{ category.translation[$i18n.locale] }}
        </h2>
        <v-autocomplete
          v-model="selectedValues"
          @change="onChangeAutocomplete"
          :items="category.children"
          :item-text="'translation.' + $i18n.locale"
          outlined multiple deletable-chips small-chips clearable
        ></v-autocomplete>
        <div class="popup__subtext">
          <ul v-for="(filters, group) in groupedFilters">
            <div class="list-header">{{ group.toUpperCase() }}</div>
            <li
              v-for="item in filters"
              :key="item.external_id"
              class="filter-categories__subitem"
            >
              <div class="filter-checkbox">
                <input
                  :id="item.external_id"
                  v-model="item.selected"
                  type="checkbox"
                  :value="item.external_id"
                  :data-item-id="item.external_id"
                  @change="onChange"
                >
                <label :for="item.external_id">
                  {{ item.translation[$i18n.locale] }}
                  ({{ item.count }})
                </label>
              </div>
            </li>
          </ul>
        </div>
        <div>
          <div class="popup-content__actions">
            <button class="button" @click="onApply">
              {{ $t('See-results') }}
            </button>
          </div>
        </div>
      </slot>
    </Popup>
  </transition>
</template>

<script>
import { sortBy, groupBy, without, concat } from 'lodash'
import Popup from '~/components/Popup'

export default {
  name: 'FilterCategoriesPopup',
  components: {
    Popup,
  },
  props: {
    category: {
      type: Object,
      default: () => ({
        children: [],
      }),
    },
    showPopup: {
      type: Boolean,
      default: false,
    },
    close: {
      type: Function,
      default: () => {},
    },
  },
  data() {
    return {
      selectedValues: []
    }
  },
  watch: {
    showPopup(visible) {
      if (!visible) {
        return
      }
      this.selectedValues = this.category.children.filter((childFilter) => {
        return childFilter.selected
      }).map((selectedFilter) => {
        return selectedFilter.value
      })
    }
  },
  computed: {
    groupedFilters() {
      return groupBy(
        sortBy(this.category.children, ['value']),
        (child) => { return child.value.slice(0, 1).toLowerCase() }
      )
    }
  },
  methods: {
    onChangeAutocomplete(values) {
      this.category.children.forEach((childFilter) => {
        childFilter.selected = values.indexOf(childFilter.value) >= 0
      })
    },
    onChange(event) {
      const { itemId } = event.target.dataset
      if (event.target.checked) {
        this.selectedValues = concat(this.selectedValues, [itemId])
      } else {
        this.selectedValues = without(this.selectedValues, itemId)
      }
    },
    onApply() {
      this.$emit('apply', this.selectedValues)
      this.close()
    }
  }
}
</script>

<style lang="less">
  .popup__subtext {
    overflow-y: scroll;
  }
</style>
