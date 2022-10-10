<template>
  <section class="edusources-container search">
    <div>
      <div class="search__info">
        <div class="search__background"></div>
        <div class="center_block center-header">
          <SearchBar @search="onSearch" />
        </div>
        <FilterCategoriesSelection :key="JSON.stringify(search.filters)" :materials="materials" @filter="onFilter" />
      </div>

      <div class="search__container">
        <div><!-- filler --></div>
        <FilterCategories v-if="materials" :materials="materials" @filter="onFilter" />
        <div class="search__tools">
          <div ref="top" class="search__tools_top" />
          <h2 class="search__tools_results">
            {{ $t("Search-results") }}
            <span v-if="materials && !materials_loading">{{ `(${materials.records_total})` }}</span>
          </h2>
          <v-btn v-if="showShareButton" outlined x-large class="secondary" @click="toggleShareSearchPopup">
            <v-icon left dark>fa-share</v-icon> {{ $t('share') }}
          </v-btn>
        </div>

        <div class="search__materials">
          <Spinner v-if="materials_loading" class="spinner" />
          <v-row v-if="materials && materials.records" class="mb-8" data-test="search_results">
            <v-col v-for="material in materials.records" :key="material.id" class="mb-4" cols="12">
              <MaterialListCard
                v-if="$vuetify.breakpoint.name !== 'xs'"
                :material="material"
                :handle-material-click="handleMaterialClick"
              />
              <MaterialCard v-else :material="material" :handle-material-click="handleMaterialClick" />
            </v-col>
          </v-row>

          <v-pagination
            v-if="
              !materials_loading && materials && materials.records && materials.records.length && materials.total_pages
            "
            v-model="materials.page"
            :length="materials.total_pages"
            :total-visible="11"
            @input="onLoadPage"
          >
          </v-pagination>
        </div>
      </div>
    </div>
    <ShareSearchPopup
      :key="$i18n.locale"
      :show-popup="showShareSearchPopup"
      :close="toggleShareSearchPopup"
      :share-url="shareUrl"
    />
  </section>
</template>

<script>
import { mapGetters } from "vuex";
import FilterCategories from "~/components/FilterCategories/FilterCategories.vue";
import FilterCategoriesSelection from "~/components/FilterCategories/FilterCategoriesSelection.vue";
import MaterialCard from "~/components/Materials/MaterialCard.vue";
import MaterialListCard from "~/components/Materials/MaterialListCard.vue";
import SearchBar from "~/components/Search/SearchBar.vue";
import Spinner from "~/components/Spinner";
import { generateSearchMaterialsQuery, parseSearchMaterialsQuery } from "~/components/_helpers";
import PageMixin from "~/pages/page-mixin";
import ShareSearchPopup from "~/components/Popup/ShareSearchPopup";

