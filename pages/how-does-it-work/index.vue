<template>
  <section class="container main how_work">
    <div class="center_block how_work__center-header">
      <div class="how_work__info">
        <img
          src="/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="/images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
             /images/pictures/rawpixel-760027-unsplash@3x.jpg 3x"
          class="how_work__info_bg"
        >
        <BreadCrumbs
          :items="[{title: $t('Home'), url: localePath('index')}]"
        />
        <h2 class="how_work__info_ttl">{{ $t('How-does-it-work') }}</h2>
        <!--<Search-->
        <!--v-model="search"-->
        <!--:hide-categories="true"-->
        <!--:hide-filter="true"-->
        <!--class="how_work__info_search"-->
        <!--/>-->
      </div>
    </div>
    <div class="center_block">
      <div class="how_work__desc">
        <div class="how_work__bg_block">
          <img
            src="/images/pictures/image_home.jpg"
            srcset="/images/pictures/image_home@2x.jpg 2x,
               /images/pictures/image_home@3x.jpg 3x"
            class="preview__bg_block-img"
          >
        </div>
        <div class="how_work__txt_block">
          <h2 class="how_work__txt_block__ttl">{{ $t('About-the-portal') }}</h2>
          <div class="html-content" v-html="$t('html-About-the-portal-text')"></div>
        </div>
      </div>
      <h2 class="how_work__materials_title">Uitgelicht</h2>
      <Materials
        v-if="materials"
        :materials="materials"
      />
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Search from '~/components/FilterCategories/Search';
import BreadCrumbs from '~/components/BreadCrumbs';
import Materials from '~/components/Materials';

export default {
  components: {
    Search,
    BreadCrumbs,
    Materials
  },
  data() {
    return {
      search: {
        search_text: []
      }
    };
  },
  computed: {
    ...mapGetters(['materials'])
  },
  mounted() {
    this.$store.dispatch('searchMaterials', {
      page_size: 4,
      search_text: [],
      return_filters: false
    });
  }
};
</script>

<style lang="less">
@import './../../assets/styles/variables';
.how_work {
  &__center-header {
    @media @mobile {
      padding-left: 30px;
      padding-right: 30px;
    }
    @media @tablet {
      padding-left: 38px;
      padding-right: 38px;
    }
  }
  padding: 96px 0 115px;
  @media @mobile {
    overflow: hidden;
  }
  &__info {
    padding: 70px 37px 0;
    margin: 0 0 223px;
    border-radius: 20px;
    position: relative;
    @media @tablet {
      padding: 70px 48px 0;
    }
    &_bg {
      position: absolute;
      right: 26px;
      top: -51px;
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
      @media @mobile {
        margin: 0;
        font-size: 28px;
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
    &_search {
      margin: 0 66px;
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
  &__desc {
    position: relative;
    @media @desktop {
      padding: 50px 0 0 100px;
    }
  }
  &__txt_block {
    background: fade(@light-grey, 90%);
    border-radius: 20px;
    margin: 100px 0 168px;
    padding-top: 80px;
    padding-left: 15px;
    padding-right: 15px;

    @media @desktop {
      padding: 56px 110px 55px 410px;
      margin: 0 0 113px;
    }
    &__ttl {
      margin-bottom: 21px;
    }
    p {
      margin-bottom: 28px;
    }
  }
  &__bg_block {
    position: absolute;
    top: -80px;
    left: 0;

    @media @desktop {
      top: -2px;
    }

    img {
      border-radius: 21px;

      @media @tablet, @mobile {
        width: 100%;
        padding-right: 80px;
        padding-left: 20px;
      }
    }
    &:before {
      content: '';
      position: absolute;
      background: url('../../public/images/combined-shape.svg') no-repeat 0 0;
      right: -100px;
      top: 0;
      height: 109px;
      width: 119px;

      @media @mobile, @tablet {
        right: 0;
      }
    }
    &:after {
      content: '';
      position: absolute;
      background: url('../../public/images/message.svg') no-repeat 0 0;
      right: -82px;
      top: 22px;
      height: 33px;
      width: 35px;
      @media @mobile, @tablet {
        right: 18px;
      }
    }
  }
  &__materials_title {
    margin: 0 0 32px;
  }
}
</style>
