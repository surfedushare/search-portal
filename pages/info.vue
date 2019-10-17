<template>
  <section class="container main info">
    <div class="center_block info__center-header">
      <div class="info__info">
        <h2 class="info__info_ttl">{{ $t(titleKey) }}</h2>
        <div class="html-content" v-html="$t(htmlKey)"></div>
      </div>
    </div>
  </section>
</template>

<script>

export default {
  components: {},
  data() {
    return {
      titleKey: this.$route.meta.title_translation_key,
      htmlKey: this.$route.meta.html_translation_key
    }
  }
};

</script>

<style lang="less" scoped>

  @import './../assets/styles/variables';

  .info {

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
        width: 50%;
        border-radius: 21px;

        @media @mobile {
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
    }
  }

</style>
