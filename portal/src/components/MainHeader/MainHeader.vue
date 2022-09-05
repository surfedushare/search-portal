<template>
  <section class="main-header">
    <div v-if="user_permission_notifications.length" id="notification-bar">
      <div class="notifications">
        <div v-for="notification in user_permission_notifications" :key="notification.id">
          <p class="message">
            {{ notification[$i18n.locale].description }}
            (<router-link :to="localePath(notification.more_info_route)">{{ $t("more-info") }}</router-link
            >)
          </p>
          <p class="acknowledge">
            <button
              data-test="accept_cookies_button"
              class="button"
              @click="acknowledgeNotification(notification.type)"
            >
              {{ $t("Ok") }}
            </button>
          </p>
        </div>
      </div>
    </div>

    <div v-for="level in getMessageLevels" id="messages-bar-container" :key="level">
      <div v-if="hasMessages(level)" class="messages-bar">
        <i class="fas" :class="[getLevelIcon(level), level]"></i>
        <p class="message">
          {{ getMessagesContent(level) }}
        </p>
        <i class="fas fa-times" @click="$store.commit('CLEAR_MESSAGES', level)"></i>
      </div>
    </div>

    <div class="center_block">
      <div class="main-header__wrapper">
        <router-link :to="localePath('index')" class="main-header__logo">
          <img
            src="../../assets/images/edusourceslogo.png"
            srcset="../../assets/images/edusourceslogo@2x.png 2x, ../../assets/images/edusourceslogo@3x.png 3x"
            class="main-header__logo_img"
          />
        </router-link>
        <Menu class="main-header__menu" />

        <div class="main-header__actions">
          <div class="main-header__question">
            <button type="button" class="button" @click="toggleQuestionPopup">
              <span>{{ $t("Question") }}</span>
            </button>
          </div>
          <div v-if="isAuthenticated" class="main-header__user">
            <div class="main-header__user_name arrow-link">
              <span class="link">{{ $t("Menu") }}</span>
            </div>
            <nav class="main-header__user_menu">
              <ul class="main-header__user_menu_items">
                <li class="main-header__user_menu_item">
                  <router-link class="main-header__user_menu_link" :to="localePath({ name: 'my-privacy' })">
                    {{ $t("My-privacy") }}
                  </router-link>
                </li>
                <li class="main-header__user_menu_item">
                  <a class="main-header__user_menu_link" href="/logout/" @click.prevent="logout()">
                    {{ $t("logout") }}
                  </a>
                </li>
              </ul>
            </nav>
          </div>
          <LanguageSwitch class="main-header__language_switch" />
          <div class="edusources-container">
            <router-link :to="searchLink" class="search-icon">
              <img src="../../assets/images/search.svg" />
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="main-header__mobile">
      <button class="main-header__menu_button" @click="toggleMobileMenu()"></button>
      <router-link to="/" class="main-header__mobile_logo" @click.native="hideMobileMenu()">
        <img
          src="../../assets/images/edusourceslogo.png"
          srcset="../../assets/images/edusourceslogo@2x.png 2x, ../../assets/images/edusourceslogo@3x.png 3x"
          class="main-header__logo_img"
        />
      </router-link>
      <div v-if="show_header_menu" class="main-header__mobile_menu" onclick="">
        <div class="main-header__user">
          <ul class="main-header__user_menu_items">
            <li class="main-header__user_menu_item">
              <router-link
                :to="localePath('communities')"
                class="main-header__user_menu_link"
                @click.native="hideMobileMenu()"
              >
                {{ $t("Communities") }}
              </router-link>
            </li>
            <li class="main-header__user_menuitem">
              <router-link
                :to="localePath('how-does-it-work')"
                class="main-header__user_menu_link"
                @click.native="hideMobileMenu()"
              >
                {{ $t("How-does-it-work") }}
              </router-link>
            </li>
            <li class="main-header__user_menuitem">
              <div class="main-header__user_menu_link" @click="toggleQuestionPopup">{{ $t("Question") }}</div>
            </li>
            <li v-if="isAuthenticated" class="main-header__user_menu_item">
              <router-link
                class="main-header__user_menu_link"
                :to="localePath({ name: 'my-privacy' })"
                @click.native="hideMobileMenu()"
              >
                {{ $t("My-privacy") }}
              </router-link>
            </li>
            <li v-if="isAuthenticated" class="main-header__user_menu_item">
              <a class="main-header__user_menu_link" href="/logout/" @click.prevent="logout()">
                {{ $t("logout") }}
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div class="main-header__actions">
        <LanguageSwitch class="main-header__language_switch" />
        <div class="edusources-container">
          <router-link :to="searchLink" class="search-icon">
            <img src="../../assets/images/search.svg" />
          </router-link>
        </div>
      </div>
    </div>

    <QuestionPopup v-if="showQuestionPopup" :show-popup="showQuestionPopup" :close="toggleQuestionPopup" />
  </section>
