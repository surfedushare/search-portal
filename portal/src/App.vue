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
  dependencies: ['$window', '$log'],
  components: {
    MainHeader,
    MainFooter
  },
  watch: {
    '$i18n.locale'(newLocale) {
      setLanguage(newLocale)
    }
  },
  mounted() {
    this.$log.pageView(this.$route.path)
    this.$store.dispatch('getThemes')
    this.$router.beforeEach((to, from, next) => {
      this.$log.pageView(to.path)
      next()
    })
  },
  methods: {
    isDemoEnvironment() {
      return (
        this.$window.location.hostname.indexOf('acc.') >= 0 ||
        new URLSearchParams(this.$window.location.search).get('demo')
      )
    }
  }
}
</script>
