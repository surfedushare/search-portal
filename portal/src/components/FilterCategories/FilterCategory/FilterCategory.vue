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
            />

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
  </li>
</template>

<script>
export default {
  name: 'FilterCategory',
  props: {
    category: {
      type: Object,
      default: () => ({
        children: []
      })
    },
    change: {
      type: Function,
      default: () => {}
    }
  },
  data() {
    const isOpen = this.category.children.some(child => child.selected)

    return {
      isOpen,
      showAll: false,
      visibleItems: 3
    }
  },
  computed: {
    visible() {
      return this.category.children.some(child => !child.is_hidden)
    },
    sortedChildren() {
      return [...this.category.children].sort((a, b) => {
        return b.selected - a.selected || b.count - a.count
      })
    },
    numberOfVisibleItems() {
      // Display all selected items or max visibleItems
      return Math.max(
        this.category.children.filter(c => c.selected).length,
        this.visibleItems
      )
    },
    visibleChildren() {
      if (this.showAll) {
        return this.sortedChildren
      }

      return this.sortedChildren.slice(0, this.numberOfVisibleItems)
    }
  },
  methods: {
    toggle() {
      this.isOpen = !this.isOpen
    },
    onToggleShowAll() {
      this.showAll = !this.showAll
    },
    onChange(e) {
      const { categoryId, itemId } = e.target.dataset

      if (e.target.checked) {
        this.$emit('check', categoryId, itemId)
      } else {
        this.$emit('uncheck', categoryId, itemId)
      }
    }
  }
}
</script>
