
<template>
  <section class="container main collection">
    <div class="center_block">
      <Collection
        :collection="my_collection"
        :contenteditable="contenteditable"
        :submitting="submitting"
        :set-editable="setEditable"
        :change-view-type="changeViewType"
        :items-in-line="materials_in_line"
        v-model="search"
        @onSubmit="onSubmit"
      />

      <div
        v-infinite-scroll="loadMore"
        infinite-scroll-disabled="my_collection_materials_loading"
        infinite-scroll-distance="10"
      >
        <Materials
          v-model="formData.materials_for_deleting"
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
      submitting: false,
      materials_in_line: 4,
      formData: {
        materials_for_deleting: []
      },
      search: {
        page_size: 10,
        page: 1,
        filters: [],
        search_text: []
      }
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
  watch: {
    search(search) {
      if (search) {
        const { id } = this.$route.params;

        this.$store.dispatch('searchMaterialInMyCollection', {
          id,
          params: {
            ...search,
            page_size: 10,
            page: 1
          }
        });
      }
    }
  },
  mounted() {
    const { id } = this.$route.params;
    this.$store.dispatch('getMaterialInMyCollection', {
      id,
      params: {
        page_size: this.search.page_size,
        page: 1
      }
    });
    this.$store.dispatch('getMyCollection', id).catch(err => {
      if (err.response.status === 404) {
        this.$router.push('/');
      }
    });
  },
  methods: {
    /**
     * Load next collections
     */
    loadMore() {
      const { my_collection_materials, search } = this;
      const { id } = this.$route.params;
      if (my_collection_materials) {
        const { page_size, page, records_total } = my_collection_materials;

        if (records_total > page_size * page) {
          this.$store.dispatch(
            'getNextPeMaterialInMyCollection',
            Object.assign(
              {},
              { id, params: { ...search, page: page + 1, page_size } }
            )
          );
        }
      }
    },
    setEditable(isEditable) {
      this.contenteditable = isEditable;

      if (!isEditable) {
        this.formData.materials_for_deleting = [];
      }
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
    },

    onSubmit(data) {
      this.submitting = true;
      this.$store.dispatch('putMyCollection', {
        ...this.my_collection,
        ...data
      });
      console.log(11111, data, this.formData);
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
