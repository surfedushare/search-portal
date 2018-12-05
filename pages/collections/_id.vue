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
    // ...mapGetters(['collection'])
  },
  mounted() {
    // this.$store.dispatch('getMaterialCommunities', {
    //   params: {
    //     material_id: this.material.external_id
    //   }
    // });
  }
};
</script>
