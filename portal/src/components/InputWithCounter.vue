<template>
  <div class="container">
    <div v-if="language" class="language">{{ language }}</div>
    <input
      v-bind="$attrs"
      :class="{ 'with-language': language !== null }"
      @input="onChange"
      @focus="showCounter = true"
      @blur="showCounter = false"
    />
    <div v-if="showCounter" class="counter">
      {{ charactersRemaining }}
    </div>
  </div>
</template>
<script>
export default {
  name: 'InputWithCounter',
  inheritAttrs: false,
  props: {
    language: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      showCounter: false
    }
  },
  computed: {
    charactersRemaining() {
      if (this.$attrs.value) {
        return this.$attrs.maxlength - this.$attrs.value.length
      }

      return this.$attrs.maxlength
    }
  },
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

.language {
  background-color: #ccc;
  color: white;
  border-radius: 50%;
  padding: 7px;
  font-size: 16px;
  line-height: 16px;
  font-weight: 600;
  position: absolute;
  top: 8px;
  left: 15px;
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

  &.with-language {
    padding-left: 60px;
  }
}
</style>
