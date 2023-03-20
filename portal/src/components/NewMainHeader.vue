<template>
  <v-app-bar app class="bg-gray-lighter">
    <div class="wrapper mx-auto">
      <router-link class="mt-2 mr-6" to="/">
        <img class="logo" src="../assets/images/edusourceslogo.png" />
      </router-link>

      <div v-if="!isAuthenticated" class="links">
        <div v-for="(link, index) in links" :key="index">
          <v-btn v-if="link.href" elevation="0" :href="link.href">
            {{ link.text }}
          </v-btn>
          <v-btn v-else elevation="0" :to="link.to">
            {{ link.text }}
          </v-btn>
        </div>
      </div>
      <v-spacer></v-spacer>
      <div v-if="!isAuthenticated" class="buttons mr-8">
        <v-btn elevation="0" class="bg-yellow mr-4" @click="toInstitution()">{{ $t("navigation.upload") }}</v-btn>
        <div class="buttons">
          <v-btn outlined class="mr-4" :href="getLoginLink()">{{ $t("navigation.signin") }}</v-btn>
          <NewLanguageSwitch class="main-header__language_switch" />
        </div>
      </div>

      <div v-if="isAuthenticated" class="user-info mr-4">
        <div>{{ user.name }}</div>
        <div class="user-org">{{ user.institution_name }}</div>
      </div>
      <v-menu>
        <template #activator="{ on: { click }, attrs, value }">
          <div v-if="!isAuthenticated">
            <div v-if="!value">
              <v-btn icon class="hamburger hamburger-closed" v-bind="attrs" @click="click">
                <svg width="24" height="17" viewBox="0 0 24 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M0 1.14286C0 0.511675 0.511675 0 1.14286 0H22.854C23.4852 0 23.9968 0.511675 23.9968 1.14286C23.9968 1.77404 23.4852 2.28571 22.854 2.28571H1.14286C0.511675 2.28571 0 1.77404 0 1.14286ZM0 8.00099C0 7.3698 0.511675 6.85813 1.14286 6.85813H22.854C23.4852 6.85813 23.9968 7.3698 23.9968 8.00099C23.9968 8.63217 23.4852 9.14384 22.854 9.14384H1.14286C0.511675 9.14384 0 8.63217 0 8.00099ZM1.14286 13.7162C0.511675 13.7162 0 14.2279 0 14.8591C0 15.4903 0.511675 16.0019 1.14286 16.0019H22.854C23.4852 16.0019 23.9968 15.4903 23.9968 14.8591C23.9968 14.2279 23.4852 13.7162 22.854 13.7162H1.14286Z"
                    fill="#5E6873"
                  />
                </svg>
              </v-btn>
            </div>
            <div v-else>
              <v-btn icon class="hamburger hamburger-open" v-bind="attrs" @click="click">
                <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M25 1L1 25"
                    stroke="#5E6873"
                    stroke-width="1.71429"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M1 1L25 25"
                    stroke="#5E6873"
                    stroke-width="1.71429"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </v-btn>
            </div>
          </div>
          <div v-else>
            <v-btn icon class="user-btn" v-bind="attrs" @click="click">
              <svg width="18" height="9" viewBox="0 0 18 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M16.5 0.874023L9.35333 8.02002C9.30696 8.06647 9.25188 8.10331 9.19125 8.12845C9.13062 8.15359 9.06563 8.16653 9 8.16653C8.93437 8.16653 8.86938 8.15359 8.80875 8.12845C8.74812 8.10331 8.69304 8.06647 8.64667 8.02002L1.5 0.874023"
                  stroke="white"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </v-btn>
          </div>
        </template>
        <v-list>
          <v-list-item>
            <NewLanguageSwitch class="main-header__language_switch" />
            <v-divider></v-divider>
          </v-list-item>
          <div v-for="(link, index) in links" :key="index" :class="{ active: link.active === true }">
            <v-list-item v-if="link.href" :href="link.href">
              <v-list-item-title>{{ link.text }}</v-list-item-title>
              <v-divider></v-divider>
            </v-list-item>
            <v-list-item v-else :to="link.to">
              <v-list-item-title>{{ link.text }}</v-list-item-title>
              <v-divider></v-divider>
            </v-list-item>
          </div>
          <v-list-item v-if="isAuthenticated" @click="toInstitution()">
            <v-list-item-title>{{ $t("navigation.my-institution") }}</v-list-item-title>
            <v-divider></v-divider>
          </v-list-item>
          <v-spacer></v-spacer>
          <v-list-item> </v-list-item>
          <v-list-item>
            <v-btn elevation="0" class="bg-yellow w-100" @click="toInstitution()">{{ $t("navigation.upload") }}</v-btn>
          </v-list-item>
          <v-list-item v-if="!isAuthenticated">
            <v-btn outlined class="w-100" :href="getLoginLink()">{{ $t("navigation.signin") }}</v-btn>
          </v-list-item>
          <v-list-item v-if="isAuthenticated">
            <v-btn outlined class="w-100" @click.prevent="logout()">{{ $t("navigation.signout") }}</v-btn>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
  </v-app-bar>
