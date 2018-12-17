
<template>
  <section class="container main collections">
    <div class="center_block">
      <div class="collections__info ">
        <img
          src="./../../assets/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="./../../assets/images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
         ./../../assets/images/pictures/rawpixel-760027-unsplash@3x.jpg 3x"
          class="collections__info_bg">
        <BreadCrumbs
          :items="[{title:`Home`, url: `/`} ]"/>
        <h2 class="collections__info_ttl">Mijn Collecties</h2>
        <Search
          :hide-categories="true"
          :hide-filter="true"
          class="collections__info_search"
          active-category-external-id="lom.technical.format"
        />
      </div>
      <div class="collections__add">
        <button
          class="collections__add__link button"
          @click.prevent="showAddCollection"
        >
          Nieuwe collectie
        </button>
      </div>
      <Collections :collections="my_collections.results"/>
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
    ...mapGetters(['my_collections', 'my_collection_materials'])
  },
  mounted() {
    this.$store.dispatch('getMyCollections');
  },
  methods: {
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
  padding: 101px 0 47px;

  &__info {
    padding: 64px 38px 0;
    margin: 0 0 87px;
    border-radius: 20px;
    position: relative;
    &_bg {
      position: absolute;
      right: 26px;
      top: -57px;
      width: 510px;
      border-radius: 21px;
      height: 298px;
    }
    &_ttl {
      padding: 0 0 49px;
      position: relative;
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
      background-image: url('./../../assets/images/plus-black.svg');
      background-position: 10px 50%;
      background-repeat: no-repeat;
      background-size: 24px 24px;
    }
  }
}
</style>
