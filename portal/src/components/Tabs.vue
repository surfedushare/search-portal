<template>
  <div class="tabs">
    <div class="buttons">
      <button
        v-for="(tab, index) in tabs"
        :key="tab.title"
        :class="{ active: selectedIndex === index, [tab.identifier]: true }"
        class="tab"
        @click="selectTab(index)"
      >
        {{ tab.title }}
      </button>
    </div>
    <slot name="after-tabs" :active-tab="activeTab"></slot>
    <slot></slot>
  </div>
</template>
<script>
export default {
  name: 'Tabs',
  props: {
    activeIndex: {
      type: Number,
      default: 0
    },
    setTab: {
      type: Function,
      params: 1,
      default: () => {}
    }
  },
  data() {
    return {
      selectedIndex: 0,
      tabs: []
    }
  },
  computed: {
    activeTab() {
      const tab = this.tabs.find(tab => tab.isActive)
      return tab && tab.identifier
    }
  },
  mounted() {
    this.tabs = this.$children.filter(c => {
      return c.$slots.default
    })
    this.selectTab(this.activeIndex)
  },
  methods: {
    selectTab(index) {
      this.selectedIndex = index
      this.setTab(index)
      this.tabs.forEach((tab, i) => (tab.isActive = index === i))
    }
  }
}
</script>
<style lang="less" scoped>
@import url('../variables');
@active-tab-indicator-size: 15px;

/* Style the tab */
.tabs {
  overflow: hidden;
  padding: @active-tab-indicator-size;
}

.buttons {
  display: inline-block;

  @media @mobile {
    display: flex;
    flex-direction: column;
  }
}

.tabs button.tab {
  position: relative;
  display: inline-block;
  border-radius: 5px;
  background-color: inherit;
  border: 1px solid #ccc;
  outline: none;
  cursor: pointer;
  padding: 14px 50px;
  margin-right: 25px;
  transition: 0.3s;
  font-size: 16px;
  font-weight: bold;

  @media @mobile {
    margin-bottom: 20px;
  }
}

.tabs button:hover {
  background-color: cornflowerblue;
}

.tabs button.active {
  background-color: @dark-blue;
  color: white;
}
.tabs button.active:after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -1 * @active-tab-indicator-size;
  width: 0;
  height: 0;
  border-top: solid @active-tab-indicator-size @dark-blue;
  border-left: solid @active-tab-indicator-size transparent;
  border-right: solid @active-tab-indicator-size transparent;

  @media @mobile {
    display: none;
  }
}
</style>
