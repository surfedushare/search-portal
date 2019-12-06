<template>
  <section class="container main">
    <Communities :user-communities="userCommunities"/>
  </section>
</template>

<script>
import Communities from '~/components/Communities';

export default {
  data() {
    return {
      userCommunities: this.$route.name.startsWith('my')
    }
  },
  components: {
    Communities
  }
};
</script>
