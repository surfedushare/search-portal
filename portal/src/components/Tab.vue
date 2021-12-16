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
      default: '',
    },
    identifier: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      isActive: true,
    }
  },
}
</script>
<style lang="less" scoped>
@import url('../variables');

.tabcontent {
  margin-top: 50px;

  @media @mobile {
    margin-top: 20px;
  }
}
</style>
