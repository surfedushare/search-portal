<template>
  <section class="container main">
    <div>
      <div class="main__info">
        <div class="center_block center-header">
          <img
            class="main__info_bg"
            src="/images/pictures/header-image.jpg"
            alt="header-image"
          />
          <div class="main__info_block">
            <div class="bg" />
            <h2 class="main__info_title">
              <span v-if="statistic">{{ contedNumber }} </span
              >{{ $t('open-learning-materials-from-higher-education') }}
            </h2>
            <ul class="main__info_items">
              <li class="main__info_item">
                {{ $t('Free-to-use') }}
              </li>
              <li class="main__info_item">
                {{ $t('Judged-by-quality') }}
              </li>
              <li class="main__info_item">
                {{ $t('Inspiration-in-your-field') }}
              </li>
            </ul>
          </div>
          <Search
            educational-level-category-id="lom.educational.context"
            material-type-external-id="lom.technical.format"
            class="main__info_search"
          />
        </div>
      </div>

      <div class="main__materials">
        <div class="center_block">
          <h2 class="main__materials_title">
            {{ $t('Newest-open-learning-material') }}
          </h2>
          <Materials :materials="materials" />
        </div>
      </div>

      <div class="center_block main__thems_and_communities">
        <PopularList :communities="communities" class="main__communities">
          <template slot="header-info">
            <h2>{{ $t('Communities') }}</h2>
            <div class="popular-list__description">
              {{ $t('Open-learning-materials-from-professional-communit') }}
            </div>
          </template>
        </PopularList>
      </div>

      <div class="center_block">
        <section class="preview">
          <div class="preview__bg_block">
            <img
              src="/images/pictures/image_home.jpg"
              srcset="
                /images/pictures/image_home@2x.jpg 2x,
                /images/pictures/image_home@3x.jpg 3x
              "
              class="preview__bg_block-img"
            />
          </div>
          <div class="preview__text_block">
            <h2 class="preview__title">
              {{ $t('How-does-it-work-title') }}
            </h2>
            <!-- eslint-disable vue/no-v-html -->
            <div
              class="preview__text html-content"
              v-html="$t('html-How-does-it-work-text')"
            />
            <!-- eslint-enable vue/no-v-html -->
            <router-link :to="localePath('how-does-it-work')" class="button">
              {{ $t('How-does-it-work') }}
            </router-link>
          </div>
        </section>
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'
import Search from '~/components/FilterCategories/Search'
import numeral from 'numeral'
import Materials from '~/components/Materials'
import PopularList from '~/components/Communities/PopularList'

export default {
  components: {
    Search,
    PopularList,
    Materials
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
        .replace(',', '.')
    }
  },
  mounted() {
    this.$store.dispatch('getMaterials', { page_size: 4 })
    this.$store.dispatch('getCommunities', { params: { page_size: 3 } })
    this.$store.dispatch('getStatistic')
  }
}
</script>

<style lang="less">
@import './../variables';
.main {
  position: relative;
  z-index: 1;
  &__info {
    @media @desktop {
      padding: 120px 0 0;
      margin-bottom: 120px;
    }
    position: relative;

    .center-header {
      position: relative;
    }

    &_bg {
      width: 100%;
    }

    &_title {
      line-height: 1.25;
      color: #fff;
      margin: 0 0 16px;
      @media @mobile {
        font-size: 16px;
      }
    }

    &_main-title {
      opacity: 0;
      @media @mobile {
        display: none;
      }
    }
    &_items {
      padding: 0;
      margin: 0;
      @media @mobile {
        font-size: 12px;
      }
    }
    &_item {
      margin: 0;
      list-style: none;
      padding: 5px 0 8px 40px;
      background: url('/images/check-white.svg') 0 0 no-repeat;

      @media @mobile {
        background-size: 20px 20px;
        background-position-x: 10px;
      }
    }
    &_block {
      position: absolute;
      top: -50px;
      right: 100px;
      color: #fff;
      width: 572px;
      font-family: @second-font;
      padding: 31px 48px 40px;
      font-size: 16px;
      font-weight: bold;
      z-index: 1;

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
        @media @mobile {
          right: 10px;
          left: 10px;
          width: auto;
        }
        &:before {
          content: '';
          background: url('/images/buble-background-blue.svg') 0 0 no-repeat;
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
      margin: auto;

      @media @mobile {
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
      width: 700px;
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
    margin: 0 0 70px;

    &_title {
      margin: 0 0 32px;

      @media @mobile {
        font-size: 22px;
        margin: 0 0 20px;
      }
    }
  }

  .preview {
    position: relative;
    @media @desktop {
      padding: 50px 0 0 100px;
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
        background: url('/images/combined-shape.svg') no-repeat 0 0;
        right: -100px;
        top: 0;
        height: 109px;
        width: 119px;

        @media @mobile {
          right: 0;
        }
      }
      &:after {
        content: '';
        position: absolute;
        background: url('/images/message.svg') no-repeat 0 0;
        right: -82px;
        top: 22px;
        height: 33px;
        width: 35px;
        @media @mobile {
          right: 18px;
        }
      }
    }

    &__text_block {
      background: fade(@light-grey, 90%);
      border-radius: 20px;
      margin: 100px 0 168px;
      padding-top: 80px;
      padding-left: 15px;
      padding-right: 15px;
      @media @desktop {
        padding: 56px 50px 43px 410px;
        margin: 0 0 168px;
      }
    }

    &__title {
      margin: 0 0 20px;
      @media @mobile {
        font-size: 22px;
      }
    }

    &__text {
      margin: 0 0 44px;
    }
    .button {
      @media @mobile {
        margin-bottom: 24px;
      }
    }
  }
}
</style>
