<template>
  <section class="container main collection">
    <div class="center_block">
      <Collection
        :collection="collection"
        :user="user"
      />
      <Materials
        :materials="collection_materials"
        :items-in-line="4"
        class="collection__materials"
      />
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
    ...mapGetters([
      'collection',
      'collection_materials',
      'user',
      'isAuthenticated',
      'user_loading'
    ])
  },
  mounted() {
    if (this.isAuthenticated) {
      this.$store.dispatch('getMaterialInMyCollection', this.$route.params.id);
      this.$store.dispatch('getCollection', this.$route.params.id);
    } else if (!this.user_loading) {
      this.$router.push('/');
    }
  }
};
</script>

<style lang="less">
  .collection {
    width: 100%;
    padding: 95px 0 215px;
  }
</style>
