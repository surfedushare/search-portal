<template>
  <section class="menu">
    <nav class="menu__links">
      <router-link class="menu__link" :to="localePath('how-does-it-work')">{{ $t("How-does-it-work") }}</router-link>
      <router-link class="menu__link" :to="{ name: 'privacy' + '___' + $i18n.locale }">{{
        $t("Privacy-link")
      }}</router-link>
      <a class="menu__link" :href="'mailto:' + 'info@edusources.nl'" target="_blank">{{ $t("Contact-email") }}</a>

      <a class="menu__link" :href="supportLink()" target="_blank">Support</a>

      <router-link class="menu__link" :to="{ name: 'institutions' + '___' + $i18n.locale }">{{
        $t("Institutions")
      }}</router-link>
    </nav>
  </section>
</template>
<script>
export default {
  name: "MenuBlock",
  methods: {
    supportLink() {
      return this.$i18n.locale === "nl"
        ? "https://wiki.surfnet.nl/display/EDS/edusources"
        : "https://wiki.surfnet.nl/pages/viewpage.action?pageId=55345575";
    },
  },
};
</script>
<style lang="less" scoped>
@import "./../../variables";
.menu {
  @media @desktop {
    text-align: right;
  }

  &__links {
    @media @mobile {
      padding-left: 45px;
      display: table;
      a {
        display: table-row;
      }
    }
  }

  &__link {
    font-family: @second-font;
    font-size: 16px;
    font-weight: bold;
    color: @dark-grey;
    margin: 0 0 0 53px;
    &:first-child {
      margin: 0;
    }
  }
}
</style>
