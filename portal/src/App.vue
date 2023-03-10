<template>
  <div id="app">
    <v-app>
      <div class="main_block">
        <NewMainHeader v-if="isNewHeader" />
        <MainHeader v-else />
        <router-view />
        <MainFooter />
      </div>
    </v-app>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { setLanguage } from "~/axios";
import MainFooter from "~/components/MainFooter/MainFooter.vue";
import NewMainHeader from "~/components/NewMainHeader.vue";
import MainHeader from "~/components/MainHeader/MainHeader.vue";

const DEFAULT_TITLE = "Edusources";

export default {
  dependencies: ["$window", "$log"],
  components: {
    MainHeader,
    MainFooter,
    NewMainHeader,
  },
  computed: {
    ...mapGetters(["isNewHeader"]),
  },
  watch: {
    "$i18n.locale"(newLocale) {
      setLanguage(newLocale);
    },
  },
  created() {
    this.$store.dispatch("getFilterCategories");
  },
  methods: {
    isDemoEnvironment() {
      return (
        this.$window.location.hostname.indexOf("acc.") >= 0 ||
        new URLSearchParams(this.$window.location.search).get("demo")
      );
    },
    isMBOEnvironment() {
      return this.$window.location.hostname.indexOf("mbo.") >= 0;
    },
  },
  metaInfo: {
    title: DEFAULT_TITLE,
    titleTemplate: (titleChunk) => {
      return titleChunk && titleChunk !== DEFAULT_TITLE ? `${titleChunk} | ${DEFAULT_TITLE}` : DEFAULT_TITLE;
    },
  },
};
</script>

<style lang="less">
@import "styles/normalize.css";
@import "variables.less";
@import "styles/common.less";
@import "styles/forms.less";
@import "styles/vuetify-overrides.less";
</style>
