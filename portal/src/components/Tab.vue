<template>
  <div v-show="isActive" class="tabcontent">
    <slot></slot>
  </div>
</template>
<script>
export default {
  name: 'Tab',
  props: {
    title: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      isActive: true
    }
  }
}
</script>
<style lang="less" scoped>
.tabcontent {
  padding: 6px 12px;
  border-top: none;
}
</style>
