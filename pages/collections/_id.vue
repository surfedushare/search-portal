
<template>
  <section class="container main collection">
    <Collection :collection="my_collection"/>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Collection from '~/components/Collections/Collection';

export default {
  components: {
    Collection
  },
  computed: {
    ...mapGetters(['my_collection'])
  },
  mounted() {
    this.$store.dispatch('getMyCollection', this.$route.params.id);
  }
};
</script>
