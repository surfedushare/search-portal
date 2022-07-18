<template>
  <section class="menu">
    <nav>
      <ul class="menu__list">
        <li class="menu__list_item">
          <router-link
            :to="localePath('communities')"
            class="menu__link"
            @click.native="closeSubMenu(true)"
          >
            {{ $t("Communities") }}
          </router-link>
        </li>
        <li class="menu__list_item">
          <router-link
            :to="localePath('how-does-it-work')"
            class="menu__link"
            @click.native="closeSubMenu(true)"
          >
            {{ $t("How-does-it-work") }}
          </router-link>
        </li>
      </ul>
    </nav>
  </section>
</template>

<script>

import { mapGetters } from "vuex";

export default {
  name: "MenuBlock",
  computed: {
    ...mapGetters(["sortedThemes", "show_header_menu"]),
  },
  methods: {
    /**
     * Hide the submenu
     */
    hideMenu() {
      this.$store.commit("SET_HEADER_MENU_STATE", false);
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../../variables";
.menu {
  font-size: 18px;
  font-weight: bold;
  font-family: @second-font;

  &__list {
    list-style: none;
    padding: 0;
    margin: 0;

    &_item {
      display: inline-block;
    }
  }

  &__link {
    color: @dark-grey;
    border-radius: 7px;
    border: 1px solid transparent;
    display: inline-block;
    margin: 0 25px;
    padding: 5px 10px;

    @media @mobile {
      padding-left: 0;
      margin-left: 0;
    }
    &.router-link-active {
      background: @light-grey;

      &:after {
        transform: rotate(-90deg);
      }
    }

    &:after {
      margin: 0 0 0 7px;
      transform: rotate(90deg);
      transition: transform 0.2s;
    }
  }

  &__sub {
    border-radius: 6px;
    width: 100%;
    background-color: #fff;
    @media @wide {
      position: absolute;
      left: 0;
      top: 100px;
      box-shadow: 0 5px 30px 0 rgba(170, 170, 170, 0.2);
    }
    @media @desktop {
      position: absolute;
      left: 0;
      top: 100%;
      box-shadow: 0 5px 30px 0 rgba(170, 170, 170, 0.2);
    }
    @media @mobile {
      padding-top: 20px;
      padding-right: 15px;
      min-width: 250px;
    }

    h3 {
      margin: 0 0 30px;
      @media @mobile {
        display: none;
      }
    }

    &_list {
      padding: 0;
      margin: 0;
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      align-items: stretch;

      &_item {
        min-width: 24%;
        margin: 0 0 20px;
        @media @mobile {
          width: 100%;
        }
      }
    }

    &_link {
      &:after {
        @media @desktop {
          margin: 0 0 0 7px;
        }
        @media @mobile {
          float: right;
          margin-top: 6px;
        }
      }

      &.nuxt-link-exact-active {
        color: @dark-grey;
        cursor: default;

        &:after {
          background-image: url("../../assets/images/arrow-text-grey.svg");
        }
      }
    }
  }
}
</style>
