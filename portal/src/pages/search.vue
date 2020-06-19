<template>
  <section class="container search">
    <div>
      <div class="search__info">
        <div class="center_block center-header">
          <div class="search__info_top">
            <BreadCrumbs :items="items" />
            <h2 v-if="materials && !materials_loading">
              {{ $t('Search-results') }} {{ `(${materials.records_total})` }}
            </h2>
            <img
              src="/images/pictures/rawpixel-760027-unsplash.jpg"
              srcset="
                /images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
                /images/pictures/rawpixel-760027-unsplash@3x.jpg 3x
              "
              class="search__info_bg"
            />
          </div>
          <Search v-if="search" v-model="search" class="search__info_search" />
        </div>
      </div>

      <div class="search__tools center_block">
        <label for="search_order_select">{{ $t('sort_by') }}: &nbsp;</label>
        <div class="search__chooser search__select">
          <select
            id="search_order_select"
            v-model="sort_order"
            @change="changeOrdering"
          >
            <option
              v-for="option in sort_order_options"
              :key="option.value"
              :value="option.value"
            >
              &nbsp;&nbsp;{{ $t(option.value) }}
            </option>
          </select>
        </div>
        <button
          :class="{
            'search__tools_type_button--list': materials_in_line === 3,
            'search__tools_type_button--cards': materials_in_line === 1
          }"
          class="search__tools_type_button"
          @click.prevent="changeViewType"
        >
          {{ materials_in_line === 1 ? $t('Card-view') : $t('List-view') }}
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
            <FilterCategories v-model="search" />
          </div>
        </div>

        <div class="search__materials">
          <Materials
            :materials="materials"
            :items-in-line="materials_in_line"
          />
          <Spinner v-if="materials_loading" />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'
import Search from '~/components/FilterCategories/Search'
import FilterCategories from '~/components/FilterCategories'
import Materials from '~/components/Materials'
import Spinner from '~/components/Spinner'
import BreadCrumbs from '~/components/BreadCrumbs'
import {
  generateSearchMaterialsQuery,
  parseSearchMaterialsQuery
} from '~/components/_helpers'

export default {
  components: {
    Search,
    FilterCategories,
    Materials,
    Spinner,
    BreadCrumbs
  },
  data() {
    return {
      search: {},
      isShow: false,
      publisherdate: 'lom.lifecycle.contribute.publisherdate',
      dates_range: {
        start_date: null,
        end_date: null
      },
      formData: {
        name: null
      },
      items: [{ title: this.$t('Home'), url: this.localePath('index') }],
      sort_order: 'relevance',
      sort_order_options: [
        { value: 'relevance' },
        { value: 'date_descending' },
        { value: 'date_ascending' }
      ]
    }
  },
  computed: {
    ...mapGetters(['materials', 'materials_loading', 'materials_in_line'])
  },
  watch: {
    search(search) {
      if (search && !this.materials_loading) {
        this.$store.dispatch('searchMaterials', search)
      }
    },
    dates_range(dates) {
      const { filters } = this.search
      let new_filters = filters ? filters.slice(0) : []
      const current_dates = new_filters.find(
        item => item.external_id === this.publisherdate
      )
      const index = current_dates
        ? new_filters.indexOf(current_dates)
        : new_filters.length

      new_filters[index] = {
        external_id: this.publisherdate,
        items: [dates.start_date || null, dates.end_date || null]
      }

      this.search = Object.assign({}, this.search, { filters: new_filters })
    }
  },
  mounted() {
    const urlInfo = parseSearchMaterialsQuery(this.$route.query)
    this.dates_range = urlInfo.dateRange
    this.search = urlInfo.search
    this.$store.dispatch('searchMaterials', urlInfo.search)
  },
  methods: {
    generateSearchMaterialsQuery,
    loadMore() {
      const { search, materials } = this
      if (materials && search) {
        const { page_size, page, records_total } = materials

        if (records_total > page_size * page) {
          this.$store.dispatch('searchNextPageMaterials', {
            ...search,
            page: page + 1
          })
        }
      }
    },
    /**
     * Change 1 item in line to 3 and back.
     */
    changeViewType() {
      if (this.materials_in_line === 1) {
        this.$store.dispatch('searchMaterialsInLine', 3)
      } else {
        this.$store.dispatch('searchMaterialsInLine', 1)
      }
    },
    /**
     * Event the ordering items
     */
    changeOrdering() {
      const { sort_order } = this
      if (sort_order === 'date_descending') {
        this.search.ordering = '-lom.lifecycle.contribute.publisherdate'
      } else if (sort_order === 'date_ascending') {
        this.search.ordering = 'lom.lifecycle.contribute.publisherdate'
      } else {
        this.search.ordering = ''
      }
      this.search.page = 1
      this.$store.dispatch('searchMaterials', Object.assign({}, this.search))
      this.$router.push(this.generateSearchMaterialsQuery(this.search))
    }
  }
}
</script>

<style lang="less" scoped>
@import './../variables';
.search {
  position: relative;

  &__info {
    padding: 97px 0 0;
    margin-bottom: 82px;
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
        margin: -20px -20px -100px -20px;
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
      top: -45px;
      width: 50%;
      border-radius: 21px;
      @media @mobile {
        z-index: -1;
        right: -20px;
      }
      @media @mobile {
        right: -50px;
      }
    }

    &_search {
      margin: auto;
      margin-top: 15px;

      @media @mobile {
        width: 100%;
        margin-bottom: 20px;
        background-color: #ffffff;
        border-radius: 10px;
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
    @media @desktop {
      display: flex;
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

    &_dates {
      width: 251px;
    }

    &_type_button {
      border-radius: 0;
      border: 0;
      color: @dark-blue;
      font-family: @second-font;
      font-size: 16px;
      font-weight: bold;
      height: 50px;
      padding: 0 8px 0 40px;
      margin: 0 0 0 31px;
      cursor: pointer;

      &--cards {
        background: transparent url('/images/card-view-copy.svg') 0 50%
          no-repeat;
      }

      &--list {
        background: transparent url('/images/list-view-copy.svg') 0 50%
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
      margin: 0;
    }

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
    width: 100%;

    @media @mobile {
      padding: 0;
    }
  }

  label {
    line-height: 50px;
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
      content: '';
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translate(0, -100%) rotate(90deg);
      width: 14px;
      height: 14px;
      background: url('/images/arrow-text-grey.svg') 50% 50% / contain no-repeat;
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
      margin: 0;
      padding: 0 40px 0 0;
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