export default {
  components: {
    FilterCategories,
    FilterCategoriesSelection,
    MaterialListCard,
    MaterialCard,
    Spinner,
    SearchBar,
    ShareSearchPopup,
  },
  mixins: [PageMixin],
  dependencies: ["$log", "$window"],
  beforeRouteLeave(to, from, next) {
    if(to.name.indexOf("___" + this.$i18n.locale) >= 0) {
      this.$store.commit("RESET_FILTER_CATEGORIES_SELECTION");
    }
    next();
  },
  data() {
    // Set filters from the URL parameters
    const urlInfo = parseSearchMaterialsQuery(this.$route.query);
    this.$store.commit("RESET_FILTER_CATEGORIES_SELECTION", urlInfo.search.filters);
    // Set filters from the router parameters (Community and Theme filters)
    if (this.$route.params.filterId) {
      this.$store.commit("SELECT_FILTER_CATEGORIES", {
        category: this.$route.meta.filterRoot,
        selection: [this.$route.params.filterId],
      });
    }
    // Update the filters
    urlInfo.search.filters = this.$store.state.filterCategories.selection;
    // Set other data than filters and return the object
    const languagePrefix = (this.$i18n.locale === "en") ? "/en" : "";
    return {
      search: urlInfo.search,
      formData: {
        name: null,
      },
      showShareSearchPopup: false,
      shareUrl: `https://${this.$window.location.host}${languagePrefix}/widget/${this.$window.location.search}`
    };
  },
  computed: {
    ...mapGetters(["materials", "materials_loading", "did_you_mean"]),
    showFilterCategories() {
      return this.isReady && this.materials && this.materials.records;
    },
    showShareButton() {
      return this.$root.isDemoEnvironment() && this.materials?.records.length;
    }
  },
  updated() {
    if (this.$vuetify.breakpoint.name === "xs") {
      this.$refs.top.scrollIntoView({ behavior: "smooth" });
    }
    const languagePrefix = (this.$i18n.locale === "en") ? "/en" : "";
    this.shareUrl =
      `https://${this.$window.location.host}${languagePrefix}/widget/${this.$window.location.search}`;
  },
  mounted() {
    this.loadFilterCategories().finally(() => {
      this.executeSearch();
    });
  },
  methods: {
    onSearch(searchText) {
      searchText = searchText || "";
      const changed = searchText !== this.search.search_text;
      this.search.search_text = searchText;
      this.executeSearch(changed);
    },
    executeSearch(updateUrl) {
      this.$store.dispatch("searchMaterials", this.search).then((results) => {
        this.$log.siteSearch(this.$route.query, results.records_total);
      });

      if (updateUrl) {
        this.$router.push(generateSearchMaterialsQuery(this.search, this.$route.name));
      }
    },
    onFilter() {
      this.search = {
        search_text: this.search.search_text,
        filters: this.$store.state.filterCategories.selection,
        page_size: 10,
        page: 1,
      };
      this.executeSearch(true);
    },
    onLoadPage(page) {
      const { search, materials } = this;
      if (materials && search) {
        search.page = page;
        this.$router.push(generateSearchMaterialsQuery(this.search, this.$route.name));
        this.$store.dispatch("searchMaterials", search);
      }
    },
    loadFilterCategories() {
      if (this.$route.name.startsWith("mat")) {
        return Promise.resolve(null);
      }
      return this.$store.dispatch("getFilterCategories");
    },
    handleMaterialClick(material) {
      if (this.selectFor === "add") {
        this.$store.commit("SET_MATERIAL", material);
      } else {
        this.$router.push(
          this.localePath({
            name: "materials-id",
            params: { id: material.external_id },
          })
        );
      }
      this.$emit("click", material);
    },
    toggleShareSearchPopup() {
      this.showShareSearchPopup = !this.showShareSearchPopup;
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../variables";

.filter-categories {
  width: -webkit-fill-available;
}

.spinner {
  position: absolute;
  margin-left: 40%;
}
.search {
  position: relative;
  &__background {
    background-color: @green;
    margin-top: -98px;
    height: 61px;
  }
  &__info {
    padding: 97px 0 0;
    margin-bottom: 20px;
    position: relative;

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

  &__container {
    display: grid;
    grid-auto-flow: column;
    grid-template-rows: auto auto;
    grid-template-columns: minmax(200px, 275px) auto;
    margin: 0 auto;
    max-width: 1296px;
    padding: 0 25px;
    @media @mobile {
      display: flex;
      justify-content: flex-start;
      flex-wrap: wrap;
    }
  }

  &__tools {
    display: grid;
    grid-auto-flow: column;
    grid-template-rows: auto;
    position: relative;
    z-index: 1;
    justify-content: space-between;

    @media @mobile {
      display: flex;
      justify-content: flex-start;
      flex-wrap: wrap;
    }

    &_top {
      position: absolute;
      top: -75px;
      left: 0;
    }
    &_results {
      margin-left: 50px;
      @media @mobile {
        display: flex;
        margin-left: 0px;
        font-size: 28px;
        column-gap: 10px;
      }
      @media @tablet {
        margin-left: 20px;
        min-width: 520px;
      }
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
        background: transparent url("../assets/images/card-view-copy.svg") 0 50% no-repeat;
      }

      &--list {
        background: transparent url("../assets/images/list-view-copy.svg") 0 50% no-repeat;
      }

      &:focus,
      &:active {
        outline: none;
      }

      @media @tablet {
        display: none;
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

  &__materials {
    position: relative;
    padding-left: 25px;
    margin-top: 25px;

    @media @wide {
      width: auto;
    }

    @media @tablet {
      max-width: 540px;
    }

    @media @mobile {
      padding: 0;
      max-width: 340px;
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
      background: url("../assets/images/arrow-text-grey.svg") 50% 50% / contain no-repeat;
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
