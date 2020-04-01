
<template>
  <section class="container main collection">
    <div v-if="!collectionInfo && !isLoading">
      <error status-code="404" message-key="collection-not-found"></error>
    </div>
    <div class="center_block" v-else>
      <Collection
        :collection="collectionInfo"
        :contenteditable="contenteditable"
        :submitting="submitting"
        :set-editable="setEditable"
        :change-view-type="changeViewType"
        :items-in-line="materials_in_line"
        v-model="search"
        @onSubmit="onSubmit"
      />

      <div>
        <Materials
          v-model="formData.materials_for_deleting"
          :materials="collection_materials"
          :items-in-line="materials_in_line"
          :loading="collection_materials_loading"
          :contenteditable="contenteditable"
          class="collection__materials"
        />
        <Spinner v-if="collection_materials_loading" />
      </div>
    </div>
    <DeleteCollection
      :close="closeDeleteCollection"
      :is-show="isShowDeleteCollection"
      :deletefunction="deleteMaterials"
    />
    <DeleteMaterial
      :close="closeDeleteMaterials"
      :is-show="isShowDeleteMaterials"
      :deletefunction="deleteMaterials"
    />
  </section>
</template>

<script>
import _ from 'lodash';
import { mapGetters } from 'vuex';
import Materials from '~/components/Materials';
import Spinner from '~/components/Spinner';
import Collection from '~/components/Collections/Collection';
import DeleteCollection from '~/components/Popup/DeleteCollection';
import DeleteMaterial from '~/components/Popup/DeleteMaterial';
import Error from '~/components/error'
import { PublishStatus } from '~/utils'


export default {
  components: {
    Collection,
    Materials,
    Spinner,
    DeleteCollection,
    DeleteMaterial,
    Error
  },
  data() {
    return {
      contenteditable: this.$route.meta.editable,
      isShowDeleteCollection: false,
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
      },
      isLoading: true
    };
  },
  computed: {
    ...mapGetters([
      'collection',
      'collection_materials',
      'materials_loading',
      'collection_materials_loading',
      'user'
    ]),
    collectionInfo() {
      if (_.isEmpty(this.collection)) {
        return this.collection;
      } else if (this.collection.publish_status === PublishStatus.PUBLISHED) {
        return this.collection;
      } else if(this.user && _.find(this.user.collections, {id: this.collection.id})) {
        return this.collection;
      }
      return {}
    },
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
    this.$store.dispatch('getCollection', id).finally(() => {
      this.isLoading = false;
    });
  },
  methods: {
    /**
     * Set editable to the collection
     * @param isEditable - Boolean
     */
    setEditable(isEditable) {
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
    deleteCollectionPopup() {
      this.isShowDeleteCollection = true;
    },
    closeDeleteCollection() {
      this.isShowDeleteCollection = false;
      this.submitting = false;
      this.setEditable(false);
    },
    deleteMaterials() {
      const { collection } = this;
      const { materials_for_deleting } = this.formData;
      this.$store
        .dispatch('removeMaterialFromMyCollection', {
          collection_id: collection.id,
          data: materials_for_deleting.map(material => {
            return {
              external_id: material
            };
          })
        })
        .then(() => {
          this.$nextTick().then(() => {
            this.$store.dispatch('putMyCollection', {
              ...this.collection,
              ...this.submitData
            });
            this.$store
              .dispatch('getMaterialInMyCollection', {
                id: collection.id,
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
            ...this.collection,
            ...data
          })
          .catch(() => {
            if(this.collection.publish_status === PublishStatus.PUBLISHED && !this.collection.materials_count) {
              this.collection.publish_status = PublishStatus.DRAFT;
            }
          })
          .finally(() => {
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
