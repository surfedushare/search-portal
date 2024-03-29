<!-- eslint-disable quotes -->
<template>
  <section class="search">
    <form action="/materials/search/" @submit.prevent="onSubmit">
      <div class="search-container">
        <div class="search__fields" tabindex="-1">
          <vue-autosuggest
            v-model="searchText"
            :class="autosuggestClasses"
            :suggestions="suggestions"
            :input-props="autosuggestInputProps"
            data-test="search_term"
            @input="onInputChange"
            @selected="onSelectSuggestion"
          >
            <template slot="before-suggestions">
              <div class="search__suggestions" tabindex="-1">{{ $t("SearchSuggestions") }}</div>
            </template>
          </vue-autosuggest>
          <button data-test="search_button" class="button" type="submit">{{ $t("Search") }}</button>
        </div>
      </div>
    </form>
  </section>
</template>

<script>
import { debounce } from "lodash";
import { VueAutosuggest } from "vue-autosuggest";
import { mapGetters } from "vuex";
import axios from "~/axios";

export default {
  name: "SearchTerm",
  components: {
    VueAutosuggest,
  },
  props: {
    placeholder: {
      type: String,
      default: null,
    },
    value: {
      type: String,
      default: null,
    },
  },
  data() {
    let text = "";
    // eslint-disable-next-line quotes
    if (this.$route.query?.search_text?.includes('"')) {
      text = this.$route.query?.search_text?.replace(/"/g, " ").trim();
    }
    // eslint-disable-next-line quotes
    if (this.$route.query?.search_text?.includes('\\"')) {
      text = this.$route.query?.search_text?.replace(/\\"/g, "");
    }

    return {
      searchText: this.value || text,
      suggestions: [],
    };
  },
  computed: {
    ...mapGetters({
      keywords: "materials_keywords",
    }),
    autosuggestInputProps: function () {
      return {
        placeholder: this.placeholder || this.$t("title-author-subject"),
        id: "autosuggest__input",
        type: "search",
        autofocus: false,
        class: {
          "with-dropdown": this.suggestions.length > 0,
        },
      };
    },
    autosuggestClasses: function () {
      return {
        "with-dropdown": this.suggestions.length > 0,
      };
    },
  },
  watch: {
    value(value) {
      this.searchText = value;
    },
  },
  methods: {
    onInputChange(query) {
      this.searchSuggestions(query, this);
    },
    searchSuggestions: debounce(async function (search) {
      if (!search || search.length <= 2) {
        this.suggestions = [];
        return;
      }

      const { data } = await axios.get("keywords/", {
        params: { query: search },
      });

      this.suggestions = [{ data }];
    }, 350),
    onSelectSuggestion(result) {
      const text = result ? result.item : this.searchText;
      this.$emit("search", text);
    },
    onSubmit() {
      this.$emit("search", this.searchText);
    },
  },
};
</script>

<style lang="less" scoped>
@import "../../variables";
.search {
  &__fields {
    display: grid;
    padding: 15px 0px;
    margin: 0px 24px;
    @media @wide {
      grid-template-columns: 3fr 135px;
    }
    @media @desktop {
      grid-template-columns: auto 135px;
    }
    @media @tablet {
      grid-template-columns: 3fr 135px;
    }
    @media @mobile-ls {
      grid-template-columns: 3fr 135px;
    }
  }
  &__suggestions {
    position: absolute;
    right: 0;
    font-weight: bold;
    font-size: 12pt;
    margin: 10px;
  }
  /deep/#autosuggest__input {
    position: relative;
    height: 48px;
    border-radius: 10px;
    background: @light-grey url("../../assets/images/search-grey.svg") 12px 50% no-repeat;
    background-size: 21px;
    border: none;
    font-family: "nunito";
    font-size: 16px;
    padding-left: 40px;
    margin-left: 0px;
    width: 100%;
    outline: none;

    @media @mobile {
      margin-bottom: 10px;
    }
  }

  .button {
    position: relative;
    margin: 0 0 0 30px;
    height: 48px;
    width: 104px;
    @media @mobile {
      margin: 10px 0;
      width: 100%;
      justify-content: center;
    }
  }
}
.search-container {
  margin-top: 5px;
  font-family: "nunito";
  font-size: 16px;
}
/deep/.autosuggest__results-container {
  position: absolute;
  width: 100%;
  margin-top: -3px;
  list-style: none;
  border-radius: 20px;
  box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
  max-width: calc(100% - 185px);
  z-index: 10;
  background-color: white;
  @media @mobile {
    max-width: calc(100% - 50px);
  }
}

/deep/.autosuggest__results {
  ul {
    list-style: none;
    padding: 10px;
  }

  li {
    text-align: left;
    padding: 10px;
    padding-left: 30px;
    background-size: 20px;
    cursor: pointer;

    &:hover,
    &.autosuggest__results-item--highlighted {
      background-size: 20px;
      color: @black;
      text-decoration: none;
      font-weight: 500;
    }

    &:last-child {
      border-radius: 0 0 20px 20px;
    }
  }
}
</style>
