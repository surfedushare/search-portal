<template>
  <section class="container search">
    <div>
      <div
        v-if="!materials_loading"
        class="search__info"
      >
        <div class="center_block">
          <div class="search__info_top">
            <nuxt-link to="/">Home</nuxt-link>
            <h2 v-if="materials">Zoekresultaten ({{ materials.records_total }})</h2>
          </div>
          <Search
            v-if="search"
            :hide-categories="true"
            :hide-filter="true"
            v-model="search"
            class="main__info_search"
          />
        </div>
      </div>
      <div class="center_block">
        <button
          class="button"
          @click.prevent="changeCount"
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
            <FilterCategories />
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

export default {
  components: {
    Search,
    FilterCategories,
    PopularList,
    Materials,
    Themes,
    Spinner
  },
  data() {
    return {
      search_text: [],
      search: false
    };
  },
  computed: {
    ...mapGetters(['materials', 'materials_loading', 'materials_in_line'])
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
    changeCount() {
      this.$store.dispatch('searchMaterialsInLine', 3);
    }
  }
};
</script>

<style lang="less" scoped>
@import './../../assets/styles/variables';
.search {
  position: relative;
  z-index: 1;
  &__info {
    padding: 104px 0 0;
    margin-bottom: 191px;
    position: relative;

    &_top {
      border-radius: 20px;
      background: fade(@light-grey, 90%);
      padding: 65px 46px;
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

    &_search {
      width: 996px;
      margin: auto;
    }
  }

  &__wrapper {
    display: flex;
    position: relative;
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
    }
  }

  &__materials {
    position: relative;
    margin: 0 0 132px;
    flex: 1 1 auto;
  }
}
</style>
