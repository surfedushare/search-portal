
<template>
  <section class="container main my_filters">
    <div class="center_block">
      <div class="my_filters__info ">
        <img
          src="/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="/images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
         /images/pictures/rawpixel-760027-unsplash@3x.jpg 3x"
          class="my_filters__info_bg">
        <BreadCrumbs
          :items="[{title: $t('Home'), url: localePath('index')}]"
        />
        <h2 class="my_filters__info_ttl">{{ $t('My-filters') }}</h2>
      </div>
      <div class="my_filters__add">
        <button
          class="my_filters__add__link button"
          @click.prevent="showAddFilter"
        >
          {{ $t('New-selection') }}
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
import AddFilter from '~/components/Popup/AddFilter';

export default {
  components: {
    MaterialsFilters,
    BreadCrumbs,
    AddFilter
  },
  data() {
    return {
      isShow: false
    };
  },
  computed: {
    ...mapGetters(['filters', 'user', 'isAuthenticated', 'user_loading'])
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
    } else if (!this.user_loading) {
      this.$router.push('/');
    }
  },
  methods: {
    /**
     * Show the popup 'Add filter'
     */
    showAddFilter() {
      this.isShow = true;
    },
    /**
     * Close the popup 'Add filter'
     */
    close() {
      this.isShow = false;
    }
  }
};
</script>

<style lang="less">
@import './../../../variables';
.my_filters {
  width: 100%;
  padding: 101px 0 47px;
  overflow: hidden;

  &__info {
    padding: 64px 38px 0;
    margin: 0 0 87px;
    border-radius: 20px;
    position: relative;
    min-height: 271px;

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
      width: 50%;
      border-radius: 21px;
      @media @mobile {
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
      @media @mobile {
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
      @media @mobile {
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
    position: relative;

    &__link {
      padding: 13px 43px 13px 51px;
      background-image: url('/images/plus-black.svg');
      background-position: 10px 50%;
      background-repeat: no-repeat;
      background-size: 24px 24px;
    }
  }
}
</style>
