<template>
  <section class="edusources-container search">
    <div>
      <div class="search__info">
        <div class="center_block center-header">
          <img
            class="main__info_bg"
            src="../assets/images/pictures/header-image.jpg"
            alt="header-image"
          />
          <SearchBar @search="onSearch" />
          <div ref="top"></div>
        </div>
        <FilterCategoriesSelection
          v-if="materials"
          :key="JSON.stringify(search.filters)"
          :materials="materials"
          @filter="onFilter"
        />
      </div>
      <div class="search__container">
        <div><!-- filler --></div>
        <FilterCategories
          v-if="materials"
          :materials="materials"
          @filter="onFilter"
        />
        <div class="search__tools">
          <h2
            v-if="materials && !materials_loading"
            class="search__tools_results"
          >
            {{ $t("Search-results") }} {{ `(${materials.records_total})` }}
          </h2>
          <label for="search_order_select">{{ $t("sort_by") }}: &nbsp;</label>
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
              'search__tools_type_button--cards': materials_in_line === 1,
            }"
            class="search__tools_type_button"
            @click.prevent="changeViewType"
          >
            {{ materials_in_line === 1 ? $t("Card-view") : $t("List-view") }}
          </button>
        </div>
        <div class="search__materials">
          <Materials :materials="materials" :items-in-line="materials_in_line" :did-you-mean="did_you_mean"
            :search-term="search.search_text" />
          <v-pagination
            v-if="
              !materials_loading &&
              materials &&
              materials.records &&
              materials.records.length &&
              materials.total_pages
            "
            v-model="materials.page"
            :length="materials.total_pages"
            :total-visible="11"
            @input="onLoadPage"
          >
          </v-pagination>
          <Spinner v-if="materials_loading" />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from "vuex";
import FilterCategories from "~/components/FilterCategories/FilterCategories.vue";
import FilterCategoriesSelection from "~/components/FilterCategories/FilterCategoriesSelection.vue";
import Materials from "~/components/Materials/Materials.vue";
import SearchBar from "~/components/Search/SearchBar.vue";
import Spinner from "~/components/Spinner";
import {
  generateSearchMaterialsQuery,
  parseSearchMaterialsQuery,
} from "~/components/_helpers";
import PageMixin from "~/pages/page-mixin";


export default {
  components: {
    FilterCategories,
    FilterCategoriesSelection,
    Materials,
    Spinner,
    SearchBar,
  },
  mixins: [PageMixin],
  beforeRouteLeave(to, from, next) {
    this.$store.commit('RESET_FILTER_CATEGORIES_SELECTION')
    next()
  },
  data() {
    // Set filters from the URL parameters
    const urlInfo = parseSearchMaterialsQuery(this.$route.query);
    this.$store.commit('RESET_FILTER_CATEGORIES_SELECTION', urlInfo.search.filters)
    // Set filters from the router parameters (Community and Theme filters)
    if (this.$route.params.filterId) {
      this.$store.commit('SELECT_FILTER_CATEGORIES', {
        category: this.$route.meta.filterRoot,
        selection: [this.$route.params.filterId]
      })
    }
    // Update the filters and return data
    urlInfo.search.filters = this.$store.state.filterCategories.selection
    return {
      search: urlInfo.search,
      formData: {
        name: null,
      },
      sort_order: "relevance",
      sort_order_options: [
        { value: "relevance" },
        { value: "date_descending" },
        { value: "date_ascending" },
      ],
    };
  },
  computed: {
    ...mapGetters([
      "materials",
      "materials_loading",
      "materials_in_line",
      "did_you_mean",
    ]),
    showFilterCategories() {
      return this.isReady && this.materials && this.materials.records;
    },
  },
  mounted() {
    this.loadFilterCategories().finally(() => {
      this.executeSearch();
    });
  },
  methods: {
    onSearch(searchText) {
      searchText = searchText || ""
      const changed = searchText !== this.search.search_text;
      this.search.search_text = searchText;
      this.executeSearch(changed);
    },
    executeSearch(updateUrl) {
      this.$store.dispatch("searchMaterials", this.search);
      if (updateUrl) {
        this.$router.push(
          generateSearchMaterialsQuery(this.search, this.$route.name)
        );
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
        this.$router.push(
          generateSearchMaterialsQuery(this.search, this.$route.name)
        );
        this.$store.dispatch("searchMaterials", search);
        this.$refs.top.scrollIntoView({ behavior: "smooth" });
      }
    } /*         Change 1 item in line to 3 and back       */,
    changeViewType() {
      if (this.materials_in_line === 1) {
        this.$store.dispatch("searchMaterialsInLine", 3);
      } else {
        this.$store.dispatch("searchMaterialsInLine", 1);
      }
    } /*         Event the ordering item       */,
    changeOrdering() {
      const { sort_order } = this;
      if (sort_order === "date_descending") {
        this.search.ordering = "-publisher_date";
      } else if (sort_order === "date_ascending") {
        this.search.ordering = "publisher_date";
      } else {
        this.search.ordering = "";
      }
      this.search.page = 1;
      this.executeSearch(true);
    },
    loadFilterCategories() {
      if (this.$route.name.startsWith("mat")) {
        return Promise.resolve(null);
      }
      return this.$store.dispatch("getFilterCategories");
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../variables";

.filter-categories {
  min-width: 250px;
}

.search {
  position: relative;

  &__info {
    padding: 97px 0 0;
    margin-bottom: 20px;
    position: relative;
    min-height: 300px;

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
      justify-content: space-evenly;
      flex-wrap: wrap;
    }
  }

  &__tools {
    display: grid;
    grid-auto-flow: column;
    grid-template-rows: auto;
    position: relative;
    z-index: 1;

    @media @mobile {
      display: flex;
      justify-content: flex-start;
      flex-wrap: wrap;
    }

    &_results {
      display: grid;
      margin-left: 50px;
      @media @mobile {
        display: flex;
        margin-left: 0px;
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

    @media @wide {
      width: auto;
    }

    @media @tablet {
      width: auto;
    }

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
      background: url("../assets/images/arrow-text-grey.svg") 50% 50% / contain
        no-repeat;
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
