<template>
  <div class="buttons">
    <v-btn plain elevation="0" :class="{ preferred: $i18n.locale === 'nl' }" @click="switchLanguage('nl')">NL</v-btn>
    |
    <v-btn plain elevation="0" :class="{ preferred: $i18n.locale === 'en' }" @click="switchLanguage('en')"> EN </v-btn>
  </div>
</template>

<script>
export default {
  name: "NewLanguageSwitch",
  methods: {
    switchLanguage(language) {
      this.$i18n.locale = language;
    },
  },
};
</script>

<style scoped lang="less">
@import "./../variables";

.buttons {
  display: flex !important;
  align-items: baseline;
  margin-left: -8px;
}

.v-btn {
  border-radius: 0px !important;
  text-transform: none !important;
  min-width: 0 !important;
}
.v-btn__content {
  padding: 0 !important;
}

.v-btn:hover,
.active {
  color: @green;
}

.v-btn--plain {
  padding: 8px !important;
}

.preferred {
  color: @green;
}

@media @mobile {
  margin: 0;
}
</style>
