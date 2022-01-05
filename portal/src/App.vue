<template>
  <div id="app">
    <div class="main_block">
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

const DEFAULT_TITLE = 'Edusources'

export default {
  dependencies: ['$window', '$log'],
  components: {
    MainHeader,
    MainFooter,
  },
  watch: {
    '$i18n.locale'(newLocale) {
      setLanguage(newLocale)
    },
  },
  created() {
    this.$store.dispatch('getFilterCategories')
  },
  methods: {
    isDemoEnvironment() {
      return (
        this.$window.location.hostname.indexOf('acc.') >= 0 ||
        new URLSearchParams(this.$window.location.search).get('demo')
      )
    },
  },
  metaInfo: {
    title: DEFAULT_TITLE,
    titleTemplate: (titleChunk) => {
      return titleChunk && titleChunk !== DEFAULT_TITLE
        ? `${titleChunk} | ${DEFAULT_TITLE}`
        : DEFAULT_TITLE
    },
  },
}
</script>
