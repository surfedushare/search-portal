<template>
  <section class="container main">
    <Collections/>
  </section>
</template>

<script>
import Collections from '~/components/Collections';

export default {
  components: {
    Collections
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'material_communities', 'themes'])
  },
  mounted() {
    this.$store.dispatch('getMaterialCommunities', {
      params: {
        material_id: this.material.external_id
      }
    });
  }
};
</script>
