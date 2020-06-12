<template>
  <transition name="fade">
    <Popup
      v-if="isShow"
      :close="close"
      :is-show="isShow"
      class="add-material"
    >
      <div>
        <div class="flex-container">
          <h2 class="popup__title">{{ $t('Add-materials-to-collection') }}</h2>
          <button class="button secondary" @click.prevent="onSaveMaterials">
            {{ $t('Add-selected-materials', {count: selection.length}) }}
          </button>
        </div>
        <Search
          :hide-filter="true"
          v-model="search"
          @submit="onSearch"
          class="add_materials__info_search"

        />

        <div
          v-infinite-scroll="loadMore"
          infinite-scroll-disabled="materials_loading"
          infinite-scroll-distance="10"
          class="search__wrapper center_block"
        >
          <div class="search__materials">
            <Materials :materials="materials" :items-in-line="2" selectFor="add"
                       contenteditable="true" v-model="selection"/>
          </div>
        </div>
      </div>
    </Popup>
  </transition>
</template>

<script>

  import { isEmpty, map } from 'lodash';
  import { mapGetters } from 'vuex';
  import Popup from '~/components/Popup';
  import Search from '~/components/FilterCategories/Search';
  import Materials from '~/components/Materials';


  export default {
    name: 'add-collection',
    props: ['is-show', 'close', 'submit-method', 'collection-id'],
    components: {
      Popup,
      Search,
      Materials
    },
    data() {
      return {
        search: {},
        selection: [],
        saved: false,
        submitting: false,
        formData: {
          title: null
        }
      };
    },
    watch: {
      search(search) {
        if (search && !this.materials_loading) {
          this.$store.dispatch('searchMaterials', search);
        }
      },
      isShow(shouldShow) {
        if(!shouldShow) {
          this.reset()
        }
      }
    },
    methods: {
      onSearch(searchData) {
        this.search = searchData;
        this.$store.dispatch('searchMaterials', searchData);
      },
      loadMore() {
        const { search, materials } = this;
        if (materials && !isEmpty(search)) {
          const { page_size, page, records_total } = materials;

          if (records_total > page_size * page) {
            this.$store.dispatch(
              'searchNextPageMaterials',
              Object.assign({}, search, { page: page + 1 })
            );
          }
        }
      },
      reset() {
        this.search = {};
        this.selection = []
      },
      onSaveMaterials() {
        this.submitting = true;
        let submitData = {
          collection_id: this.collectionId,
          data: map(this.selection, (external_id) => {return { external_id }})
        };
        this.$store
          .dispatch(this.submitMethod || 'setMaterialInMyCollection', submitData)
          .then(collection => {
            this.$store.dispatch('getUser');
            this.saved = true;
            if (this.$listeners.submitted) {
              this.$emit('submitted', collection);
            }
          })
          .finally(() => {
            this.submitting = false;
          });
      }
    },
    computed: {
      ...mapGetters([
        'materials',
        'materials_loading'
      ])
    }
  };

</script>

<style lang="less">

  @import "../../variables";

  .add-material {
    .popup__center {
      max-height: calc(100vh - 200px);
      overflow-y: scroll
    }
  }
  .add_materials__info_search {
    margin: 40px auto;
  }

</style>

