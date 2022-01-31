<template>
  <section class="container search">
    <div>
      <div class="search__info">
        <div class="center_block center-header">
          <img class="main__info_bg" src="/images/pictures/header-image.jpg" alt="header-image" />
          <SearchBar @onSearch="initialSearch" />
        </div>
      </div>

      <div class="search__tools center_block">
        <h2
          v-if="materials && !materials_loading"
          class="search__tools_results"
        >{{ $t('Search-results') }} {{ `(${materials.records_total})` }}</h2>
        <label for="search_order_select">{{ $t('sort_by') }}: &nbsp;</label>
        <div class="search__chooser search__select">
          <select id="search_order_select" v-model="sort_order" @change="changeOrdering">
            <option
              v-for="option in sort_order_options"
              :key="option.value"
              :value="option.value"
            >&nbsp;&nbsp;{{ $t(option.value) }}</option>
          </select>
        </div>
        <button
          :class="{
            'search__tools_type_button--list': materials_in_line === 3,
            'search__tools_type_button--cards': materials_in_line === 1,
          }"
          class="search__tools_type_button"
          @click.prevent="changeViewType"
        >{{ materials_in_line === 1 ? $t('Card-view') : $t('List-view') }}</button>
      </div>

      <div
        v-infinite-scroll="loadMore"
        infinite-scroll-disabled="materials_loading"
        infinite-scroll-distance="10"
        class="search__wrapper center_block"
      >
        <div v-if="showFilterCategories" class="search__filter">
          <div class="search__filter_content">
            <FilterCategories
              v-model="search"
              :selected-filters="search.filters"
              :default-filter="$route.params.filterId"
              :materials="materials"
              @reset="onSearch"
            />
          </div>
        </div>

        <div class="search__materials">
          <Materials
            :materials="materials"
            :items-in-line="materials_in_line"
            :did-you-mean="did_you_mean"
          />
          <Spinner v-if="materials_loading" />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'
import FilterCategories from '~/components/FilterCategories'
import Materials from '~/components/Materials'
import Spinner from '~/components/Spinner'
import {
  addFilter, generateSearchMaterialsQuery,
  parseSearchMaterialsQuery
} from '~/components/_helpers'
import PageMixin from '~/pages/page-mixin'
import SearchBar from '../components/Search/SearchBar.vue'

export default {
  components: {
    FilterCategories,
    Materials,
    Spinner,
    SearchBar
  },
  mixins: [PageMixin],
  data() {
    const urlInfo = parseSearchMaterialsQuery(this.$route.query)
    return {
      search: urlInfo.search,
      formData: {
        name: null,
      },
      sort_order: 'relevance',
      sort_order_options: [
        { value: 'relevance' },
        { value: 'date_descending' },
        { value: 'date_ascending' },
      ],
    }
  },
  computed: {
    ...mapGetters([
      'materials',
      'materials_loading',
      'materials_in_line',
      'did_you_mean',
    ]),
    defaultFilterTitle() {
      if (!this.$route.params.filterId) {
        return
      }
      const defaultFilter = this.$store.getters.getCategoryById(
        this.$route.params.filterId,
        this.$route.meta.filterRoot
      )
      return defaultFilter
        ? defaultFilter.title_translations[this.$i18n.locale]
        : null
    },
    showFilterCategories() {
      return this.isReady && this.materials && this.materials.records && this.materials.records.length
    },
  },
  watch: {
    search(search) {
      if (search && !this.materials_loading) {
        this.executeSearch()
      }
    },
  },
  mounted() {
    this.loadFilterCategories().finally(() => {
      this.executeSearch()
    })
  },
  beforeRouteLeave(to, from, next) {
    if (!from.params.filterId || to.params.filterId) {
      next()
      return
    }
    this.search.filters = {}
    this.$store.dispatch('searchMaterials', this.search).finally(next)
  },
  methods: {
    initialSearch(search) {
      this.search = search;
      this.executeSearch(true)
    },
    executeSearch(updateUrl) {

      if (this.$route.params.filterId) {
        const category = this.$store.getters.getCategoryById(
          this.$route.params.filterId,
          this.$route.meta.filterRoot
        )
        if (category) {
          this.search = addFilter(
            this.search,
            category.searchId,
            this.$route.params.filterId
          )
          this.search = category.children.reduce((search, child) => {
            return addFilter(search, child.searchId, child.external_id)
          }, this.search)
        }
      }
      console.log(this.search)
      this.$store.dispatch('searchMaterials', this.search)
      if (updateUrl) {
        this.$router.push(
          generateSearchMaterialsQuery(this.search, this.$route.name)
        )
      }
    },
    onSearch() {
      this.search = {
        search_text: this.search.search_text,
        filters: {},
        page_size: 10,
        page: 1,
      }
      this.executeSearch(true)
    },
    loadMore() {
      const { search, materials } = this
      if (materials && search) {
        const { page_size, page, records_total } = materials

        if (records_total > page_size * page) {
          this.$store.dispatch('searchNextPageMaterials', {
            ...search,
            page: page + 1,
          })
        }
      }
    },      /*         Change 1 item in line to 3 and back       */
    changeViewType() {
      if (this.materials_in_line === 1) {
        this.$store.dispatch('searchMaterialsInLine', 3)
      } else {
        this.$store.dispatch('searchMaterialsInLine', 1)
      }
    },     /*         Event the ordering item       */
    changeOrdering() {
      const { sort_order } = this
      if (sort_order === 'date_descending') {
        this.search.ordering = '-publisher_date'
      } else if (sort_order === 'date_ascending') {
        this.search.ordering = 'publisher_date'
      } else {
        this.search.ordering = ''
      }
      this.search.page = 1
      this.executeSearch(true)
    },
    loadFilterCategories() {
      if (this.$route.name.startsWith('mat')) {
        return Promise.resolve(null)
      }
      return this.$store.dispatch('getFilterCategories')
    },
  },
}
</script>

