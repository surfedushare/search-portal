<template>
  <section class="main__info_search">
    <PreFilterSearch class="main__info_search__domain" @update:filter="onUpdateFilter" />
    <SearchTerm class="main__info_search__term" @onSearch="searchMaterials" />
  </section>
</template>

<script>
import PreFilterSearch from '@/components/Search/PreFilterSearch'
import SearchTerm from '@/components/Search/SearchTerm'
import { isNull } from 'lodash'
import numeral from 'numeral'
import { mapGetters } from 'vuex'

export default {
  name: 'SearchBar',
  components: {
    SearchTerm,
    PreFilterSearch
  },
  data() {
    return {
      searchText: '',
      filters: {},
    }
  },
  computed: {
    ...mapGetters({
      filterCategories: 'filter_categories',
      materials: 'materials',
      allCommunities: 'allCommunities',
      statistic: 'statistic',
    }),
    numberOfMaterials() {
      return numeral(this.statistic.value).format('0,0').replace(',', '.')
    },
  },
  methods: {
    getFilterOptions(external_id) {
      if (this.filterCategories) {
        const filterCategory = this.filterCategories.find(
          (category) => category.external_id === external_id
        )

        if (filterCategory) {
          return {
            name: filterCategory.title_translations[this.$i18n.locale],
            options: filterCategory.children,
          }
        }
      }

      return null
    },
    searchMaterials(searchText) {
      const searchRequest = {
        search_text: searchText || '',
        filters: this.filters,
        page_size: 10,
        page: 1,
      }
      this.$emit('onSearch', searchRequest)
    },
    onUpdateFilter(filter) {
      if (isNull(filter.selection)) {
        delete this.filters[filter.field]
        return
      }
      this.filters[filter.field] = filter.selection
    },

  },
}
</script>

<style lang="less">
@import "../../variables";
.main {
  position: relative;
  z-index: 1;

  &__info {
    padding: 120px 0 0;
    margin-bottom: 60px;
    position: relative;

    .center-header {
      position: relative;
    }

    &_bg {
      width: 100%;
    }

    &_title {
      line-height: 1.25;
      color: #fff;
      margin: 0 0 16px;
      @media @mobile {
        font-size: 16px;
      }
    }

    &_main-title {
      opacity: 0;
      @media @mobile {
        display: none;
      }
    }
    &_items {
      padding: 0;
      margin: 0;
      @media @mobile {
        font-size: 12px;
      }
    }
    &_item {
      margin: 0;
      list-style: none;
      padding: 5px 0 8px 40px;
      background: url("/images/check-white.svg") 0 0 no-repeat;

      @media @mobile {
        background-size: 20px 20px;
        background-position-x: 10px;
      }
    }
    &_block {
      position: absolute;
      top: -50px;
      right: 100px;
      color: #fff;
      width: auto;
      max-width: 550px;
      font-family: @second-font;
      padding: 31px 48px 40px;
      font-size: 16px;
      font-weight: bold;
      z-index: 1;

      @media @mobile {
        top: -90px;
        right: 20px;
        padding: 5px 32px;
        max-width: 300px;
      }

      & .bg {
        background: @green;
        opacity: 0.9;
        position: absolute;
        border-radius: 0 20px 20px 20px;
        height: 100%;
        left: 0;
        top: 0;
        width: 100%;
        z-index: -1;
        @media @mobile {
          right: 10px;
          left: 10px;
          width: auto;
        }
        &:before {
          content: "";
          background: url("/images/bubble-background-green.svg") 0 0 no-repeat;
          position: absolute;
          top: -36px;
          left: -46px;
          width: 63px;
          height: 58px;

          @media @tablet, @mobile {
            left: -24px;
            top: -19px;
            height: 30px;
          }
        }
      }
    }

    &_search {
      position: relative;
      display: flex;
      justify-content: space-between;
      z-index: 10;
      background: white;
      height: 92px;
      border-radius: 20px;
      box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
      margin-top: -18px;

      &__term {
        display: flex;
      }

      &__domain {
        display: flex;
        justify-content: space-between;
        margin-left: 1rem;
        margin-top: 1rem;
      }
    }
  }

  &__thems_and_communities {
    margin-bottom: 50px;
    @media @desktop {
      display: flex;
      margin-bottom: 97px;
    }
    align-items: start;
    justify-content: space-between;
  }

  &__thems {
    @media @desktop {
      width: 700px;
    }
  }

  &__communities {
    @media @desktop {
      width: 485px;
      padding: 0 86px 0 0;
    }
  }

  &__materials {
    position: relative;
    margin: 0 0 40px;

    &_title {
      margin: 0 0 32px;

      @media @mobile {
        font-size: 22px;
        margin: 0 0 20px;
      }
    }
  }

  .preview {
    position: relative;
    @media @desktop {
      padding: 50px 0 0 100px;
    }

    &__bg_block {
      position: absolute;
      top: -80px;
      left: 0;

      @media @desktop {
        top: -2px;
      }

      @media @mobile {
        display: none;
      }

      img {
        width: 275px;
        border-radius: 21px;
      }

      &:before {
        content: "";
        position: absolute;
        background: url("/images/combined-shape.svg") no-repeat 0 0;
        right: -100px;
        top: 0;
        height: 109px;
        width: 119px;
      }
      &:after {
        content: "";
        position: absolute;
        background: url("/images/message.svg") no-repeat 0 0;
        right: -82px;
        top: 22px;
        height: 33px;
        width: 35px;
      }
    }

    &__text_block {
      background: fade(@light-grey, 90%);
      border-radius: 20px;
      margin: 0 0 80px;
      padding: 20px;

      @media @desktop {
        padding: 30px 30px 30px 270px;
      }
    }

    &__title {
      margin: 0 0 20px;
      @media @mobile {
        font-size: 22px;
      }
    }
  }
}
</style>
