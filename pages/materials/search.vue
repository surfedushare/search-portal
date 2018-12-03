<template>
  <section class="container search">
    <div>
      <div
        class="search__info"
      >
        <div class="center_block">
          <div class="search__info_top">
            <BreadCrumbs :items="items" />
            <h2 v-if="materials">Zoekresultaten ({{ materials.records_total }})</h2>
          </div>
          <Search
            v-if="search"
            :hide-categories="true"
            :hide-filter="true"
            v-model="search"
            class="search__info_search"
          />
        </div>
      </div>
      <div class="search__tools center_block">
        <DatesRange />
        <button
          class="search__tools_type_button"
          @click.prevent="changeViewType"
        >
          Kaartweergave
        </button>
      </div>
      <div
        v-infinite-scroll="loadMore"
        infinite-scroll-disabled="materials_loading"
        infinite-scroll-distance="10"
        class="search__wrapper center_block"
      >
        <div class="search__filter">
          <div class="search__filter_sticky">
            <FilterCategories
              v-model="search"
              :show-popup-save-filter="showPopupSaveFilter"
            />
          </div>
        </div>

        <div
          v-if="materials"
          class="search__materials"
        >
          <Materials
            :materials="materials"
            :items-in-line="materials_in_line"
          />
          <Spinner />
        </div>
      </div>
    </div>
    <transition name="fade">
      <Popup
        v-if="isShow"
        :close="close"
        :is-show="isShow"
        class="save_filter"
      >
        <slot>
          <h2 class="save_filter__title">Selectie opslaan</h2>
          <form
            action=""
            @submit.prevent="onSaveFilter"
          >
            <div class="form__item">
              <input
                v-model="formData.name"
                type="text"
                placeholder="Name"
                class="input"
                required="required"
                name="name"
              >
            </div>
            <button
              class="button"
              type="submit"
            >
              Save
            </button>
          </form>
        </slot>
      </Popup>
    </transition>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Search from '~/components/FilterCategories/Search/index.vue';
import FilterCategories from '~/components/FilterCategories';
import PopularList from '~/components/Communities/PopularList';
import Materials from '~/components/Materials';
import Themes from '~/components/Themes';
import Spinner from '~/components/Spinner';
import BreadCrumbs from '~/components/BreadCrumbs';
import Popup from '~/components/Popup';
import DatesRange from '~/components/DatesRange';

export default {
  components: {
    Search,
    FilterCategories,
    PopularList,
    Materials,
    Themes,
    Spinner,
    BreadCrumbs,
    Popup,
    DatesRange
  },
  data() {
    return {
      search_text: [],
      search: false,
      isShow: false,
      date_range: {
        external_id: 'lom.lifecycle.contribute.publisherdate',
        items: ['2018-01-05', '2018-06-09']
      },
      formData: {
        name: null
      },
      items: [
        {
          title: 'Home',
          url: '/'
        }
      ]
    };
  },
  computed: {
    ...mapGetters(['materials', 'materials_loading', 'materials_in_line'])
  },
  watch: {
    search(search) {
      if (search) {
        this.$store.dispatch('searchMaterials', search);
      }
    }
  },
  mounted() {
    const search = Object.assign({}, this.$route.query, {
      filters: JSON.parse(this.$route.query.filters),
      search_text: JSON.parse(this.$route.query.search_text)
    });

    this.search = search;
    this.$store.dispatch('searchMaterials', search);
  },
  methods: {
    /**
     * Load next materials
     */
    loadMore() {
      const { search } = this;
      const { page_size, page, records_total } = this.materials;
      if (records_total > page_size * page) {
        this.$store.dispatch(
          'searchNextPageMaterials',
          Object.assign({}, search, { page: page + 1 })
        );
      }
    },
    /**
     * Change 1 item in line to 3 and back.
     */
    changeViewType() {
      if (this.materials_in_line === 1) {
        this.$store.dispatch('searchMaterialsInLine', 3);
      } else {
        this.$store.dispatch('searchMaterialsInLine', 1);
      }
    },
    showPopupSaveFilter() {
      this.isShow = true;
    },
    close() {
      this.isShow = false;
    },
    onSaveFilter() {
      console.log(111);
    }
  }
};
</script>

<style lang="less" scoped>
@import './../../assets/styles/variables';
.search {
  position: relative;

  &__info {
    padding: 97px 0 0;
    margin-bottom: 82px;
    position: relative;
    min-height: 300px;

    &_top {
      border-radius: 20px;
      background: fade(@light-grey, 90%);
      padding: 65px 576px 65px 46px;
      min-height: 274px;
      margin: 0 0 -68px;
    }

    &_search {
      width: 996px;
      margin: auto;
    }

    &_title {
      line-height: 1.25;
      color: #fff;
      margin: 0 0 20px;
    }
    &_item {
      margin: 0 0 14px;
      list-style: none;
      padding: 0;
    }
    &_block {
      background: fade(@dark-blue, 90%);
      color: #fff;
      width: 572px;
      border-radius: 20px;
      margin: -39px 0 99px 541px;
      padding: 31px 48px 33px;
      font-family: @second-font;
      font-size: 16px;
      font-weight: bold;
    }
  }

  &__wrapper {
    display: flex;
    position: relative;
  }

  &__tools {
    width: 100%;
    justify-content: flex-end;
    display: flex;
    margin-bottom: -30px;
    position: relative;
    z-index: 1;

    &_type_button {
      border-radius: 0;
      border: 0;
      color: @dark-blue;
      background: transparent url('./../../assets/images/card-view-copy.svg') 0
        50% no-repeat;
      font-family: @second-font;
      font-size: 16px;
      font-weight: bold;
      height: 50px;
      padding: 0 8px 0 40px;
      margin: 0 0 0 31px;
      cursor: pointer;

      &:focus,
      &:active {
        outline: none;
      }
    }
    .select {
      height: 50px;
      width: 251px;
    }
  }

  &__filter {
    width: 250px;
    flex-shrink: 0;
    margin: 0 64px 0 0;

    &_sticky {
      position: sticky;
      top: 0;
      left: 0;
      width: 100%;
      padding-top: 102px;
      padding-bottom: 102px;
    }
  }

  &__materials {
    position: relative;
    margin: 0 0 132px;
    flex: 1 1 auto;
    padding: 98px 0 0;
  }
}

.save_filter {
  &__title {
    margin: 0 0 30px;
  }
}
</style>
