
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
          :items="[{title:'Profiel', url: '/my/'}, {title:`Mijn Collecties`, url: `/my/collections/`} ]"/>
        <h2 class="collections__info_ttl">Mijn Collecties</h2>
        <Search
          :hide-categories="true"
          :hide-filter="true"
          class="collections__info_search"
          active-category-external-id="lom.technical.format"
        />
      </div>
      <div class="collections__add">
        <a
          href="/"
          class="collections__add__link button">Nieuwe collectie
        </a>
      </div>
      <Collections :collections="my_collections.results"/>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import Materials from '~/components/Materials';
import Collections from '~/components/Collections';
import Search from '~/components/FilterCategories/Search';

export default {
  components: {
    Collections,
    BreadCrumbs,
    Materials,
    Search
  },
  computed: {
    ...mapGetters(['my_collections', 'my_collection_materials'])
  },
  mounted() {
    console.log(this.$route);
    // this.$store.dispatch('getMaterialInMyCollection', this.$route.params.id);
    this.$store.dispatch('getMyCollections');
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
    &__link {
      padding: 13px 43px 13px 51px;
      background-image: url('./../../assets/images/plus-black.svg');
      background-position: 10px 50%;
      background-repeat: no-repeat;
      background-size: 24px;
    }
  }
}
</style>
