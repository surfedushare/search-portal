<template>
  <section class="edusources-container main how_work">
    <HeaderBlock :title="$t('How-does-it-work')" />
    <InfoBlock :title="$t('About-the-portal')" :content="$t('html-About-the-portal-text')" />
    <div class="center_block">
      <h2 class="how_work__materials_title">{{ $t("Newest-open-learning-material") }}</h2>
      <MaterialCards :materials="materials"></MaterialCards>
    </div>
  </section>
</template>

<script>
import { mapGetters } from "vuex";
import HeaderBlock from "~/components/HeaderBlock";
import InfoBlock from "~/components/InfoBlock";
import PageMixin from "~/pages/page-mixin";
import MaterialCards from "~/components/Materials/MaterialCards.vue";

export default {
  components: {
    HeaderBlock,
    InfoBlock,
    MaterialCards,
  },
  mixins: [PageMixin],
  computed: {
    ...mapGetters(["materials"]),
  },
  mounted() {
    this.$store.dispatch("getMaterials", { page_size: 4 });
  },
  metaInfo() {
    return {
      title: this.$i18n.t("How-does-it-work"),
    };
  },
};
</script>

<style lang="less" scoped>
@import "./../variables";
.how_work {
  &__materials_title {
    margin: 0 0 32px;
  }
}
</style>
