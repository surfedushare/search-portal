<template>
  <transition name="fade">
    <Popup v-if="isShow" :close="close" :is-show="isShow" class="add-material">
      <div class="content-container center_block">
        <div class="flex-container">
          <h2 class="popup__title">{{ $t("Add-materials-to-collection") }}</h2>
          <button data-test="popup_add_materials_button" class="button secondary" @click.prevent="onSaveMaterials">
            {{ $t("Add-selected-materials", { count: selection.length }) }}
          </button>
        </div>
        <SearchTerm class="add_materials__info_search" @search="onSearch" />

        <div
          v-infinite-scroll="loadMore"
          infinite-scroll-disabled="materials_loading"
          infinite-scroll-distance="10"
          class="search__wrapper"
        >
          <div class="search__materials">
            <Materials
              v-if="materials"
              v-model="selection"
              :materials="materials"
              :items-in-line="2"
              select-for="add"
              :contenteditable="true"
            />
          </div>
        </div>
      </div>
    </Popup>
  </transition>
</template>

<script>
import { isEmpty } from "lodash";
import { mapGetters } from "vuex";
import Materials from "~/components/Materials/Materials.vue";
import Popup from "~/components/Popup";
import SearchTerm from "~/components/Search/SearchTerm.vue";

export default {
  name: "AddMaterialPopup",
  components: {
    Popup,
    Materials,
    SearchTerm,
  },
  props: {
    isShow: { type: Boolean },
    close: { type: Function, default: () => {} },
    collectionId: { type: String, default: "" },
    collectionCount: { type: Number, default: 0 },
  },
  data() {
    return {
      selection: [],
      saved: false,
      submitting: false,
    };
  },
  computed: {
    ...mapGetters(["materials", "materials_loading"]),
  },
  watch: {
    isShow(shouldShow) {
      if (!shouldShow) {
        this.reset();
      }
    },
  },
  methods: {
    onSearch(searchText) {
      this.$store.dispatch("searchMaterials", {
        search_text: searchText || "",
        page_size: 10,
        page: 1,
      });
    },
    loadMore() {
      const { search, materials } = this;
      if (materials && !isEmpty(search)) {
        const { page_size, page, records_total } = materials;

        if (records_total > page_size * page) {
          this.$store.dispatch("searchNextPageMaterials", {
            search_text: this.search,
            page_size: page_size,
            page: page + 1,
          });
        }
      }
    },
    reset() {
      this.search = "";
      this.selection = [];
    },
    onSaveMaterials() {
      this.submitting = true;
      const data = this.selection.map((material, index) => {
        return {
          external_id: material,
          position: index + this.collectionCount,
        };
      });
      this.$store
        .dispatch("addMaterialToCollection", {
          collection_id: this.collectionId,
          data,
        })
        .then((collection) => {
          this.saved = true;
          if (this.$listeners.submitted) {
            this.$emit("submitted", collection);
          }
        })
        .finally(() => {
          this.submitting = false;
          this.close();
        });
    },
  },
};
</script>

<style lang="less" scoped>
@import "../../variables";
.popup.add-material .popup__center {
  max-width: calc(100% - 200px);
  width: 1050px;
}

.content-container {
  overflow: scroll;
  display: flex;
  flex-direction: column;
}

.flex-container {
  justify-content: space-between;
}

.add-material {
  .center_block {
    max-height: calc(100vh - 300px);
    overflow: hidden;
  }
}
.add_materials__info_search {
  margin-top: 20px;
}

.search__wrapper {
  overflow: visible;
  overflow-y: scroll;
  padding: 0 20px;
  margin: 0 -20px;
}
</style>
