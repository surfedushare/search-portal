<template>
  <section class="container main collection">
    <Collection/>
  </section>
</template>

<script>
import Collection from '~/components/Collections/Collection';

export default {
  components: {
    Collection
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'material_communities', 'themes'])
  },
  mounted() {}
};
</script>
