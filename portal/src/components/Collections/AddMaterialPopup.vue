<template>
  <transition name="fade">
    <Popup v-if="isShow" :close="close" :is-show="isShow" class="add-material">
      <div class="content-container center_block">
        <div class="flex-container">
          <h2 class="popup__title">
            {{ $t('Add-materials-to-collection') }}
          </h2>
          <button class="button secondary" @click.prevent="onSaveMaterials">
            {{ $t('Add-selected-materials', { count: selection.length }) }}
          </button>
        </div>
        <Search
          v-model="search"
          class="add_materials__info_search"
          @onSearch="onSearch"
        />

        <div
          v-infinite-scroll="loadMore"
          infinite-scroll-disabled="materials_loading"
          infinite-scroll-distance="10"
          class="search__wrapper"
        >
          <div class="search__materials">
            <Materials
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
import { isEmpty } from 'lodash'
import { mapGetters } from 'vuex'
import Popup from '~/components/Popup'
import Search from '~/components/Search'
import Materials from '~/components/Materials'

export default {
  name: 'AddMaterialPopup',
  components: {
    Popup,
    Search,
    Materials
  },
  props: {
    isShow: { type: Boolean },
    close: { type: Function, default: () => {} },
    collectionId: { type: String, default: '' },
    collectionCount: { type: Number, default: 0 }
  },
  data() {
    return {
      search: '',
      selection: [],
      saved: false,
      submitting: false
    }
  },
  computed: {
    ...mapGetters(['materials', 'materials_loading'])
  },
  watch: {
    isShow(shouldShow) {
      if (!shouldShow) {
        this.reset()
      }
    }
  },
  methods: {
    onSearch() {
      this.$store.dispatch('searchMaterials', {
        search_text: this.search,
        page_size: 10,
        page: 1
      })
    },
    loadMore() {
      const { search, materials } = this
      if (materials && !isEmpty(search)) {
        const { page_size, page, records_total } = materials

        if (records_total > page_size * page) {
          this.$store.dispatch('searchNextPageMaterials', {
            search_text: this.search,
            page_size: page_size,
            page: page + 1
          })
        }
      }
    },
    reset() {
      this.search = ''
      this.selection = []
    },
    onSaveMaterials() {
      this.submitting = true
      const data = this.selection.map((material, index) => {
        return {
          external_id: material,
          position: index + this.collectionCount
        }
      })
      this.$store
        .dispatch('addMaterialToCollection', {
          collection_id: this.collectionId,
          data
        })
        .then(collection => {
          this.saved = true
          if (this.$listeners.submitted) {
            this.$emit('submitted', collection)
          }
        })
        .finally(() => {
          this.submitting = false
          this.close()
        })
    }
  }
}
</script>

<style lang="less">
.popup.add-material .popup__center {
  max-width: calc(100% - 200px);
  width: 1050px;
}
</style>
<style lang="less" scoped>
@import '../../variables';

.content-container {
  overflow: scroll;
  display: flex;
  flex-direction: column;
}

.flex-container {
  justify-content: space-between;
}

.add-material {
  .popup__center {
    max-height: calc(100vh - 200px);
    /* overflow-y: scroll; */
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
