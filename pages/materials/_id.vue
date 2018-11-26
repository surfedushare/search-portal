<template>
  <section class="container main material">
    <div
      v-if="material"
      class="center_block material__wrapper"
    >
      <div class="material__left">
        <div class="material__grey_block">
          <h4>Vakgebieden</h4>
          Biologie
          <h4>Leerniveaus</h4>
          WO Bachelor
          <h4>Soort materiaal</h4>
          <!--Video-->
          <!--<h4>Bestandsformaat</h4>-->
          {{ material.format }}
          <h4>Publicatiedatum</h4>
          {{ material.publish_datetime }}
          <h4>Taal</h4>
          {{ material.language }}
          <h4>Gebruiksrechten</h4>
          Naamsvermelding - Gelijk delen
          <a
            :href="material.url"
            class="button button--full-width"
            target="_blank"
          >Open link</a>
        </div>
        <h3>Materiaal toevoegen aan collectie</h3>
        <p>Om collecties te kunnen maken moet u eerst inloggen</p>
        <a
          href="/login/"
          class="arrow-link"
        >Inloggen met SURFconext</a>
      </div>
      <div class="material__right">
        <h1>{{ material.title }}</h1>
        <div><nuxt-link to="/">{{ material.author }}</nuxt-link> {{ material.publisher }}</div>
        <h3>Kwaliteit</h3>
        <h3>Samenvatting</h3>
        <div
          class="description"
          v-html="material.description"
        />
      </div>
    </div>
    <Materials class="center_block" />
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Materials from '~/components/Materials';

export default {
  components: {
    Materials
  },
  computed: {
    ...mapGetters(['material', 'material_communities'])
  },
  watch: {
    material(material) {
      if (material) {
        this.$store.dispatch('getMaterialCommunities', {
          params: {
            material_id: material.external_id
          }
        });
      }
    }
  },
  mounted() {
    this.$store.dispatch('getMaterial', this.$route.params.id);
  }
};
</script>

<style lang="less">
@import './../../assets/styles/variables';
.material {
  padding: 67px 0;
  &__wrapper {
    display: flex;
    margin: 0 0 133px;
  }

  &__left {
    width: 282px;
    flex-shrink: 0;
    margin: 0 124px 0 0;
  }

  &__grey_block {
    border-radius: 10px;
    padding: 30px 20px;
    background-color: fade(@light-grey, 90%);
    margin: 0 0 30px;
  }

  &__right {
    flex: 1 1 auto;
  }
}
</style>
