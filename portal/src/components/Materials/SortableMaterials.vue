<template>
  <section class="collection__materials">
    <slot name="header-info"></slot>
    <draggable
      v-model="myList"
      draggable=".materials__item"
      class="materials__items deleting"
      :class="{
        loading: current_loading,
        list: itemsInLine === 1,
        tile: itemsInLine > 1
      }"
    >
      <div
        v-for="(material, index) in myList"
        :key="material.external_id"
        :class="[
          `tile--items-in-line-${itemsInLine}`,
          `materials__item--items-in-line-${itemsInLine}`,
          'select-delete'
        ]"
        class="materials__item tile"
      >
        <div v-if="material.has_bookmark" class="materials__bookmark">Bookmark</div>
        <button v-if="contentEditable" class="select-icon" @click="deleteFromCollection(material)" />
        <Material
          :material="material"
          :handle-material-click="handleMaterialClick"
          :items-in-line="itemsInLine"
          :index="index"
        />
      </div>
    </draggable>
    <div v-if="myList.length === 0" class="not_found">{{ $t('Not-found') }}</div>
  </section>
</template>

<script>
import draggable from 'vuedraggable'
import { mapGetters } from 'vuex'
import Material from './Material/Material.vue'

export default {
  name: 'SortableMaterials',
  components: {
    draggable,
    Material,
  },
  props: {
    materials: {
      type: Object,
      default: null,
    },
    itemsInLine: {
      type: Number,
      default: 4,
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
    ...mapGetters(['materials_loading']),
    current_loading() {
      return this.materials_loading || this.loading
    },
    myList: {
      get() {
        if (this.materials) {
          return this.sortByPosition(
            this.shortenDescriptions(this.materials.records)
          )
        } else {
          return []
        }
      },
      set(values) {
        const { id } = this.$route.params
        const orderedList = values.map((value, index) => {
          value.position = index
          return value
        })
        const external_ids = values.map((material) => ({
          external_id: material.external_id,
        }))
        const materials = orderedList.map((material) => {
          return {
            external_id: material.external_id,
            position: material.position,
          }
        })
        this.$store
          .dispatch('removeMaterialFromCollection', {
            collection_id: id,
            data: external_ids,
          })
          .then(() => {
            this.$store.dispatch('addMaterialToCollection', {
              collection_id: id,
              data: materials,
            })
          })
      },
    },
  },
  methods: {
    handleMaterialClick(material) {
      this.$router.push(
        this.localePath({
          name: 'materials-id',
          params: { id: material.external_id },
        })
      )
    },
    deleteFromCollection(material) {
      const { id } = this.$route.params
      this.$store
        .dispatch('removeMaterialFromCollection', {
          collection_id: id,
          data: [{ external_id: material.external_id }],
        })
        .then(() => {
          Promise.all([
            this.$store.dispatch('getCollectionMaterials', id),
            this.$store.dispatch('getCollection', id),
          ]).then(() => null)
        })
    },
    shortenDescriptions(records) {
      if (!records) {
        return []
      }
      return records.map((record) => {
        if (record.description && record.description.length > 200) {
          record.description = record.description.slice(0, 200) + '...'
        }
        return record
      })
    },
    sortByPosition(records) {
      return records.sort((a, b) => (a.position > b.position ? 1 : -1))
    },
  },

}

</script>

<style lang="less" scoped>
@import "./../../variables";
.materials {
  &.community__materials h2 {
    margin-bottom: 20px;
  }
  &__items {
    padding: 0;
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(275px, 1fr));
    grid-gap: 1rem;

    &.list {
      grid-template-columns: repeat(auto-fit, minmax(100%, 1fr));

      @media @mobile {
        .materials__item_content {
          flex-direction: column;
        }
      }

      .materials__item_main_info {
        flex: 1;
        padding: 10px 20px 20px;
      }

      .materials__item_subinfo {
        padding: 10px 20px 20px;
        width: 230px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }
    }

    &.tile {
      .materials__item_content {
        flex-direction: column;
        justify-content: space-between;
      }
    }

    .select-icon {
      background-size: 20px 20px;
      position: absolute;
      left: 50%;
      top: -20px;
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

  &__item {
    list-style: none;
    background-color: #fff;
    font-size: 16px;
    line-height: 1.44;

    &_set-wrapper {
      padding: 10px 0 0 20px;
    }

    &_set {
      display: inline-flex;
      background-color: @light-grey;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 14px;
      align-items: center;

      &:before {
        content: "";
        display: inline-flex;
        vertical-align: middle;
        width: 13px;
        height: 13px;
        margin-right: 6px;
        background: url("../../assets/images/icon-set.svg") 50% 50% no-repeat;
        background-size: contain;
      }
    }

    &_set_count {
      display: flex;
      margin-top: 10px;
      align-items: center;
      font-size: 14px;

      &:before {
        content: "";
        display: inline-flex;
        vertical-align: middle;
        width: 13px;
        height: 13px;
        margin-right: 6px;
        background: url("../../assets/images/icon-materials.svg") 50% 50% no-repeat;
        background-size: contain;
      }
    }

    &.select-delete {
      cursor: pointer;
    }

    &_wrapper {
      display: flex;
      flex-direction: column;
    }

    &_content {
      flex: 1;
      display: flex;
    }

    &_main_info {
      padding: 10px 20px;
    }

    &_date {
      margin-top: 10px;
    }

    &_subinfo {
      padding: 0 20px 20px 20px;
    }

    &_footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 20px;
      background: @light-grey;
    }

    &_title {
      line-height: 1.2;
    }

    &_link {
      color: @dark-grey;
      text-decoration: none;

      &:hover {
        text-decoration: none;
      }
    }

    &_community_link {
      font-weight: bold;
      text-decoration: none;
      font-family: @second-font;
      position: relative;
      z-index: 1;

      &:hover {
        color: @black;
      }
    }

    &_author {
      font-weight: bold;

      .materials__item--items-in-line-1 & {
        font-weight: bold;
        display: inline-block;
      }
    }

    &_applauds {
      background: @green url("../../assets/images/clap_white.svg") 2px 50% no-repeat;
      background-size: 20px 20px;
      height: 25px;
      border-radius: 4px;
      color: #fff;
      font-size: 16px;
      font-weight: bold;
      min-width: 58px;
      padding-left: 23px;
      font-size: 1.1em;
    }

    &_external_link {
      background: @yellow url("../../assets/images/open-link-black.svg") 50% 50% no-repeat;
      background-size: 20px 20px;
      margin: 0 0 0 7px;
      display: inline-block;
      width: 35px;
      height: 25px;
      border-radius: 4px;
      overflow: hidden;
      color: transparent;
      position: relative;
      z-index: 1;

      &:hover {
        background-color: @orange-hover;
      }
    }

    &_copyrights {
      &.cc-by,
      &.cc-by-30,
      &.cc-by-40 {
        background: url("../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../assets/images/by-black.svg") no-repeat 23px 0;
        background-size: contain;
      }
      &.cc-by-nc,
      &.cc-by-nc-30,
      &.cc-by-nc-40 {
        background: url("../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../assets/images/nc-black.svg") no-repeat 46px 0;
        background-size: contain;
      }
      &.cc-by-nc-sa,
      &.cc-by-nc-sa-30,
      &.cc-by-nc-sa-40 {
        background: url("../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../assets/images/nc-black.svg") no-repeat 46px 0,
          url("../../assets/images/sa-black.svg") no-repeat 69px 0;
        background-size: contain;
      }
      &.cc-by-nd,
      &.cc-by-nd-30,
      &.cc-by-nd-40 {
        background: url("../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../assets/images/nd-black.svg") no-repeat 46px 0;
        background-size: contain;
      }
      &.cc-by-sa,
      &.cc-by-sa-30,
      &.cc-by-sa-40 {
        background: url("../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../assets/images/sa-black.svg") no-repeat 46px 0;
        background-size: contain;
      }
      &.yes,
      &.cc-by-nc-nd,
      &.cc-by-nc-nd-30,
      &.cc-by-nc-nd-40 {
        background: url("../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../assets/images/nc-black.svg") no-repeat 46px 0,
          url("../../assets/images/nd-black.svg") no-repeat 69px 0;
        background-size: contain;
      }
      height: 20px;
      margin: 6px 0px 3px;
      width: 100%;
      display: block;
      background-size: contain;
    }

    &_actions {
      display: flex;
      align-items: center;
    }

    &_description {
      padding: 16px 0 0;
    }
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
}
</style>
