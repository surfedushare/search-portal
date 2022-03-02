<template>
  <div class="edusources-container">
    <router-link
      v-if="$i18n.locale === 'en'"
      class="lang"
      :to="switchLocalePath('nl')"
      @click.native="switchLanguage('nl')"
    >
      NL
    </router-link>
    <router-link
      v-if="$i18n.locale === 'nl'"
      class="lang"
      :to="switchLocalePath('en')"
      @click.native="switchLanguage('en')"
    >
      EN
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'LanguageSwitch',
  methods: {
    switchLanguage(language) {
      this.$i18n.locale = language
    },
  },
}
</script>

<style scoped lang="less">
@import './../../../variables';

.edusources-container {
  align-self: center;
  flex-shrink: 0;
}

.lang {
  border: none;
  height: 20px;
  padding: 0;
  font-family: @second-font;
  font-size: 16px;
  font-weight: bold;

  @media @mobile {
    margin: 0;
  }
}
</style>
