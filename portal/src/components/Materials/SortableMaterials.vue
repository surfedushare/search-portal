<template>
  <section>
    <slot name="header-info"></slot>

    <draggable v-model="myList" class="row deleting">
      <v-col v-for="material in myList" data-test="materials" :key="material.external_id" class="select-delete" lg="3">
        <div v-if="material.has_bookmark" class="bookmark">Bookmark</div>
        <button
          v-if="contentEditable"
          data-test="delete_select_icon"
          class="select-icon"
          @click="deleteFromCollection(material)"
        />
        <MaterialCard :material="material" :handle-material-click="handleMaterialClick" />
      </v-col>
    </draggable>
    <div v-if="myList.length === 0" class="not_found">{{ $t("Not-found") }}</div>
  </section>
</template>

<script>
import draggable from "vuedraggable";
import { mapGetters } from "vuex";
import MaterialCard from "~/components/Materials/MaterialCard.vue";

export default {
  name: "SortableMaterials",
  components: {
    draggable,
    MaterialCard,
  },
  props: {
    materials: {
      type: Object,
      default: null,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    contentEditable: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    ...mapGetters(["materials_loading"]),
    current_loading() {
      return this.materials_loading || this.loading;
    },
    myList: {
      get() {
        if (this.materials) {
          return this.sortByPosition(this.shortenDescriptions(this.materials.records));
        } else {
          return [];
        }
      },
      set(values) {
        const { id } = this.$route.params;
        const orderedList = values.map((value, index) => {
          value.position = index;
          return value;
        });
        const external_ids = values.map((material) => ({
          external_id: material.external_id,
        }));
        const materials = orderedList.map((material) => {
          return {
            external_id: material.external_id,
            position: material.position,
          };
        });
        this.$store
          .dispatch("removeMaterialFromCollection", {
            collection_id: id,
            data: external_ids,
          })
          .then(() => {
            this.$store.dispatch("addMaterialToCollection", {
              collection_id: id,
              data: materials,
            });
          });
      },
    },
  },
  methods: {
    handleMaterialClick(material) {
      this.$router.push(
        this.localePath({
          name: "materials-id",
          params: { id: material.external_id },
        })
      );
    },
    deleteFromCollection(material) {
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
    shortenDescriptions(records) {
      if (!records) {
        return [];
      }
      return records.map((record) => {
        if (record.description && record.description.length > 200) {
          record.description = record.description.slice(0, 200) + "...";
        }
        return record;
      });
    },
    sortByPosition(records) {
      return records.sort((a, b) => (a.position > b.position ? 1 : -1));
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../../variables";

.select-icon {
  background-size: 20px 20px;
  position: relative;
  left: 50%;
  top: 15x;
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
}

.deleting {
  .select-icon {
    background: @light-grey url("../../assets/images/close-grey.svg") 50% 50% no-repeat;
  }
  .selected {
    opacity: 0.5;
    pointer-events: none;
  }
}
.adding {
  .select-icon {
    background: @light-grey url("../../assets/images/plus-black.svg") 50% 50% no-repeat;
  }
  .select-icon.selected {
    background: @green url("../../assets/images/plus-white.svg") 50% 50% no-repeat;
  }
}
.bookmark {
  width: 24px;
  height: 39px;
  position: absolute;
  right: 17px;
  top: -3px;
  overflow: hidden;
  color: transparent;
  background: url("../../assets/images/label.svg") 50% 0 no-repeat;
}
</style>
