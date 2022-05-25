<template>
  <li class="filter-categories__item" if="visible">
    <div>
      <h4
        class="filter-categories__item_title"
        :class="{ 'filter-categories__item_title--hide': isOpen }"
        @click="toggle()"
      >{{ titleTranslation(category) }}</h4>
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
          <a v-if="showAll" href="/show-more/" @click.prevent="onToggleShowAll()">{{ $t('Hide') }}</a>

          <a v-else href="/show-more/" @click.prevent="onToggleShowAll()">{{ $t('View-more') }}</a>
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
  components: { FilterCategoriesPopup },
  props: {
    category: {
      type: Object,
      default: () => ({
        children: [],
      }),
    },
    change: {
      type: Function,
      default: () => { },
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
      if (this.category.children.length > 0) {
            this.isOpen = !this.isOpen
      }
    },
    onToggleShowAll() {
      if (this.category.children.length >= 20) {
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

<style lang="less" scoped>
@import "../../variables.less";
.filter-categories {
  &__item_title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    word-break: break-word;

    &:after {
      content: "";
      display: inline-block;
      width: 20px;
      height: 20px;
      flex-shrink: 0;
      margin: 2px 5px 0 20px;
      background: url("../../assets/images/plus-black.svg") 50% 50% / contain no-repeat;
    }

    &--hide:after {
      background: url("../../assets/images/min-black.svg") 50% 50% / contain no-repeat;
    }
  }

  &__item {
    padding: 0 0 2px;
    margin: 0 0 19px;
    list-style: none;
    border-bottom: 1px solid @light-grey;
  }

  &__subitems {
    padding: 16px 0 !important;
    margin: 0;
    list-style: none;
  }

  &__subitem {
    padding: 6px 0;
    margin: 0;
    list-style: none;
    display: block;
    width: 100%;

    &_icon {
      &.cc-by {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/sa-black.svg") no-repeat 23px 0;
        background-size: contain;
      }
      &.cc-by-nc,
      &.cc-by-nc-sa {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/nc-black.svg") no-repeat 23px 0,
          url("../../assets/images/sa-black.svg") no-repeat 46px 0;
        background-size: contain;
      }
      &.cc-by-nd {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/nd-black.svg") no-repeat 23px 0;
        background-size: contain;
      }
      &.cc-by-sa {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/nc-black.svg") no-repeat 23px 0;
        background-size: contain;
      }
      &.cc-by-nc-nd {
        background: url("../../assets/images/by-black.svg") no-repeat 0 0,
          url("../../assets/images/nc-black.svg") no-repeat 23px 0,
          url("../../assets/images/nd-black.svg") no-repeat 46px 0;
        background-size: contain;
      }

      height: 20px;
      margin: 6px 0 3px;
      width: 100%;
      display: block;
      background-size: contain;

      @media @tablet, @mobile {
        margin-bottom: 25px;
      }

      &--inline {
        display: inline-block;
        width: 70px;
        vertical-align: bottom;
        margin: 0;
      }
    }

    input {
      margin: 5px 10px 0;
    }

    label {
      cursor: pointer;
    }

    &--show-more {
      padding-top: 10px;
      padding-left: 10px;
      font-size: 14px;

      a {
        text-decoration: underline;

        &:hover {
          text-decoration: none;
        }
      }
    }
  }
}
</style>