</template>

<script>
import { mapGetters } from "vuex";
import NewLanguageSwitch from "./NewLanguageSwitch";

export default {
  name: "NewMainHeader",
  components: {
    NewLanguageSwitch,
  },
  props: [],
  data() {
    return {
      showQuestionPopup: false,
    };
  },
  computed: {
    ...mapGetters([
      "use_api_endpoint",
      "isAuthenticated",
      "user",
      "show_header_menu",
      "user_permission_notifications",
      "hasMessages",
      "getMessageLevels",
      "getLevelIcon",
      "getMessagesContent",
    ]),
    links() {
      return [
        { text: this.$i18n.t("navigation.find-material"), to: "/", active: false },
        { text: this.$i18n.t("navigation.communities"), to: "/communitys", active: false },
        { text: this.$i18n.t("navigation.services"), href: this.use_api_endpoint, active: true },
      ];
    },
  },
  methods: {
    getLoginLink() {
      return this.$store.getters.getLoginLink(this.$route);
    },
    logout() {
      this.$store.dispatch("logout", { fully: true });
    },
    acknowledgeNotification(notificationType) {
      let notification = this.user_permission_notifications.find((notification) => {
        return notification.type === notificationType;
      });
      notification.is_allowed = true;
      this.$store.dispatch("postUser");
    },
    toInstitution() {
      if (this.user?.institution_link) {
        window.open(`${this.use_api_endpoint}/instellingen/${this.user?.institution_link}`, "_blank");
      } else {
        window.open(`${this.use_api_endpoint}/instellingen`, "_blank");
      }
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../variables";
.wrapper {
  display: flex;
  max-width: 1296px;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  width: 100%;
  top: 50px;
}
.links {
  display: none;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  @media @wide {
    display: flex;
  }
  @media @desktop {
    display: flex;
  }
}

.hamburger {
  display: flex;
  margin-right: 0px;
  @media @wide {
    display: none;
  }
  @media @desktop {
    display: none;
  }
}

.links .v-btn {
  font-weight: 700;
  font-size: 15.75px;
  color: black;
}

.logo {
  max-height: 36px;
}
.buttons {
  display: contents;
}
.user-btn {
  background-color: @green;
  color: white;
  border-radius: 24px !important;
  margin-right: 10px;
  @media @mobile {
    margin-right: 30px;
  }
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.user-org {
  color: @green;
}

.buttons {
  display: none;
  @media @wide {
    display: flex;
  }
  @media @desktop {
    display: flex;
  }
}
.buttons .v-btn {
  text-transform: none;
  border-radius: 6px;
  font-weight: 700;
  padding: 0 24px;
}

.v-btn--outlined {
  border: thin solid #5e6873;
}
.v-btn__content {
  flex-direction: column;
  align-items: flex-end;
}

.v-list-item {
  width: 200px;
  height: 60px;
}

.v-divider {
  position: absolute;
  bottom: 0px;
  width: 85%;
}

.w-100 {
  width: 100%;
}

.v-menu__content {
  top: 60px !important;
  margin-right: 12px;
  min-width: 390px !important;
}

.v-menu__content .v-list .v-list-item {
  width: 100% !important;
}

.v-btn--active {
  border-radius: 0;
  color: @green !important;
}

.v-btn--active::before {
  opacity: 0 !important;
}

.v-btn--active::after {
  content: "";
  position: absolute;
  width: 90%;
  margin-top: 62px;
  border-bottom: 2px solid @green;
}
</style>
