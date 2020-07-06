<template>
  <section class="container main how_work">
    <div class="center_block how_work__center-header">
      <div class="how_work__info">
        <img
          src="/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="
            /images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
            /images/pictures/rawpixel-760027-unsplash@3x.jpg 3x
          "
          class="how_work__info_bg"
        />
        <h2 class="how_work__info_ttl">
          {{ $t('How-does-it-work') }}
        </h2>
      </div>
    </div>
    <InfoBlock
      :title="$t('About-the-portal')"
      :content="$t('html-About-the-portal-text')"
    />
    <div class="center_block">
      <h2 class="how_work__materials_title">
        {{ $t('Newest-open-learning-material') }}
      </h2>
      <Materials v-if="materials" :materials="materials" />
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'
import Materials from '~/components/Materials'
import InfoBlock from '~/components/InfoBlock'

export default {
  components: {
    Materials,
    InfoBlock
  },
  computed: {
    ...mapGetters(['materials'])
  },
  mounted() {
    this.$store.dispatch('getMaterials', { page_size: 4 })
  }
}
</script>

<style lang="less">
@import './../variables';
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
  padding: 80px 0 60px;

  &__info {
    padding: 50px 30px;
    margin: 0 0 80px;
    border-radius: 20px;
    background-color: rgba(244, 244, 244, 0.9);
    position: relative;
    border-radius: 20px;
    &_bg {
      position: absolute;
      right: 26px;
      top: -51px;
      width: 40%;
      border-radius: 21px;

      @media @mobile {
        display: none;
      }
    }
    &_search {
      margin: 0 66px;
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
  &__materials_title {
    margin: 0 0 32px;
  }
}
</style>
