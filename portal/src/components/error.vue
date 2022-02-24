<template>
  <section class="edusources-container container-pd text-center">
    <h1 class="title">
      {{ statusCode }}
    </h1>
    <h2 class="info">
      {{ $t(messageKey) }}
    </h2>
    <router-link v-if="parseInt(statusCode) === 404" class="button" to="/">
      {{ $t('Main-page') }}
    </router-link>
  </section>
</template>

<script>
export default {
  name: 'Error',
  props: {
    statusCode: {
      type: String,
      default: '',
    },
    messageKey: {
      type: String,
      default: '',
    },
  },
}
</script>

<style scoped>
.edusources-container {
  flex: 1 1 auto;
  box-sizing: border-box;
  background: transparent;
  padding: 80px 0;
}
.title {
  margin-top: 15px;
  font-size: 5em;
}

.info {
  font-weight: 300;
  color: #9aabb1;
  margin: 20px 0;
}
</style>
