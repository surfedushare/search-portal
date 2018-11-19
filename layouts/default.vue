<template>
  <div class="main_block">
    <MainHeader />
    <nuxt/>
    <MainFooter />
  </div>
</template>

<script>
import MainHeader from './../components/MainHeader'
import MainFooter from './../components/MainFooter'

export default {
  components: {
    MainHeader,
    MainFooter
  },
  mounted() {}
}
</script>
