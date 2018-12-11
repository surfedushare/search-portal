
<template>
  <section class="container main collection">
    <div class="center_block">
      <Collection :collection="my_collection"/>
      <div
        v-infinite-scroll="loadMore"
        infinite-scroll-disabled="my_collection_materials_loading"
        infinite-scroll-distance="10"
      >
        <Materials
          :materials="my_collection_materials"
          :items-in-line="4"
          :loading="my_collection_materials_loading"
          class="collection__materials"
        />
        <Spinner v-if="my_collection_materials_loading" />
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Materials from '~/components/Materials';
import Spinner from '~/components/Spinner';
import Collection from '~/components/Collections/Collection';

export default {
  components: {
    Collection,
    Materials,
    Spinner
  },
  computed: {
    ...mapGetters([
      'my_collection',
      'my_collection_materials',
      'materials_loading',
      'my_collection_materials_loading'
    ])
  },
  mounted() {
    const { id } = this.$route.params;
    this.$store.dispatch('getMaterialInMyCollection', {
      id,
      page_size: 10,
      page: 1
    });
    this.$store.dispatch('getMyCollection', id);
  },
  methods: {
    /**
     * Load next materials
     */
    loadMore() {
      const { my_collection_materials } = this;
      const { id } = this.$route.params;
      if (my_collection_materials) {
        const { page_size, page, records_total } = my_collection_materials;

        if (records_total > page_size * page) {
          this.$store.dispatch(
            'getNextPeMaterialInMyCollection',
            Object.assign({}, { id, page: page + 1, page_size })
          );
        }
      }
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
