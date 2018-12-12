
<template>
  <section class="container main collection">
    <div class="center_block">
      <Collection
        :collection="my_collection"
        :contenteditable="contenteditable"
        :set-editable="setEditable"
        :change-view-type="changeViewType"
        :items-in-line="materials_in_line"
      />
      <div
        v-infinite-scroll="loadMore"
        infinite-scroll-disabled="my_collection_materials_loading"
        infinite-scroll-distance="10"
      >
        <Materials
          :materials="my_collection_materials"
          :items-in-line="materials_in_line"
          :loading="my_collection_materials_loading"
          :contenteditable="contenteditable"
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
  data() {
    return {
      contenteditable: false,
      materials_in_line: 4
    };
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
     * Load next collections
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
    },
    setEditable(isEditable) {
      this.contenteditable = isEditable;
    },
    /**
     * Change 1 item in line to 4 and back.
     */
    changeViewType() {
      if (this.materials_in_line === 1) {
        this.materials_in_line = 4;
      } else {
        this.materials_in_line = 1;
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
