<template>
  <section class="container main">
    <div>
      <div class="main__info">
        <div class="center_block center-header">
          <img
            class="main__info_bg"
            src="/images/pictures/header-image.jpg"
            alt="header-image"
          >
          <img
            class="main__info_bg-mobile"
            src="/images/pictures/lab-21-windesheim-voor-surf-018@2x.jpg"
            alt="header-image"
          >
          <h2 class="main__info_main-title">{{ $t('Open-learning-materials') }}</h2>

          <div class="main__info_block">
            <div class="bg" />
            <h2 class="main__info_title" ><span v-if="statistic">{{ contedNumber }} </span>{{ $t('open-learning-materials-from-higher-education') }}</h2>
            <ul class="main__info_items">
              <li class="main__info_item">{{ $t('Free-to-use') }}</li>
              <li class="main__info_item">{{ $t('Judged-by-quality') }}</li>
              <li class="main__info_item">{{ $t('Inspiration-in-your-field') }}</li>
            </ul>
          </div>
          <Search
            show-selected-category="lom.classification.obk.educationallevel.id"
            class="main__info_search"
            active-category-external-id="lom.technical.format"
          />
        </div>
      </div>
      <div class="center_block main__thems_and_communities">
        <Themes
          :themes="sortedThemes"
          class="main__thems"
        />
        <PopularList
          :communities="communities"
          class="main__communities"
        >
          <template slot="header-info">
            <h2>{{ $t('Communities') }}</h2>
            <div class="popular-list__description">{{ $t('Open-learning-materials-from-professional-communit') }}</div>
          </template>
        </PopularList>
      </div>
      <div class="main__materials">
        <div class="center_block">
          <h2 class="main__materials_title">{{ $t('Featured-open-learning-material') }}</h2>
          <Materials :materials="materials" />
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
import Search from '~/components/FilterCategories/Search';
import numeral from 'numeral';
import Materials from '~/components/Materials';
import PopularList from '~/components/Communities/PopularList';
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
    ...mapGetters(['materials', 'communities', 'sortedThemes', 'statistic']),
    /**
     * Get formatted 'number_of_views'
     * @returns String
     */
    contedNumber() {
      return numeral(this.statistic.value)
        .format('0,0')
        .replace(',', '.');
    }
  },
  mounted() {
    this.$store.dispatch('getMaterials', {
      page_size: 4
    });
    this.$store.dispatch('getCommunities', { params: { page_size: 3 } });
    this.$store.dispatch('getStatistic');
  }
};
</script>

<style lang="less">
@import './../assets/styles/variables';
.main {
  position: relative;
  z-index: 1;
  &__info {
    @media @desktop {
      padding: 104px 0 0;
      margin-bottom: 191px;
    }
    position: relative;

    &:before {
      @media @desktop {
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
    }
    .center-header {
      position: relative;
    }

    &_bg {
      position: absolute;
      top: 80px;
      left: 50px;
      width: calc(100% - 100px);
      z-index: -1;
      @media @mobile, @tablet {
        display: none;
      }
    }

    &_bg-mobile {
      @media @desktop {
        display: none;
      }
      position: absolute;
      left: 0;
      z-index: -1;
      top: 70px;
      border-radius: 10px;
      width: 100%;
      padding: 0 30px;
    }

    &_title {
      line-height: 1.25;
      color: #fff;
      margin: 0 0 16px;
      @media @mobile, @tablet {
        font-size: 16px;
      }
    }

    &_main-title {
      opacity: 0;
      @media @mobile, @tablet {
        display: none;
      }
    }
    &_items {
      padding: 0;
      margin: 0;
      @media @mobile, @tablet {
        font-size: 12px;
      }
    }
    &_item {
      margin: 0;
      list-style: none;
      padding: 5px 0 8px 40px;
      background: url('/images/check-white.svg') 0 0 no-repeat;

      @media @mobile, @tablet {
        background-size: 20px 20px;
        background-position-x: 10px;
      }
    }
    &_block {
      /*background: fade(@dark-blue, 90%); */
      color: #fff;
      width: 572px;
      margin: -39px 0 99px 541px;
      font-family: @second-font;
      padding: 31px 48px 40px;
      font-size: 16px;
      font-weight: bold;
      position: relative;

      @media @mobile, @tablet {
        margin: 50px 0 0 0;
        padding: 10px 20px;
        width: 100%;
        max-width: 350px;
      }

      & .bg {
        background: @dark-blue;
        opacity: 0.9;
        position: absolute;
        border-radius: 0 20px 20px 20px;
        height: 100%;
        left: 0;
        top: 0;
        width: 100%;
        z-index: -1;
        @media @mobile, @tablet {
          right: 10px;
          left: 10px;
          width: auto;
        }
        &:before {
          content: '';
          background: url('/images/buble-background-blue.svg') 0 0
            no-repeat;
          position: absolute;
          top: -36px;
          left: -46px;
          width: 63px;
          height: 58px;

          @media @tablet, @mobile {
            left: -24px;
            top: -19px;
            height: 30px;
          }
        }
      }
    }

    &_search {
      width: 996px;
      margin: auto;

      @media @mobile, @tablet {
        width: 100%;
        margin-top: 25px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
      }
    }
  }

  &__thems_and_communities {
    margin-bottom: 50px;
    @media @desktop {
      display: flex;
      margin-bottom: 97px;
    }
    align-items: start;
    justify-content: space-between;
  }

  &__thems {
    @media @desktop {
      width: 521px;
    }
  }

  &__communities {
    @media @desktop {
      width: 485px;
      padding: 0 86px 0 0;
    }
  }

  &__materials {
    position: relative;
    margin: 0 0 200px;

    &_title {
      margin: 0 0 32px;

      @media @mobile, @tablet {
        font-size: 22px;
        margin: 0 0 20px;
      }
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
