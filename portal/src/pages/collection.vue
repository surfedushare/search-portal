<template>
  <section class="edusources-container main collection" :class="{ 'new-header': isNewHeader }">
    <div v-if="!collectionInfo && isReady">
      <error status-code="404" message-key="collection-not-found" />
    </div>
    <div v-else class="center_block">
      <Collection
        v-if="collectionInfo"
        v-model="search"
        :collection="collectionInfo"
        :contenteditable="contenteditable"
        :submitting="submitting"
        :change-view-type="changeViewType"
        :items-in-line="materials_in_line"
        @onSubmit="onSubmit"
      />

      <div class="add-materials">
        <button
          v-if="contenteditable"
          data-test="add_materials_button"
          class="button secondary"
          @click.prevent="showAddMaterial"
        >
          {{ $t("Add-materials") }}
        </button>

        <v-btn
          v-else-if="collection && hasPermission"
          data-test="add_materials_button"
          elevation="0"
          class="bg-yellow mr-4"
          :to="localePath({ name: 'my-collection', params: { id: collection.id }, force: true })"
        >
          {{ $t("Edit-collection") }}
        </v-btn>
      </div>
      <SortableMaterials
        v-if="contenteditable && collection_materials"
        :materials="collection_materials"
        :loading="collection_materials_loading"
        :content-editable="contenteditable"
      />

      <MaterialCards v-if="!contenteditable" :materials="collection_materials" />
      <Spinner v-if="collection_materials_loading" />
    </div>
    <DeleteCollection :close="closeDeleteCollection" :is-show="isShowDeleteCollection" />
    <AddMaterialPopup
      v-if="isShowAddMaterial && collection && collection_materials"
      :close="closeAddMaterial"
      :is-show="isShowAddMaterial"
      :collection-id="collection.id"
      :collection-count="collection_materials.length"
      @submitted="saveMaterials"
    />
  </section>
</template>

<script>
import { isEmpty } from "lodash";
import { mapGetters } from "vuex";
import AddMaterialPopup from "~/components/Collections/AddMaterialPopup";
import Collection from "~/components/Collections/Collection";
import Error from "~/components/error";
import MaterialCards from "~/components/Materials/MaterialCards.vue";
import SortableMaterials from "~/components/Materials/SortableMaterials.vue";
import DeleteCollection from "~/components/Popup/DeleteCollection";
import Spinner from "~/components/Spinner";
import PageMixin from "~/pages/page-mixin";
import { PublishStatus } from "~/utils";

export default {
  components: {
    MaterialCards,
    SortableMaterials,
    Collection,
    Spinner,
    DeleteCollection,
    Error,
    AddMaterialPopup,
  },
  mixins: [PageMixin],
  data() {
    return {
      contenteditable: this.$route.meta.editable,
      isShowDeleteCollection: false,
      submitting: false,
      submitData: false,
      materials_in_line: 4,
      search: {
        page_size: 10,
        page: 1,
        filters: [],
        search_text: "",
      },
      isShowAddMaterial: false,
    };
  },
  computed: {
    ...mapGetters(["collection", "collection_materials", "collection_materials_loading", "user", "isNewHeader"]),
    collectionInfo() {
      if (isEmpty(this.collection)) {
        return null;
      } else if (this.collection.publish_status === PublishStatus.PUBLISHED) {
        return this.collection;
      } else if (this.user && this.user.collections.find((collection) => collection.id === this.collection.id)) {
        return this.collection;
      }

      return null;
    },
    hasPermission() {
      return this.user && this.user.collections?.find((collection) => collection.id === this.collection.id);
    },
  },
  created() {
    const { id } = this.$route.params;
    this.$store.dispatch("getCollectionMaterials", id);
    this.pageLoad = Promise.all([this.$store.dispatch("getCollection", id), this.$store.dispatch("getUser")]);
  },
  metaInfo() {
    const defaultTitle = this.$root.$meta().title;
    return {
      title: this.collectionInfo ? this.collectionInfo[`title_${this.$i18n.locale}`] || defaultTitle : defaultTitle,
    };
  },
  methods: {
    showAddMaterial() {
      this.isShowAddMaterial = true;
    },
    closeAddMaterial() {
      this.isShowAddMaterial = false;
      this.materialsUpdateKey += 1;
    },
    saveMaterials() {
      const { id } = this.$route.params;
      this.isReady = false;
      Promise.all([
        this.$store.dispatch("getCollectionMaterials", id),
        this.$store.dispatch("getCollection", id),
      ]).finally(() => {
        this.isReady = true;
      });
    },
    deleteCollectionPopup() {
      this.isShowDeleteCollection = true;
    },
    closeDeleteCollection() {
      this.isShowDeleteCollection = false;
      this.submitting = false;
    },
    changeViewType() {
      if (this.materials_in_line === 1) {
        this.materials_in_line = 4;
      } else {
        this.materials_in_line = 1;
      }
    },
    onSubmit(data) {
      this.submitting = true;
      this.submitData = data;
      this.$store
        .dispatch("editCollection", {
          ...this.collection,
          ...data,
        })
        .catch(() => {
          if (this.collection.publish_status === PublishStatus.PUBLISHED && !this.collection.materials_count) {
            this.$store.commit("ADD_MESSAGE", {
              level: "error",
              message: "can-not-publish-empty-collection",
            });
            this.collection.publish_status = PublishStatus.DRAFT;
          }
        })
        .finally(() => {
          this.submitting = false;
        });
    },
  },
};
</script>

<style lang="less" scoped>
@import "../variables";

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
  background-image: url("../assets/images/plus-black.svg");
  background-position: 10px 50%;
  background-repeat: no-repeat;
  background-size: 24px 24px;
}
</style>
