<template>
  <div id="app">
    <div class="main_block ">
      <MainHeader />
      <nuxt/>
      <MainFooter />
    </div>
    <nuxt-loading ref="loading"></nuxt-loading>
  </div>
</template>

<style lang="less">
  @import 'styles/normalize.css';

  @import 'variables.less';

  @import 'styles/common.less';

  @import 'styles/forms.less';
</style>

<script>

import Vue from 'vue'

import MainHeader from '~/components/MainHeader';
import MainFooter from '~/components/MainFooter';
import NuxtLoading from '~/components/nuxt-loading.vue'


export default {
  components: {
    MainHeader,
    MainFooter,
    NuxtLoading
  },
  data: () => ({
    layout: null,
    layoutName: ''
  }),
  beforeCreate () {
    Vue.util.defineReactive(this, 'nuxt', this.$options.nuxt);
  },
  created () {
    // Add this.$nuxt in child instances
    Vue.prototype.$nuxt = this;
    // add to window so we can listen when ready
    if (typeof window !== 'undefined') {
      window.$nuxt = this
    }
    this.$store.dispatch('getFilterCategories');
  },

  mounted () {
    this.$loading = this.$refs.loading;
    this.$store.dispatch('getThemes');
  },
  watch: {
    '$i18n.locale'(newLocale) {
      this.$axios.setLanguage(newLocale);
    }
  },
  methods: {
    setLayout() {  // previously received a layout
      return 'default';
    }
  }
}
</script>
