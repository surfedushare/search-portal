<template>
  <section
    v-show="showError"
    class="container container-pd text-center"
  >
    <h1
      :class="{'chunkfailed-title' : isChunkLoadingFailed}"
      class="title"
    >
      {{ isChunkLoadingFailed ? '' : error.statusCode }}
    </h1>
    <h2
      :class="{'chunkfailed-info' : isChunkLoadingFailed}"
      class="info"
    >
      {{ isChunkLoadingFailed ? '' : error.message }}
    </h2>
    <nuxt-link
      v-if="error.statusCode === 404"
      class="button"
      to="/"
    >
      Main page
    </nuxt-link>
  </section>
</template>

<script>
/*eslint-disable */
export default {
  props: ['error'],
  data() {
    return {
      showError: false,
      isChunkLoadingFailed: false
    };
  },
  mounted() {
    if (this.error == null) {
      return;
    }
    if (this.error.statusCode === 404) {
      // 404
      const mt = /^\/page\/(\d+)$/g.exec(this.$route.path);
      if (mt && mt.length === 2) {
        const query = this.$route.query || {};
        location.replace(
          `/page.shtml?id=${mt[1]}${
            Object.keys(query).length > 0 ? '&' : ''
          }${utils.serialize(query)}`
        );
        return;
      }
    }
    // webpack error
    if (
      this.error.statusCode === 500 &&
      /^Loading chunk (\d)+ failed\./.test(this.error.message)
    ) {
      this.isChunkLoadingFailed = true;
      location.replace(location.href);
    }
    this.showError = true;
  }
};
</script>


<style scoped>
.container {
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

.chunkfailed-title {
  font-size: 2.5em;
}

.chunkfailed-info {
  font-size: 20px;
}
</style>
