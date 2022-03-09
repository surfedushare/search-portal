<template>
  <section class="edusources-container main-info">
    <div class="center_block info__center-header">
      <div class="info__info">
        <h2>{{ $t(titleKey) }}</h2>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="html-content" v-html="$t(htmlKey)" />
      </div>
    </div>
  </section>
</template>

<script>
import PageMixin from '~/pages/page-mixin'

export default {
  components: {},
  mixins: [PageMixin],
  data() {
    return {
      titleKey: this.$route.meta.title_translation_key,
      htmlKey: this.$route.meta.html_translation_key,
    }
  },
  metaInfo() {
    return {
      title: this.$i18n.t(this.$route.meta.title_translation_key),
    }
  },
}
</script>

<style lang="less" scoped>
@import './../variables';

.main-info {
  &__center-header {
    @media @mobile {
      padding-left: 30px;
      padding-right: 30px;
    }
    @media @tablet {
      padding-left: 38px;
      padding-right: 38px;
    }
  }
  padding: 96px 0 115px;
  @media @mobile {
    overflow: hidden;
  }

  &__info {
    margin: 0 0 223px;
    border-radius: 20px;
    position: relative;
    @media @tablet {
      padding: 70px 48px 0;
    }
  }
}
</style>
