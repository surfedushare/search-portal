
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
    <DeleteCollection
      :close="closeDeleteMaterials"
      :is-show="isShowDeleteMaterials"
      :deletefunction="deleteMaterials"
    />
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Materials from '~/components/Materials';
import Spinner from '~/components/Spinner';
import Collection from '~/components/Collections/Collection';
import DeleteCollection from '~/components/Popup/DeleteCollection';

export default {
  components: {
    Collection,
    Materials,
    Spinner,
    DeleteCollection
  },
  data() {
    return {
      contenteditable: false,
      isShowDeleteMaterials: false,
      submitting: false,
      submitData: false,
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
    /**
     * Set editable to the collection
     * @param isEditable - Boolean
     */
    setEditable(isEditable) {
      this.contenteditable = isEditable;

      if (!isEditable) {
        this.formData.materials_for_deleting = [];
      }
    },
    /**
     * Deleting collection by id
     * @param id - String
     */
    deleteMaterialsPopup() {
      this.isShowDeleteMaterials = true;
    },
    closeDeleteMaterials() {
      this.isShowDeleteMaterials = false;
      this.submitting = false;
      this.setEditable(false);
    },
    deleteMaterials() {
      const { my_collection } = this;
      const { materials_for_deleting } = this.formData;
      this.$store
        .dispatch('removeMaterialFromMyCollection', {
          collection_id: my_collection.id,
          data: materials_for_deleting.map(material => {
            return {
              external_id: material
            };
          })
        })
        .then(() => {
          this.$nextTick().then(() => {
            this.$store.dispatch('putMyCollection', {
              ...this.my_collection,
              ...this.submitData
            });
            this.$store
              .dispatch('getMaterialInMyCollection', {
                id: my_collection.id,
                params: {
                  page_size: this.search.page_size,
                  page: 1
                }
              })
              .then(() => {
                this.closeDeleteMaterials();
                this.submitting = false;
                this.setEditable(false);
              });
          });
        });
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
    /**
     * Save collection
     * @param data - Object
     */
    onSubmit(data) {
      const { materials_for_deleting } = this.formData;
      this.submitting = true;
      this.submitData = data;
      if (materials_for_deleting && materials_for_deleting.length) {
        this.deleteMaterialsPopup();
      } else {
        this.$store
          .dispatch('putMyCollection', {
            ...this.my_collection,
            ...data
          })
          .then(() => {
            if (!materials_for_deleting || !materials_for_deleting.length) {
              this.submitting = false;
              this.setEditable(false);
            }
          });
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
