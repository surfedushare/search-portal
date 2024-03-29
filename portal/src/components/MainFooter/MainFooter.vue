<template>
  <section class="main-footer">
    <div class="center_block main-footer__top_block">
      <div class="main-footer__quotes">
        <div class="bg"></div>
        {{ $t("Footer-quote") }}
      </div>
      <div class="main-footer__info">
        <h3>{{ $t("Footer-info-title") }}</h3>
        <div class="main-footer__info_text html-content" v-html="getFooterText()"></div>
        <a :href="$t('Digital-learning-materials-link')" target="_blank" class="main-footer__info_link arrow-link">
          SURF.nl
        </a>
      </div>
    </div>
    <div class="main-footer__bottom_block">
      <div class="main-footer__logo">
        <router-link :to="localePath('index')">
          <img
            src="../../assets/images/surflogo.png"
            srcset="../../assets/images/surflogo@2x.png 2x, ../../assets/images/surflogo@3x.png 3x"
            class="main-footer__logo_img"
          />
        </router-link>
      </div>
      <Menu />
      <div v-if="!isAuthenticated" class="main-footer__login">
        <a :href="getLoginLink()" class="button">
          {{ $t("login") }}
        </a>
      </div>
    </div>
  </section>
</template>

<script>
import Menu from "./Menu.vue";
import { mapGetters } from "vuex";
import DOMPurify from "dompurify";

export default {
  name: "MainFooter",
  components: {
    Menu,
  },
  computed: {
    ...mapGetters(["isAuthenticated"]),
  },
  methods: {
    getLoginLink() {
      return this.$store.getters.getLoginLink(this.$route);
    },
    getFooterText() {
      const footerInfo = this.$i18n.t("html-Footer-info-text");
      return DOMPurify.sanitize(footerInfo);
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../../variables";
.main-footer {
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  max-width: 1296px;
  padding: 0 20px;
  margin-top: 80px;

  &__top_block {
    @media @wide {
      display: flex;
    }
    @media @desktop {
      display: flex;
    }
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 80px;
  }

  &__quotes {
    font-family: @second-font;
    font-size: 22px;
    font-weight: bold;
    font-style: normal;
    font-stretch: normal;
    line-height: 1.2;
    letter-spacing: normal;
    color: #fff;
    max-width: 407px;
    margin: 0 0 0 40px;
    padding: 54px 37px 47px;
    @media @wide {
      margin: 3px 57px 0 47px;
    }
    @media @desktop {
      margin: 3px 57px 0 47px;
    }
    @media @tablet {
      margin: 3px 57px 50px 47px;
    }
    flex-shrink: 0;
    position: relative;
    .bg {
      background: @green;
      opacity: 0.9;
      position: absolute;
      border-radius: 20px 20px 20px 0;
      height: 100%;
      left: 0;
      top: 0;
      width: 100%;
      z-index: -1;
      &:before {
        content: "";
        background: url("../../assets/images/bubble-background-flipped.svg") 0 0 no-repeat;
        position: absolute;
        bottom: -37px;
        left: -43px;
        width: 63px;
        height: 58px;
      }
    }
  }

  h3 {
    margin: 0 0 29px;
  }

  &__info {
    @media @mobile {
      padding-top: 60px;
    }

    &_text {
      margin: 0 0 10px;
    }

    a {
      font-family: @second-font;
      font-size: 16px;
      font-weight: bold;
    }
  }

  &__links {
    flex-shrink: 0;
    width: 226px;
    margin: 0 54px 0 68px;
    @media @mobile {
      margin: 0;
      padding-top: 30px;
    }
  }

  &__link {
    display: flex;
    width: 100%;
    font-family: @second-font;
    font-size: 16px;
    font-weight: bold;
    justify-content: space-between;
    margin: -3px 0 23px;
    align-items: center;
  }

  &__bottom_block {
    @media @wide {
      display: flex;
      justify-content: space-around;
      height: 139px;
    }
    @media @desktop {
      display: flex;
      justify-content: space-around;
      height: 139px;
    }
    @media @tablet {
      display: flex;
      justify-content: space-around;
      height: 339px;
    }
    margin: auto;
    align-items: center;
    z-index: 1;
    padding: 0 0 15px;

    &:before {
      content: "";
      right: 50%;
      left: 0;
      height: 180px;
      margin-left: -25px;
      width: 100%;
      @media @wide {
        height: 137px;
        margin: 0 -600px 0 0;
        width: auto;
      }
      @media @desktop {
        height: 137px;
        margin: 0 -570px 0 0;
        width: auto;
      }
      @media @tablet {
        height: 239px;
        margin: 0 -390px 0 0;
        width: auto;
      }
      bottom: 0;
      border-radius: 0 60px 0 0;

      pointer-events: none;
      position: absolute;
      z-index: -1;
      background: @light-grey;
    }
  }

  &__logo {
    @media @desktop {
      padding: 31px 0 0;
    }
  }

  &__login {
    @media @mobile {
      margin-top: 10px;
      padding-left: 45px;
    }
  }
}
</style>