<style lang="less" scoped>
@import "./../variables";
.search {
  position: relative;

  &__info {
    padding: 97px 0 0;
    margin-bottom: 60px;
    position: relative;
    min-height: 300px;

    @media @mobile {
      overflow: hidden;
    }
    &_top {
      border-radius: 20px;
      background: fade(@light-grey, 90%);
      padding: 65px 576px 95px 46px;
      min-height: 274px;
      margin: 0 0 -68px;
      position: relative;

      @media @mobile {
        padding: initial;
        margin: -20px -20px -165px -20px;
        padding-top: 20px;
        padding-left: 20px;

        h2 {
          font-size: 24px;
          width: 330px;
        }
      }

      @media @tablet {
        padding: 65px 46px 95px 46px;
        h2 {
          font-size: 28px;
        }
      }
    }

    &_bg {
      position: absolute;
      right: 26px;
      top: -62px;
      width: 50%;
      border-radius: 21px;

      @media @mobile {
        display: none;
      }
    }

    &_search {
      margin: auto;
      margin-top: 15px;

      @media @mobile {
        width: 100%;
        margin-bottom: 20px;
        background-color: #ffffff;
        border-radius: 20px;
        box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
      }
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
      background: fade(@green, 90%);
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
    @media @desktop {
      display: flex;
    }
    @media @mobile {
      margin-bottom: 60px;
    }
    position: relative;
  }

  &__tools {
    width: 100%;
    justify-content: flex-end;
    display: flex;
    margin-bottom: -30px;
    position: relative;
    z-index: 1;

    @media @mobile {
      justify-content: flex-start;
    }

    &_results {
      width: 485px;
    }

    &_dates {
      width: 251px;
    }

    &_type_button {
      border-radius: 0;
      border: 0;
      color: @green;
      font-family: @second-font;
      font-size: 16px;
      font-weight: bold;
      height: 50px;
      padding: 0 8px 0 40px;
      margin: 0 0 0 31px;
      cursor: pointer;

      &--cards {
        background: transparent url("/images/card-view-copy.svg") 0 50%
          no-repeat;
      }

      &--list {
        background: transparent url("/images/list-view-copy.svg") 0 50%
          no-repeat;
      }

      &:focus,
      &:active {
        outline: none;
      }

      @media @mobile {
        display: none;
      }
    }

    .select {
      height: 50px;
      width: 251px;
      @media @mobile {
        width: 100%;
      }
    }
  }

  &__filter {
    width: 250px;
    flex-shrink: 0;
    margin: 0 64px 0 0;

    @media @mobile {
      width: 100%;
      max-width: 400px;
      margin: 0;
    }

    &_content {
      width: 100%;
      padding-top: 80px;
      padding-bottom: 102px;

      @media @mobile {
        padding-top: 60px;
        padding-bottom: 40px;
      }
    }
  }

  &__materials {
    position: relative;
    flex: 1 1 auto;
    padding: 60px 0 0;
    width: 100%;

    @media @mobile {
      padding: 0;
    }
  }

  label {
    line-height: 50px;
    margin-right: 10px;
  }
  &__select {
    position: relative;
    overflow: hidden;
    border-radius: 0;
    background: transparent;
    box-sizing: border-box;
    height: 67px;
    cursor: pointer;
    z-index: 4;

    &--wrap {
      overflow: inherit;
    }

    &::-ms-expand {
      display: none;
    }

    &:before {
      content: "";
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translate(0, -100%) rotate(90deg);
      width: 14px;
      height: 14px;
      background: url("/images/arrow-text-grey.svg") 50% 50% / contain no-repeat;
      pointer-events: none;
    }

    select {
      width: 100%;
      height: 50px;
      font-family: @main-font;
      font-size: 16px;
      font-weight: normal;
      font-style: normal;
      font-stretch: normal;
      line-height: 1.5;
      background-color: transparent;
      background-image: none;
      -moz-appearance: none;
      appearance: none;
      box-shadow: none;
      display: block;
      color: @dark-grey;
      border-radius: 5px;
      border: solid 1px rgba(0, 0, 0, 0.12);
      padding: 0 40px 0 10px;
      cursor: pointer;
      box-sizing: border-box;

      &::-ms-expand {
        display: none;
      }
      &::-ms-value {
        background: transparent;
        color: @dark-grey;
      }
      &:-moz-focusring {
        color: transparent;
        text-shadow: 0 0 0 #000;
      }

      &--focused &,
      &:active,
      &:focus {
        outline: none;
      }
    }

    &--not-choose select {
      color: rgba(0, 0, 0, 0.38);
    }
  }
}
</style>
