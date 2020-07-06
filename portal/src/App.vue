<template>
  <div id="app">
    <div class="main_block ">
      <MainHeader />

      <router-view />

      <MainFooter />
    </div>
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
import { setLanguage } from '~/axios'

export default {
  components: {
    MainHeader,
    MainFooter
  },
  watch: {
    '$i18n.locale'(newLocale) {
      setLanguage(newLocale)
    }
  },
  created() {
    if (typeof window !== 'undefined') {
      window.app = this
    }
    this.$store.dispatch('getFilterCategories')
  },

  mounted() {
    this.$store.dispatch('getThemes')
  }
}
</script>
