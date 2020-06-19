<template>
  <div v-if="material" class="material__info_mobile">
    <h1 class="material__info_mobile_ttl">
      {{ material.title }}
    </h1>
    <div v-if="material" class="material__info_mobile_author">
      <router-link v-if="material.author" :to="authorUrl">
        {{ material.author }}
      </router-link>
      <div>{{ material.publisher }}</div>
    </div>
  </div>
</template>

<script>
import { generateSearchMaterialsQuery } from './../../_helpers'
export default {
  name: 'MaterialTitleMobile',
  props: {
    material: {
      type: Object,
      default: null
    }
  },
  computed: {
    /**
     * Get author URL
     * @returns {{path, query}}
     */
    authorUrl() {
      let formData = {
        page_size: 10,
        page: 1,
        filters: [],
        search_text: []
      }
      if (this.material) {
        formData.author = this.material.author
        return this.generateSearchMaterialsQuery(this.formData)
      }
      return ''
    }
  },
  methods: {
    generateSearchMaterialsQuery
  }
}
</script>

<style lang="less" scoped>
@import './../../../variables';
.material__info_mobile {
  padding: 0 25px;
  font-size: 16px;
  @media @desktop {
    display: none;
  }
  &_ttl {
    margin: 0;
    font-size: 22px;
  }
  &_author a {
    font-weight: bold;
  }
}
</style>
