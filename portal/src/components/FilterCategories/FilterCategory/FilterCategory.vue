<template>
  <li class="filter-categories__item" if="visible">
    <div>
      <h4
        class="filter-categories__item_title"
        :class="{ 'filter-categories__item_title--hide': isOpen }"
        @click="toggle()"
      >
        {{ titleTranslation(category) }}
      </h4>
      <ul v-show="isOpen" class="filter-categories__subitems">
        <li
          v-for="item in visibleChildren"
          :key="item.external_id"
          class="filter-categories__subitem"
        >
          <div class="filter-checkbox">
            <input
              :id="item.external_id"
              v-model="item.selected"
              type="checkbox"
              :value="item.external_id"
              :data-category-id="category.external_id"
              :data-item-id="item.external_id"
              @change="onChange"
            >

            <label :for="item.external_id">
              {{ titleTranslation(item) }}
              ({{ item.count }})
            </label>
          </div>
        </li>

        <li
          v-if="category.children.length > numberOfVisibleItems"
          class="filter-categories__subitem--show-more"
        >
          <a
            v-if="showAll"
            href="/show-more/"
            @click.prevent="onToggleShowAll()"
          >
            {{ $t('Hide') }}
          </a>

          <a v-else href="/show-more/" @click.prevent="onToggleShowAll()">
            {{ $t('View-more') }}
          </a>
        </li>
      </ul>
    </div>
    <FilterCategoriesPopup
      :category="category"
      :show-popup="showPopup"
      :close="onToggleShowAll"
      @apply="onApply"
    />
  </li>
</template>

<script>
import FilterCategoriesPopup from '~/components/FilterCategories/FilterCategoriesPopup'
export default {
  name: 'FilterCategory',
  components: {FilterCategoriesPopup},
  props: {
    category: {
      type: Object,
      default: () => ({
        children: [],
      }),
    },
    change: {
      type: Function,
      default: () => {},
    },
  },
  data() {
    const isOpen = this.category.children.some((child) => child.selected)

    return {
      isOpen,
      showAll: false,
      showPopup: false,
      visibleItems: 5,
    }
  },
  computed: {
    visible() {
      return this.category.children.some((child) => !child.is_hidden)
    },
    sortedChildren() {
      return [...this.category.children].sort((a, b) => {
        return b.selected - a.selected || b.count - a.count
      })
    },
    numberOfVisibleItems() {
      // Display all selected items or max visibleItems
      return Math.max(
        this.category.children.filter((c) => c.selected).length,
        this.visibleItems
      )
    },
    visibleChildren() {
      if (this.showAll) {
        return this.sortedChildren
      }

      return this.sortedChildren.slice(0, this.numberOfVisibleItems)
    },
  },
  watch: {
    category(newCategory) {
      this.isOpen = newCategory.children.some((child) => child.selected)
    },
  },
  methods: {
    toggle() {
      this.isOpen = !this.isOpen
    },
    onToggleShowAll() {
      if (this.$root.isDemoEnvironment() && this.category.children.length >= 15) {
        this.showPopup = !this.showPopup
        return
      }
      this.showAll = !this.showAll
    },
    onChange(e) {
      const { categoryId, itemId } = e.target.dataset
      if (e.target.checked) {
        this.$emit('check', categoryId, itemId)
      } else {
        this.$emit('uncheck', categoryId, itemId)
      }
    },
    onApply(values) {
      values = values || []
      this.category.children.forEach((child) => {
        if (values.indexOf(child.value) >= 0) {
          this.$emit('check', this.category.external_id, child.value)
        } else {
          this.$emit('uncheck', this.category.external_id, child.value)
        }
      })
    }
  },
}
</script>
