<template>
  <section class="container main collection">
    <div v-if="!collectionInfo && !isLoading">
      <error status-code="404" message-key="collection-not-found" />
    </div>
    <div v-else class="center_block">
      <Collection
        v-if="collectionInfo"
        v-model="search"
        :collection="collectionInfo"
        :contenteditable="contenteditable"
        :submitting="submitting"
        :set-editable="setEditable"
        :change-view-type="changeViewType"
        :items-in-line="materials_in_line"
        @onSubmit="onSubmit"
      />

      <div v-if="contenteditable" class="add-materials">
        <button
          class="materials__add__link button secondary"
          @click.prevent="showAddMaterial"
        >
          {{ $t('Add-materials') }}
        </button>
      </div>

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
    <AddMaterialPopup
      v-if="isShowAddMaterial"
      :close="closeAddMaterial"
      :is-show="isShowAddMaterial"
      :collection-id="collection.id"
      @submitted="saveMaterials"
    />
  </section>
</template>

<script>
import { isEmpty } from 'lodash'
import { mapGetters } from 'vuex'
import Materials from '~/components/Materials'
import Spinner from '~/components/Spinner'
import Collection from '~/components/Collections/Collection'
import AddMaterialPopup from '~/components/Collections/AddMaterialPopup'
import DeleteCollection from '~/components/Popup/DeleteCollection'
import DeleteMaterial from '~/components/Popup/DeleteMaterial'
import Error from '~/components/error'
import { PublishStatus } from '~/utils'

export default {
  components: {
    Collection,
    Materials,
    Spinner,
    DeleteCollection,
    DeleteMaterial,
    Error,
    AddMaterialPopup
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
        search_text: ''
      },
      isLoading: true,
      isShowAddMaterial: false
    }
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
      if (isEmpty(this.collection)) {
        return null
      } else if (this.collection.publish_status === PublishStatus.PUBLISHED) {
        return this.collection
      } else if (
        this.user &&
        this.user.collections.find(
          collection => collection.id === this.collection.id
        )
      ) {
        return this.collection
      }

      return null
    }
  },
  mounted() {
    const { id } = this.$route.params
    this.$store.dispatch('getMaterialInMyCollection', {
      id,
      params: {
        page_size: this.search.page_size,
        page: 1
      }
    })
    this.$store.dispatch('getCollection', id).finally(() => {
      this.isLoading = false
    })
  },
  methods: {
    showAddMaterial() {
      this.isShowAddMaterial = true
    },
    closeAddMaterial() {
      this.isShowAddMaterial = false
      this.materialsUpdateKey += 1
    },
    saveMaterials() {
      const { id } = this.$route.params
      this.isLoading = true
      this.$store
        .dispatch('getMaterialInMyCollection', { id, params: {} })
        .finally(() => {
          this.isLoading = false
        })
    },
    /**
     * Set editable to the collection
     * @param isEditable - Boolean
     */
    setEditable(isEditable) {
      if (!isEditable) {
        this.formData.materials_for_deleting = []
      }
    },
    /**
     * Deleting collection by id
     * @param id - String
     */
    deleteMaterialsPopup() {
      this.isShowDeleteMaterials = true
    },
    closeDeleteMaterials() {
      this.isShowDeleteMaterials = false
      this.submitting = false
      this.setEditable(false)
    },
    deleteCollectionPopup() {
      this.isShowDeleteCollection = true
    },
    closeDeleteCollection() {
      this.isShowDeleteCollection = false
      this.submitting = false
      this.setEditable(false)
    },
    deleteMaterials() {
      const { collection } = this
      const { materials_for_deleting } = this.formData
      this.$store
        .dispatch('removeMaterialFromMyCollection', {
          collection_id: collection.id,
          data: materials_for_deleting.map(material => {
            return {
              external_id: material
            }
          })
        })
        .then(() => {
          this.$nextTick().then(() => {
            this.$store.dispatch('putMyCollection', {
              ...this.collection,
              ...this.submitData
            })
            this.$store
              .dispatch('getMaterialInMyCollection', {
                id: collection.id,
                params: {
                  page_size: this.search.page_size,
                  page: 1
                }
              })
              .then(() => {
                this.closeDeleteMaterials()
                this.submitting = false
                this.setEditable(false)
              })
          })
        })
    },
    /**
     * Change 1 item in line to 4 and back.
     */
    changeViewType() {
      if (this.materials_in_line === 1) {
        this.materials_in_line = 4
      } else {
        this.materials_in_line = 1
      }
    },
    /**
     * Save collection
     * @param data - Object
     */
    onSubmit(data) {
      const { materials_for_deleting } = this.formData
      this.submitting = true
      this.submitData = data
      if (materials_for_deleting && materials_for_deleting.length) {
        this.deleteMaterialsPopup()
      } else {
        this.$store
          .dispatch('putMyCollection', {
            ...this.collection,
            ...data
          })
          .catch(() => {
            if (
              this.collection.publish_status === PublishStatus.PUBLISHED &&
              !this.collection.materials_count
            ) {
              this.$store.commit('ADD_MESSAGE', {
                level: 'error',
                message: 'can-not-publish-empty-collection'
              })
              this.collection.publish_status = PublishStatus.DRAFT
            }
          })
          .finally(() => {
            if (!materials_for_deleting || !materials_for_deleting.length) {
              this.submitting = false
              this.setEditable(false)
            }
          })
      }
    }
  }
}
</script>

<style lang="less">
@import '../variables';

.collection {
  width: 100%;
  padding: 80px 0 0;
}

.add-materials {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 50px;
}

.materials {
  margin-top: 20px;
}

.materials__add__link {
  padding: 13px 43px 13px 51px;
  background-image: url('/images/plus-black.svg');
  background-position: 10px 50%;
  background-repeat: no-repeat;
  background-size: 24px 24px;
}
</style>
