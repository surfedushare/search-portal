
<template>
  <section class="container main collections">
    <div class="center_block center-header collections__center-header">
      <div class="collections__info ">
        <img
          src="./../../assets/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="./../../assets/images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
         ./../../assets/images/pictures/rawpixel-760027-unsplash@3x.jpg 3x"
          class="collections__info_bg">
        <BreadCrumbs
          :items="[{title: $t('Home'), url: localePath('index')}]"
        />
        <h2 class="collections__info_ttl">{{ $t('My-collections') }}</h2>
      </div>
    </div>
    <div class="center_block">
      <div class="collections__add">
        <button
          class="collections__add__link button"
          @click.prevent="showAddCollection"
        >
          {{ $t('New-collection') }}
        </button>
      </div>
      <div
        v-infinite-scroll="loadMore"
        infinite-scroll-disabled="my_collections_loading"
        infinite-scroll-distance="10"
      >
        <Collections
          :collections="my_collections.results"
          :loading="my_collections_loading"
        />
      </div>
      <AddCollection
        v-if="isShow"
        :close="close"
        :is-show="isShow"
      />
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import Materials from '~/components/Materials';
import Collections from '~/components/Collections';
import Search from '~/components/FilterCategories/Search';
import AddCollection from '~/components/Popup/AddCollection';

export default {
  components: {
    Collections,
    BreadCrumbs,
    Materials,
    Search,
    AddCollection
  },
  data() {
    return {
      isShow: false
    };
  },
  computed: {
    ...mapGetters([
      'my_collections',
      'my_collection_materials',
      'my_collections_loading',
      'isAuthenticated',
      'user_loading'
    ])
  },
  watch: {
    isAuthenticated(isAuthenticated) {
      if (isAuthenticated) {
        this.$store.dispatch('getMyCollections');
      }
    }
  },
  mounted() {
    if (this.isAuthenticated) {
      this.$store.dispatch('getMyCollections');
    } else if (!this.user_loading) {
      this.$router.push('/');
    }
  },
  methods: {
    /**
     * Load next collections
     */
    loadMore() {
      const { my_collections, my_collections_loading } = this;
      if (my_collections.next && !my_collections_loading) {
        this.$store.dispatch('getMyCollectionsNextPage');
      }
    },
    showAddCollection() {
      this.isShow = true;
    },
    close() {
      this.isShow = false;
    }
  }
};
</script>
<style lang="less">
@import './../../assets/styles/variables';
.collections {
  width: 100%;
  padding: 0 0 47px;
  &__center-header {
    padding-top: 101px;
    overflow: hidden;
    @media @mobile {
      padding-left: 30px;
      padding-right: 30px;
    }
  }
  &__info {
    padding: 64px 48px 0;
    margin: 0 0 87px;
    border-radius: 20px;
    position: relative;
    min-height: 271px;

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
        right: -20px;
      }
      @media @mobile {
        right: -50px;
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
        background-color: #fff;
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
    margin-bottom: 55px;
    position: relative;

    &__link {
      padding: 13px 43px 13px 51px;
      background-image: url('./../../assets/images/plus-black.svg');
      background-position: 10px 50%;
      background-repeat: no-repeat;
      background-size: 24px 24px;
    }
  }
}
</style>
