<template>
  <section class="container main">
    <div>
      <div class="main__info">
        <div class="center_block">
          <h2>Open leermaterialen</h2>
          <div class="main__info_block">
            <h2 class="main__info_title">13.231 open leermaterialen uit het hoger onderwijs</h2>
            <ul class="main__info_items">
              <li class="main__info_item">Vrij te gebruiken</li>
              <li class="main__info_item">Op kwaliteit beoordeeld</li>
              <li class="main__info_item">Inspiratie op jouw vakgebied</li>
            </ul>
          </div>
          <Search class="main__info_search" />
        </div>
      </div>
      <div class="center_block main__thems_and_communities">
        <Themes class="main__thems" />
        <PopularList class="main__communities" />
      </div>
      <div class="main__materials">
        <div class="center_block">
          <h2 class="main__materials_title">Uitgelicht open leermateriaal</h2>
          <Materials
            :materials="materials"
          />
        </div>
      </div>
      <div class="center_block">
        <Preview />
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Search from '~/components/FilterCategories/Search/index.vue';
import PopularList from '~/components/Communities/PopularList';
import Materials from '~/components/Materials';
import Themes from '~/components/Themes';
import Preview from '~/components/HowDoesItWork/Preview';

export default {
  components: {
    Search,
    PopularList,
    Materials,
    Themes,
    Preview
  },
  computed: {
    ...mapGetters(['materials'])
  },
  mounted() {
    this.$store.dispatch('searchMaterials', {
      page_size: 4,
      search_text: []
    });
  }
};
</script>

<style lang="less">
@import './../assets/styles/variables';
.main {
  position: relative;
  z-index: 1;
  &__info {
    padding: 104px 0 0;
    margin-bottom: 191px;
    position: relative;

    &:before {
      content: '';
      right: 0;
      left: 50%;
      height: 353px;
      top: 303px;
      border-radius: 65px 0 0 65px;
      margin: 0 0 0 420px;
      pointer-events: none;
      border-left: 1px solid #686d75;
      border-top: 1px solid #686d75;
      border-bottom: 1px solid #686d75;
      position: absolute;
      z-index: -1;
    }

    &_title {
      line-height: 1.25;
      color: #fff;
      margin: 0 0 16px;
    }
    &_items {
      padding: 0;
      margin: 0;
    }
    &_item {
      margin: 0;
      list-style: none;
      padding: 5px 0 8px 40px;
      background: url('./../assets/images/check-white.svg') 0 0 no-repeat;
    }
    &_block {
      background: fade(@dark-blue, 90%);
      color: #fff;
      width: 572px;
      border-radius: 20px;
      margin: -39px 0 99px 541px;
      padding: 31px 48px 40px;
      font-family: @second-font;
      font-size: 16px;
      font-weight: bold;
    }

    &_search {
      width: 996px;
      margin: auto;
    }
  }

  &__thems_and_communities {
    display: flex;
    align-items: start;
    justify-content: space-between;
    margin-bottom: 97px;
  }

  &__thems {
    width: 521px;
  }

  &__communities {
    width: 485px;
    padding: 0 86px 0 0;
  }

  &__materials {
    position: relative;

    &_title {
      margin: 0 0 32px;
    }

    &:before {
      content: '';
      left: 0;
      right: 50%;
      height: 353px;
      bottom: -137px;
      border-radius: 0 65px 65px 0;
      margin: 0 410px 0 0;
      pointer-events: none;
      border-right: 1px solid #686d75;
      border-top: 1px solid #686d75;
      border-bottom: 1px solid #686d75;
      position: absolute;
      z-index: -1;
    }
  }
}
</style>
