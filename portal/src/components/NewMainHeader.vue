<template>
  <v-app-bar app class="bg-gray-lighter">
    <div class="wrapper mx-auto">
      <router-link class="mt-2 mr-6" to="/">
        <img class="logo" src="../assets/images/edusourceslogo.png" />
      </router-link>
      <div class="links">
        <div v-for="(link, index) in links" :key="index" :class="{ active: link.active === true }">
          <v-btn elevation="0" :href="link.href">
            {{ link.text }}
          </v-btn>
        </div>
      </div>
      <v-spacer></v-spacer>
      <div class="buttons mr-8">
        <v-btn elevation="0" class="bg-yellow mr-4" @click="toInstitution()">{{ $t("navigation.upload") }}</v-btn>
        <div v-if="!isAuthenticated" class="buttons">
          <v-btn outlined class="mr-4" :href="getLoginLink()">{{ $t("navigation.signin") }}</v-btn>
          <LanguageSwitch class="main-header__language_switch" />
        </div>

        <v-menu v-else>
          <template #activator="{ on: { click }, attrs }">
            <v-btn icon class="user-btn" v-bind="attrs" @click="click"
              ><svg width="18" height="9" viewBox="0 0 18 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M16.5 0.874023L9.35333 8.02002C9.30696 8.06647 9.25188 8.10331 9.19125 8.12845C9.13062 8.15359 9.06563 8.16653 9 8.16653C8.93437 8.16653 8.86938 8.15359 8.80875 8.12845C8.74812 8.10331 8.69304 8.06647 8.64667 8.02002L1.5 0.874023"
                  stroke="white"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </v-btn>
            <div class="user-info mr-4">
              <div>{{ user.name }}</div>
              <div class="user-org">{{ user.institution_name }}</div>
            </div>
          </template>
          <v-list>
            <v-list-item>
              <LanguageSwitch class="main-header__language_switch" />
              <v-divider></v-divider>
            </v-list-item>
            <v-list-item @click="toInstitution()">
              <v-list-item-title>
                <v-list-item-title>{{ $t("navigation.my-institution") }}</v-list-item-title>
              </v-list-item-title>
              <v-divider></v-divider>
            </v-list-item>
            <v-list-item href="/logout" @click.prevent="logout()">
              <v-list-item-title>{{ $t("navigation.signout") }}</v-list-item-title>
              <v-divider></v-divider>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </div>
  </v-app-bar>
</template>

<script>
import { mapGetters } from "vuex";
import LanguageSwitch from "./MainHeader/LanguageSwitch";

export default {
  name: "NewMainHeader",
  components: {
    LanguageSwitch,
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
    links() {
      return [
        { text: this.$i18n.t("navigation.find-material"), href: "/", active: false },
        { text: this.$i18n.t("navigation.communities"), href: "/communitys", active: false },
        { text: this.$i18n.t("navigation.services"), href: "https://use.edusources.nl", active: true },
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
        console.log(process.env.VUE_APP_USE_URL);
        if (process.env.VUE_APP_USE_URL) {
          window.open(process.env.VUE_APP_USE_URL + "/instellingen/" + this.user?.institution_link, "_blank");
        }
      } else {
        window.open(process.env.VUE_APP_USE_URL + "/instellingen", "_blank");
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
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
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
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.user-org {
  color: @green;
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

.v-menu__content {
  top: 60px !important;
  margin-right: 12px;
}
</style>