</template>

<script>
import LanguageSwitch from "./LanguageSwitch";
import QuestionPopup from "../Popup/QuestionPopup.vue";
import Menu from "./Menu.vue";
import { generateSearchMaterialsQuery } from "../_helpers";
import { mapGetters } from "vuex";

export default {
  name: "MainHeader",
  components: {
    LanguageSwitch,
    Menu,
    QuestionPopup,
  },
  props: [],
  data() {
    return {
      showQuestionPopup: false,
    };
  },
  computed: {
    ...mapGetters([
      "isAuthenticated",
      "user",
      "show_header_menu",
      "user_permission_notifications",
      "hasMessages",
      "getMessageLevels",
      "getLevelIcon",
      "getMessagesContent",
    ]),
    questionLink() {
      return "mailto:info@edusources.nl?subject=" + this.$i18n.t("Question");
    },
    searchLink() {
      const searchRequest = {
        search_text: "",
        ordering: null,
        filters: [],
      };
      const route = this.$router.resolve(generateSearchMaterialsQuery(searchRequest, "materials-search"));
      return route ? route.href : "";
    },
  },
  methods: {
    logout() {
      this.$store.dispatch("logout", { fully: true });
    },
    toggleMobileMenu() {
      this.$store.commit("SET_HEADER_MENU_STATE", !this.show_header_menu);
    },
    hideMobileMenu() {
      this.$store.commit("SET_HEADER_MENU_STATE", false);
    },
    acknowledgeNotification(notificationType) {
      let notification = this.user_permission_notifications.find((notification) => {
        return notification.type === notificationType;
      });
      notification.is_allowed = true;
      this.$store.dispatch("postUser");
    },
    toggleQuestionPopup() {
      this.showQuestionPopup = !this.showQuestionPopup;
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../../variables";
.main-header {
  flex-shrink: 0;
  background-color: #fff;
  position: relative;
  position: sticky;
  top: 0;
  left: 0;
  z-index: 20;

  &:after {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
    pointer-events: none;
    box-shadow: 0 5px 30px 0 rgba(0, 0, 0, 0.1);
  }

  @p-top: 16px;
  @p-bottom: 15px;

  #notification-bar {
    border-bottom: 1px solid #333;
    padding: 10px;

    .notifications {
      max-width: 900px;
      margin: 0 auto;

      > div {
        display: flex;

        .message {
          flex: 1;
          padding-right: 20px;
        }

        .acknowledge {
          width: 70px;
        }
      }
    }
  }

  #messages-bar-container {
    position: fixed;
    z-index: 100;
    left: 50%;
    top: 0;
    width: 600px;
    margin-left: -300px;

    .messages-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;

      p {
        width: 100%;
      }

      .fas {
        padding: 10px;
      }
      .error {
        color: @red;
      }
      .info {
        color: @green;
      }

      min-height: 60px;
      margin-top: 10px;

      padding: 5px;
      background: white;
      border-radius: 5px;
      box-shadow: 5px 5px 10px;
    }
  }

  &__wrapper {
    @media @tablet {
      display: none;
    }
    @media @mobile {
      display: none;
    }
    @media @mobile-ls {
      display: none;
    }
    display: flex;
    width: 100%;
    justify-content: space-between;
    min-height: 80px;
    position: relative;
  }

  &__mobile {
    position: relative;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    @media @wide {
      display: none;
    }
    @media @desktop {
      display: none;
    }

    &_login {
      text-align: center;
      padding-bottom: 25px;
      .button {
        width: 100%;
      }
    }
    &_menu {
      position: absolute;
      z-index: 100;
      left: 0;
      top: 59px;
      width: auto;
      max-width: 320px;
      margin-right: 56px;
      background-color: #ffffff;
      box-shadow: 10px 20px 30px 0 rgba(0, 0, 0, 0.1);
      overflow-y: scroll;
    }

    &_logo {
      height: 32px;
      img {
        height: 32px;
      }
    }
  }

  &__menu_button {
    border-radius: 0;
    border: 0;
    color: @green;
    height: 30px;
    width: 30%;
    cursor: pointer;
    background: transparent url("../../assets/images/list-view-copy.svg") 0 50% no-repeat;

    &:focus,
    &:active {
      outline: none;
    }
  }

  &__logo {
    width: 20%;
    padding: 20px 0 9px 3px;
    line-height: 40px;

    img {
      height: 35px;
      vertical-align: middle;
    }
  }

  &__menu {
    display: flex;
    align-items: center;
    @media @desktop {
      padding: @p-top 0 @p-bottom;
    }
  }

  &__actions {
    display: flex;
    width: 30%;
    justify-content: flex-end;
  }

  &__login {
    display: flex;
    align-items: center;
    padding: @p-top 0 @p-bottom;
  }

  &__question {
    display: flex;
    align-items: flex-end;
    margin-right: 20px;
    @media @wide {
      padding: @p-top 0 @p-bottom;
    }
    @media @desktop {
      padding: @p-top 0 @p-bottom;
    }
    @media @mobile-ls {
      display: none;
    }
    @media @mobile {
      display: none;
    }
  }

  &__user {
    position: relative;
    display: flex;
    align-items: center;
    cursor: pointer;
    margin-right: 20px;

    &_name {
      color: @green;
      font-family: @second-font;
      font-size: 16px;
      font-weight: bold;
      display: flex;
      align-items: center;

      &:before {
        content: "";
        display: inline-block;
        vertical-align: middle;
        width: 25px;
        height: 25px;
        margin: 0 7px 0 0;
        background: url("../../assets/images/user.svg") 50% 50% / contain no-repeat;
      }

      &:after {
        transform: rotate(90deg);
        margin: 0 0 0 7px;
      }
    }

    &_menu {
      display: none;
      position: absolute;
      right: 0;
      top: 100%;
      width: 200px;
      box-shadow: 5px 5px 10px 5px rgba(204, 204, 204, 0.4);
      background-color: #ffffff;
      @media @mobile {
        width: 100%;
        z-index: 1;
      }
      &_items {
        margin: 0;
        padding: 0;
        list-style: none;
      }

      &_item {
        border-bottom: 1px solid @light-grey;
      }

      &_link {
        color: @dark-grey;
        font-size: 16px;
        line-height: 1.44;
        display: block;
        text-decoration: none;
        padding: 15px 35px;
        transition: color 0.2s;

        &:hover {
          color: @black;
        }
      }
    }

    &:hover &_menu {
      display: block;
    }
  }

  &__language_switch {
    margin-right: 20px;
  }

  .search-icon {
    display: block;
  }
  .edusources-container {
    align-self: center;
  }
}
</style>
