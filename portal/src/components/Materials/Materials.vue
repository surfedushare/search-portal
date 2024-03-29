<template>
  <section class="materials mb-4">
    <slot name="header-info"></slot>
    <ul
      v-if="selectedMaterials && selectedMaterials.length"
      data-test="search_results"
      class="materials__items"
      :class="{
        loading: current_loading,
        deleting: selectFor === 'delete',
        adding: selectFor !== 'delete',
      }"
    >
      <li
        v-for="(material, index) in selectedMaterials"
        :key="index"
        :class="selectMaterialClass"
        class="materials__item tile"
      >
        <div v-if="material.has_bookmark" class="materials__bookmark">Bookmark</div>
        <button
          v-if="contenteditable"
          data-test="add_select_icon"
          :class="{ 'select-icon': true, selected: material.selected }"
          @click="selectMaterial(material)"
        />
        <div v-if="$vuetify.breakpoint.name !== 'xs'">
          <MaterialListCard :material="material" :handle-material-click="handleMaterialClick" />
        </div>
      </li>
    </ul>

    <div
      v-else-if="!current_loading && has_no_results_with_search_filters"
      data-test="no_search_results"
      class="not_found"
    >
      <div class="not_found__icon"></div>
      <div class="not_found__message">
        {{ $t("No-results-for-filters") }}
        <div class="not_found__info">
          <i>{{ $t("Not-found-info") }}</i>
        </div>
      </div>
    </div>

    <div v-else-if="!current_loading && has_no_result_suggestion" data-test="search_suggestion" class="not_found">
      <div class="not_found__icon"></div>
      <div class="not_found__message">
        {{ $t("Did-you-mean") }}
        <a :href="no_result_suggestion_link" data-test="search_suggestion_link">{{ didYouMean.suggestion }}</a>
        ?
        {{ $t("Because-no-results-for") }} '{{ didYouMean.original }}'
        <div class="not_found__info">
          <i>{{ $t("Adjust-your-search-query") }}</i>
        </div>
      </div>
    </div>

    <div v-else-if="!current_loading" data-test="no_search_results" class="not_found">
      <div class="not_found__icon"></div>
      <div class="not_found__message">
        {{ $t("No-results-for") }} '{{ searchTerm }}'
        <div class="not_found__info">
          <i>{{ $t("Not-found-info") }}</i>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from "vuex";
import MaterialListCard from "./MaterialListCard.vue";
import { isEmpty } from "lodash";
import { generateSearchMaterialsQuery } from "../_helpers";

