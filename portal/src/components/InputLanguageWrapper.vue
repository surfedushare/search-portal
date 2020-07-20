<template>
  <div class="container">
    <slot class="input"></slot>
    <div v-if="language" class="language">{{ language }}</div>
  </div>
</template>
<script>
export default {
  name: 'InputLanguageWrapper',
  props: {
    language: {
      type: String,
      default: ''
    }
  }
}
</script>
<style lang="less" scoped>
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
  top: calc(50% - 15px);
  left: 15px;
}

/deep/ input {
  padding-left: 60px;
}
</style>
