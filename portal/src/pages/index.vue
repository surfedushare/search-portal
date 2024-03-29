<template>
  <section class="edusources-container main" :class="{ 'new-header': isNewHeader }">
    <div>
      <div class="main__info">
        <div class="center_block center-header">
          <img class="main__info_bg" src="../assets/images/pictures/header-image.jpg" alt="header-image" />
          <div class="main__info_block">
            <div class="bg" />
            <h2 class="main__info_title">
              <span v-if="statistic">{{ numberOfMaterials }}</span>
              {{ headline }}
            </h2>
            <ul class="main__info_items">
              <li class="main__info_item">{{ $t("Free-to-use") }}</li>
              <li class="main__info_item">{{ $t("Judged-by-quality") }}</li>
              <li class="main__info_item">
                {{ $t("Inspiration-in-your-field") }}
              </li>
            </ul>
          </div>
          <SearchBar enable-pre-filters @search="searchMaterials" />
        </div>
      </div>

      <div class="main__materials">
        <div class="center_block">
          <h2 class="main__materials_title">
            {{ $t("Newest-open-learning-material") }}
          </h2>
          <MaterialCards :materials="materials"></MaterialCards>
        </div>
      </div>

      <div class="center_block main__thems_and_communities">
        <PopularList :communities="allCommunities()" class="main__communities">
          <template slot="header-info">
            <h2>{{ $t("Communities") }}</h2>
            <div class="popular-list__description">
              {{ $t("Open-learning-materials-from-professional-communit") }}
            </div>
          </template>
        </PopularList>
      </div>

      <div class="center_block">
        <section class="preview">
          <div class="preview__bg_block">
            <img src="../assets/images/pictures/hoe-werkt-het.png" class="preview__bg_block-img" />
          </div>
          <div class="preview__text_block">
            <h2 class="preview__title">{{ $t("How-does-it-work-title") }}</h2>
            <div class="preview__text html-content" v-html="getHowDoesItWork" />
            <router-link :to="localePath('how-does-it-work')" class="button">{{ $t("How-does-it-work") }}</router-link>
          </div>
        </section>
      </div>
    </div>
  </section>
</template>

<script>
import numeral from "numeral";
import { mapGetters } from "vuex";
import PopularList from "~/components/Communities/PopularList";
import SearchBar from "~/components/Search/SearchBar.vue";
import { generateSearchMaterialsQuery } from "~/components/_helpers";
import PageMixin from "~/pages/page-mixin";
import DOMPurify from "dompurify";
import { isEmpty } from "lodash";
import MaterialCards from "~/components/Materials/MaterialCards.vue";

const EDUCATIONAL_LEVEL_CATEGORY_ID = "lom_educational_levels";

export default {
  components: {
    PopularList,
    SearchBar,
    MaterialCards,
  },
  mixins: [PageMixin],
  data() {
    const headlineTranslationKeyPostfix = this.$root.isMBOEnvironment() ? "education" : "higher-education";
    return {
      filters: {},
      headline: this.$i18n.t(`open-learning-materials-from-${headlineTranslationKeyPostfix}`),
    };
  },
  computed: {
    ...mapGetters({
      filterCategories: "filter_categories",
      materials: "materials",
      allCommunities: "allCommunities",
      statistic: "statistic",
      isNewHeader: "isNewHeader",
    }),
    numberOfMaterials() {
      return numeral(this.statistic.value).format("0,0").replace(",", ".");
    },
    educationalLevelOptions() {
      return this.getFilterOptions(EDUCATIONAL_LEVEL_CATEGORY_ID);
    },
    getHowDoesItWork() {
      const footerInfo = this.$i18n.t("html-How-does-it-work-text");
      return DOMPurify.sanitize(footerInfo);
    },
  },
  mounted() {
    this.$store.dispatch("getCommunities", { params: { page_size: 3 } });
    this.$store.dispatch("getStatistic");
    this.$store.dispatch("getFilterCategories");
    this.$store.dispatch("getMaterials", { page_size: 4 });
  },
  methods: {
    getFilterOptions(external_id) {
      if (this.filterCategories) {
        const filterCategory = this.filterCategories.find((category) => category.external_id === external_id);

        if (filterCategory) {
          return {
            name: filterCategory.title_translations[this.$i18n.locale],
            options: filterCategory.children,
          };
        }
      }

      return null;
    },
    setEducationalLevelFilter(value) {
      this.filters[EDUCATIONAL_LEVEL_CATEGORY_ID] = [value];
    },
    searchMaterials(searchText) {
      const searchData = {
        search_text: searchText,
        filters: this.$store.state.filterCategories.selection,
        page_size: 10,
        page: 1,
      };
      const searchRoute = generateSearchMaterialsQuery(
        searchData,
        "materials-search",
        !isEmpty(this.$store.state.filterCategories.selection)
      );
      this.$router.push(searchRoute);
    },
  },
};
</script>

<style lang="less">
@import "./../variables";
.materials {
  list-style: none;
}
.main {
  position: relative;
  z-index: 1;

  &__info {
    padding: 120px 0 0;
    margin-bottom: 60px;
    position: relative;
    margin-top: 70px;
    @media @mobile-ls {
      padding: 230px 0 0;
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
      background: url("../assets/images/check-white.svg") 0 0 no-repeat;

      @media @mobile {
        background-size: 20px 20px;
        background-position-x: 10px;
      }
    }
    &_block {
      position: absolute;
      top: 30px;
      right: 100px;
      color: #fff;
      max-width: 550px;
      font-family: @second-font;
      padding: 31px 48px 40px;
      font-size: 16px;
      font-weight: bold;
      z-index: 1;
      @media @wide {
        top: 50px;
        right: 470px;
        max-width: 550px;
      }
      @media @desktop {
        top: 50px;
        right: 170px;
        max-width: 550px;
      }
      @media @tablet {
        right: 20px;
        padding: 5px 32px;
        max-width: 400px;
      }
      @media @mobile {
        top: 30px;
        right: 20px;
        padding: 5px 32px;
        max-width: 300px;
      }
      @media @mobile-ls {
        top: 50px;
        right: 20px;
        padding: 5px 32px;
        max-width: 300px;
        min-height: 300px;
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
          background: url("../assets/images/bubble-background-green.svg") 0 0 no-repeat;
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
    display: flex;
    position: relative;
    padding: 50px 0 0 0px;

    &__bg_block {
      position: absolute;

      @media @wide {
        top: -2px;
      }

      @media @desktop {
        top: -2px;
      }

      @media @tablet {
        display: none;
      }

      @media @mobile {
        display: none;
      }

      img {
        width: 275px;
        border-radius: 21px;
      }

      &:before {
        display: flex;
        content: "";
        position: absolute;
        background: url("../assets/images/combined-shape.svg") no-repeat 0 0;
        right: -100px;
        top: 0;
        height: 109px;
        width: 119px;
      }
      &:after {
        content: "";
        position: absolute;
        background: url("../assets/images/message.svg") no-repeat 0 0;
        right: -82px;
        top: 22px;
        height: 33px;
        width: 35px;
      }
    }

    &__text_block {
      background: fade(@light-grey, 90%);
      margin-left: 100px;
      border-radius: 20px;

      @media @wide {
        padding: 30px 30px 30px 270px;
      }

      @media @desktop {
        padding: 30px 30px 30px 270px;
      }

      @media @tablet {
        padding: 30px 30px 30px 70px;
        margin-left: 0px;
      }
    }

    &__title {
      margin: 0 0 40px;
      @media @mobile {
        font-size: 22px;
      }
    }
  }
}
</style>