export default {
  name: "Materials",
  components: {
    MaterialListCard,
  },
  props: {
    materials: {
      type: Object,
      default: null,
    },
    didYouMean: {
      type: Object,
      default: () => {
        return null;
      },
    },
    itemsLength: {
      type: [Number, String],
      default: "auto",
    },
    loading: {
      type: Boolean,
      default: false,
    },
    contenteditable: {
      type: Boolean,
      default: false,
    },
    selectFor: {
      type: String,
      default: "delete",
    },
    searchTerm: {
      type: String,
      default: "",
    },
    value: {
      required: false,
      type: Array,
      default: null,
    },
  },
  data() {
    return {
      selectedMaterialIds: this.value || [],
    };
  },
  computed: {
    ...mapGetters(["materials_loading", "selected_filters"]),
    selectMaterialClass() {
      return this.selectFor === "delete" ? "select-delete" : "select-neutral";
    },
    current_loading() {
      return this.materials_loading || this.loading;
    },
    selectedMaterials() {
      const { materials, selectedMaterialIds } = this;
      if (materials) {
        const arrMaterials = materials.records ? materials.records : materials;

        return arrMaterials.map((material) => {
          return {
            ...material,
            selected: selectedMaterialIds.indexOf(material.external_id) !== -1,
          };
        });
      }
      return false;
    },
    has_no_results_with_search_filters() {
      return !isEmpty(this.selected_filters);
    },
    has_no_result_suggestion() {
      return this.didYouMean?.suggestion;
    },
    no_result_suggestion_link() {
      let searchQuery = generateSearchMaterialsQuery({
        search_text: this.didYouMean.suggestion,
        filters: this.materials.search_filters,
        page_size: 10,
        page: 1,
      });
      return this.$router.resolve(searchQuery).href;
    },
  },
  watch: {
    value(value) {
      this.selectedMaterialIds = value;
    },
  },
  methods: {
    handleMaterialClick(material) {
      if (this.selectFor === "add") {
        this.$store.commit("SET_MATERIAL", material);
      } else {
        this.$router.push(
          this.localePath({
            name: "materials-id",
            params: { id: material.external_id },
          })
        );
      }
      this.$emit("click", material);
    },
    selectMaterial(material) {
      if (this.selectFor === "delete") {
        this.deleteMaterial(material);
      } else {
        this.$emit("input", this.toggleMaterial(material));
      }
    },
    deleteMaterial(material) {
      const { id } = this.$route.params;
      this.$store
        .dispatch("removeMaterialFromCollection", {
          collection_id: id,
          data: [{ external_id: material.external_id }],
        })
        .then(() => {
          Promise.all([
            this.$store.dispatch("getCollectionMaterials", id),
            this.$store.dispatch("getCollection", id),
          ]).then(() => null);
        });
    },
    toggleMaterial(material) {
      let selectedMaterialIds = this.value.slice(0);

      if (selectedMaterialIds.indexOf(material.external_id) === -1) {
        selectedMaterialIds.push(material.external_id);
      } else {
        selectedMaterialIds = selectedMaterialIds.filter((item) => item !== material.external_id);
      }
      return selectedMaterialIds;
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../../variables";
.materials {
  &__items {
    display: grid;
    gap: 48px;
    list-style: none;

    &.list {
      grid-template-columns: repeat(auto-fit, minmax(100%, 1fr));
    }

    &.tile {
      .materials__item_content {
        flex-direction: column;
        justify-content: space-between;
      }
    }

    .select-icon {
      background-size: 20px 20px;
      position: relative;
      left: 50%;
      top: 15px;
      width: 40px;
      height: 40px;
      color: transparent;
      overflow: hidden;
      padding: 0;
      cursor: pointer;
      z-index: 1;
      border-radius: 50%;
      transform: translate(-50%, 0);
      border: 0;

      &:focus {
        outline: none;
      }
    }

    &.deleting {
      .select-icon {
        background: @light-grey url("../../assets/images/close-grey.svg") 50% 50% no-repeat;
      }
      .selected {
        opacity: 0.5;
        pointer-events: none;
      }
    }
    &.adding {
      gap: unset;
      .select-icon {
        background: @light-grey url("../../assets/images/plus-black.svg") 50% 50% no-repeat;
      }
      .select-icon.selected {
        background: @green url("../../assets/images/plus-white.svg") 50% 50% no-repeat;
      }
    }
  }
  &__description {
    font-size: 20px;
    line-height: 1.15;
    margin: 1px 0 76px;
  }

  &__bookmark {
    width: 24px;
    height: 39px;
    position: absolute;
    right: 17px;
    top: -3px;
    overflow: hidden;
    color: transparent;
    background: url("../../assets/images/label.svg") 50% 0 no-repeat;
  }
  .not_found {
    display: grid;
    grid-auto-flow: column;
    grid-template-rows: repeat(2, max-height);
    grid-template-columns: auto 1fr;
    width: 100%;
    margin: 0 auto;
    background-color: @light-grey;
    border-radius: 20px;
    box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
    padding: 24px;
    &__icon {
      display: inline-block;
      border-radius: 50%;
      background: @green url("../../assets/images/search-white.svg") 50% 50% no-repeat;
      height: 48px;
      width: 48px;
    }
    &__message {
      grid-template-rows: repeat(2, max-height);
      min-height: 48px;
      padding-left: 24px;
      font-weight: 800;
      font-size: 20px;
    }
    &__info {
      color: @dark-grey;
      font-weight: 400;
      font-size: 16px;
    }
    &__suggestion {
      color: @green;
    }
  }
}
</style>
