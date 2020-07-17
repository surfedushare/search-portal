<template>
  <div :class="{ 'with-errors': errors.length > 0 }">
    <slot></slot>
    <ul v-if="errors.length > 0" class="errors">
      <li v-for="(error, ix) in errors" :key="ix">
        {{ error }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'ErrorWrapper',
  props: {
    errors: {
      type: Array,
      default: () => []
    }
  }
}
</script>
<style lang="less" scoped>
@import './../variables';

.with-errors {
  /deep/ input {
    border-color: @red;
  }
}

.errors {
  color: @red;
  font-size: 14px;
  list-style-type: none;
  padding: 0;
  padding-top: 5px;
  margin: 0;
  display: block;
}
</style>
