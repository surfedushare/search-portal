
<template>
  <section class="container main collections my_filters">
    <div class="center_block">
      <div class="my_filters__info ">
        <img
          src="./../../../assets/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="./../../../assets/images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
         ./../../../assets/images/pictures/rawpixel-760027-unsplash@3x.jpg 3x"
          class="my_filters__info_bg">
        <BreadCrumbs
          :items="[{title:`Home`, url: `/`} ]"/>
        <h2 class="my_filters__info_ttl">Mijn Filters</h2>
        <Search
          :hide-categories="true"
          :hide-filter="true"
          class="my_filters__info_search"
          active-category-external-id="lom.technical.format"
        />
      </div>
      <div class="my_filters__add">
        <button
          class="my_filters__add__link button"
          @click.prevent="showAddFilter"
        >
          Nieuwe selectie
        </button>
      </div>
      <MaterialsFilters
        :materials_filters="filters"
        :user="user"
      />
    </div>
    <AddFilter
      v-if="isShow"
      :close="close"
      :is-show="isShow"
    />
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import MaterialsFilters from '~/components/MaterialsFilters';
import Search from '~/components/FilterCategories/Search';
import AddFilter from '~/components/Popup/AddFilter';

export default {
  components: {
    MaterialsFilters,
    BreadCrumbs,
    Search,
    AddFilter
  },
  data() {
    return {
      isShow: false
    };
  },
  computed: {
    ...mapGetters(['filters', 'user', 'isAuthenticated'])
  },
  watch: {
    isAuthenticated(isAuthenticated) {
      if (isAuthenticated) {
        this.$store.dispatch('getFilters');
      }
    }
  },
  mounted() {
    if (this.isAuthenticated) {
      this.$store.dispatch('getFilters');
    }
  },
  methods: {
    showAddFilter() {
      this.isShow = true;
    },
    close() {
      this.isShow = false;
    }
  }
};
</script>

<style lang="less">
@import './../../../assets/styles/variables';
.my_filters {
  width: 100%;
  padding: 101px 0 47px;
  overflow: hidden;

  &__info {
    padding: 64px 38px 0;
    margin: 0 0 87px;
    border-radius: 20px;
    position: relative;
    @media @tablet {
      margin-left: 25px;
      margin-right: 25px;
    }
    @media @mobile {
      margin-left: 15px;
      margin-right: 15px;
    }
    &_bg {
      position: absolute;
      right: 26px;
      top: -57px;
      width: 510px;
      border-radius: 21px;
      height: 298px;
      @media @mobile, @tablet {
        padding: 0;
        z-index: -1;
        right: -30px;
      }
      @media @mobile {
        right: -60px;
      }
    }
    &_ttl {
      padding: 0 0 49px;
      position: relative;
      @media @mobile, @tablet {
        font-size: 26px;
      }
      &:before {
        content: '';
        min-width: 100%;
        position: absolute;
        background-color: rgba(244, 244, 244, 0.9);
        right: -48px;
        left: -48px;
        top: -98px;
        bottom: -70px;
        border-radius: 20px;
        z-index: -1;
      }
    }
    &_all {
      text-decoration: none;
      font-weight: bold;
      margin-bottom: 11px;
      display: inline-block;
    }
    &_search {
      margin: 0 65px;
      @media @mobile, @tablet {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
        margin-bottom: 180px;
        margin-left: -20px;
        margin-right: -20px;
      }

      @media @tablet {
        margin-left: -48px;
        margin-right: -48px;
      }
      .search__fields {
        margin-bottom: 33px;
      }
    }
  }
  &__add {
    display: flex;
    justify-content: flex-end;
    margin-bottom: -55px;
    &__link {
      padding: 13px 43px 13px 51px;
      background-image: url('./../../../assets/images/plus-black.svg');
      background-position: 10px 50%;
      background-repeat: no-repeat;
      background-size: 24px 24px;
    }
  }
}
</style>
