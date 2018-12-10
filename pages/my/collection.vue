
<template>
  <section class="container main collection">
    <div class="center_block">
      <Collection :collection="my_collection"/>
      <Materials
        :materials="my_collection_materials"
        :items-in-line="4"
        class="collection__materials"/>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Materials from '~/components/Materials';
import Collection from '~/components/Collections/Collection';

export default {
  components: {
    Collection,
    Materials
  },
  computed: {
    ...mapGetters(['my_collection', 'my_collection_materials'])
  },
  mounted() {
    this.$store.dispatch('getMaterialInMyCollection', this.$route.params.id);
    this.$store.dispatch('getMyCollection', this.$route.params.id);
  }
};
</script>
<style lang="less">
.collection {
  width: 100%;
  padding: 95px 0 215px;
}
</style>
