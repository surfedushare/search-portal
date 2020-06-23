<template>
  <div id="app">
    <div class="main_block ">
      <MainHeader />

      <router-view />

      <MainFooter />
    </div>

    <nuxt-loading ref="loading" />
  </div>
</template>

<style lang="less">
@import 'styles/normalize.css';

@import 'variables.less';

@import 'styles/common.less';

@import 'styles/forms.less';
</style>

<script>
import MainHeader from '~/components/MainHeader'
import MainFooter from '~/components/MainFooter'
import NuxtLoading from '~/components/nuxt-loading.vue'
import axios from '~/axios'

export default {
  components: {
    MainHeader,
    MainFooter,
    NuxtLoading
  },
  watch: {
    '$i18n.locale'(newLocale) {
      axios.setLanguage(newLocale)
    }
  },
  created() {
    if (typeof window !== 'undefined') {
      window.app = this
    }
    this.$store.dispatch('getFilterCategories')
  },

  mounted() {
    this.$loading = this.$refs.loading
    this.$store.dispatch('getThemes')
  }
}
</script>
