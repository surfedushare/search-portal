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
        <v-btn elevation="0" class="bg-yellow mr-4" href="upload">{{ $t("navigation.upload") }}</v-btn>
        <div v-if="!isAuthenticated" class="buttons">
          <v-btn outlined class="mr-4" :href="getLoginLink()">{{ $t("navigation.signin") }}</v-btn>
          <!-- <language-switcher-component></language-switcher-component> -->
        </div>

        <v-menu v-else>
          <template #activator="{ props }">
            <div class="user-info mr-4">
              <div>{{ user.name }}</div>
              <div class="user-org">{{ user.schac_home_organization }}</div>
            </div>
            <v-btn icon class="user-btn" v-bind="props"
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
          </template>
          <v-list>
            <v-list-item>
              <language-switcher-component></language-switcher-component>
              <v-divider></v-divider>
            </v-list-item>
            <v-list-item @click="toInstitution()">
              <v-list-item-title>
                <v-list-item-title>{{ $t("navigation.my-institution") }}</v-list-item-title>
              </v-list-item-title>
              <v-divider></v-divider>
            </v-list-item>
            <v-list-item @click="logout">
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
import { generateSearchMaterialsQuery } from "./_helpers";
import { mapGetters } from "vuex";

export default {
  name: "NewMainHeader",
  components: {},
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
    getLoginLink() {
      return this.$store.getters.getLoginLink(this.$route);
    },
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
  text-transform: none;
  font-family: Nunito;
  font-weight: 700;
}

.logo {
  max-height: 36px;
}
.buttons {
  display: contents;
}
.user-btn {
  background-color: rgba(var(--v-theme-green));
  color: white;
  border-radius: 24px !important;
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.user-org {
  color: rgba(var(--v-theme-green));
}
.buttons .v-btn {
  text-transform: none;
  border-radius: 6px;
  font-weight: 600;
  padding: 0 24px;
}

.v-btn--variant-outlined {
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

// /deep/ .button {
//   background-color: @yellow;
// }
</style>
