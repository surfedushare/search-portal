<template>
  <div class="container">
    <input v-bind="$attrs" @input="onChange" />
    <div class="counter">
      {{ $attrs['maxlength'] - $attrs['value'].length }}
    </div>
  </div>
</template>
<script>
export default {
  name: 'InputWithCounter',
  inheritAttrs: false,
  methods: {
    onChange(event) {
      this.$emit('input', event.target.value)
    }
  }
}
</script>
<style lang="less" scoped>
@import './../variables';

.container {
  position: relative;
}

.counter {
  position: absolute;
  right: 10px;
  top: 0;
  height: 100%;
  display: flex;
  align-items: center;
  color: darken(@light-grey, 20%);
}

input {
  font-family: @main-font;
  border: 1px solid #e5e5e5;
  width: 100%;
  border-radius: 7px;
  padding: 10px 40px 10px 10px;
  font-size: 16px;
  line-height: 1.44;
  color: #686d75;
  &:focus {
    outline: none;
  }
}
</style>
