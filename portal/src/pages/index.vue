<template>
  <section class="container main">
    <div>
      <div class="main__info">
        <div class="center_block center-header">
          <img class="main__info_bg" src="/images/pictures/header-image.jpg" alt="header-image" />
          <div class="main__info_block">
            <div class="bg" />
            <h2 class="main__info_title">
              <span v-if="statistic">{{ numberOfMaterials }}</span>
              {{ $t('open-learning-materials-from-higher-education') }}
            </h2>
            <ul class="main__info_items">
              <li class="main__info_item">{{ $t('Free-to-use') }}</li>
              <li class="main__info_item">{{ $t('Judged-by-quality') }}</li>
              <li class="main__info_item">{{ $t('Inspiration-in-your-field') }}</li>
            </ul>
          </div>
          <SearchBar v-if="$root.isDemoEnvironment()" @onSearch="searchMaterials" />
          <Search
            v-if="!$root.isDemoEnvironment()"
            :select-options="educationalLevelOptions"
            @onSearch="searchMaterials"
            @selectDropdownOption="setEducationalLevelFilter"
          />
        </div>
      </div>

      <div class="main__materials">
        <div class="center_block">
          <h2 class="main__materials_title">{{ $t('Newest-open-learning-material') }}</h2>
          <Materials :materials="materials" />
        </div>
      </div>

      <div class="center_block main__thems_and_communities">
        <PopularList :communities="allCommunities()" class="main__communities">
          <template slot="header-info">
            <h2>{{ $t('Communities') }}</h2>
            <div
              class="popular-list__description"
            >{{ $t('Open-learning-materials-from-professional-communit') }}</div>
          </template>
        </PopularList>
      </div>

      <div class="center_block">
        <section class="preview">
          <div class="preview__bg_block">
            <img src="/images/pictures/hoe-werkt-het.png" class="preview__bg_block-img" />
          </div>
          <div class="preview__text_block">
            <h2 class="preview__title">{{ $t('How-does-it-work-title') }}</h2>
            <!-- eslint-disable vue/no-v-html -->
            <div class="preview__text html-content" v-html="$t('html-How-does-it-work-text')" />
            <!-- eslint-enable vue/no-v-html -->
            <router-link
              :to="localePath('how-does-it-work')"
              class="button"
            >{{ $t('How-does-it-work') }}</router-link>
          </div>
        </section>
      </div>
    </div>
  </section>
</template>

<script>
import { isNull } from 'lodash'
import numeral from 'numeral'
import { mapGetters } from 'vuex'
import PopularList from '~/components/Communities/PopularList'
import Materials from '~/components/Materials'
import Search from '~/components/Search'
import SearchBar from '~/components/Search/SearchBar.vue'
import { generateSearchMaterialsQuery } from '~/components/_helpers'
import PageMixin from '~/pages/page-mixin'

const EDUCATIONAL_LEVEL_CATEGORY_ID = 'lom_educational_levels'

export default {
  components: {
    Search,
    PopularList,
    Materials,
    SearchBar
  },
  mixins: [PageMixin],
  data() {
    return {
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
    educationalLevelOptions() {
      return this.getFilterOptions(EDUCATIONAL_LEVEL_CATEGORY_ID)
    },
  },
  mounted() {
    this.$store.dispatch('getMaterials', { page_size: 4 })
    this.$store.dispatch('getCommunities', { params: { page_size: 3 } })
    this.$store.dispatch('getStatistic')
    this.$store.dispatch('getFilterCategories')
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
    setEducationalLevelFilter(value) {
      this.filters[EDUCATIONAL_LEVEL_CATEGORY_ID] = [value]
    },
    searchMaterials(search) {
      this.$router.push(
        generateSearchMaterialsQuery({
          search_text: this.$root.isDemoEnvironment() ? search.search_text : search,
          filters: this.filters,
          page_size: 10,
          page: 1,
        })
      )
    },
    onUpdateFilter(filter) {
      if (isNull(filter.value)) {
        delete this.filters[filter.field]
        return
      }
      this.filters[filter.field] = filter.values
    },
  },
}
</script>

<style lang="less">
@import "./../variables";
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
