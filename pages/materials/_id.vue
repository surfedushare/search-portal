<template>
  <section class="container main material">
    <Navigation />

    <div
      v-if="material"
      class="center_block material__wrapper"
    >
      <Sidebar :material="material"/>
      <MaterialInfo :material="material"/>
    </div>
    <div class="main__materials">
      <div class="center_block">
        <h2 class="main__materials_title">Ook interessant voor jou</h2>
        <Materials
          v-if="materials"
          :materials="materials"
        />
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Materials from '~/components/Materials';
import Sidebar from '~/components/Materials/Sidebar';
import MaterialInfo from '~/components/Materials/MaterialInfo';
import Navigation from '~/components/Materials/Navigation';

export default {
  components: {
    Materials,
    Sidebar,
    MaterialInfo,
    Navigation
  },
  computed: {
    ...mapGetters(['material', 'material_communities', 'materials'])
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
    this.$store.dispatch('searchMaterials', {
      page_size: 4,
      search_text: []
    });
    this.$store.dispatch('getMaterial', this.$route.params.id);
  }
};
</script>

<style lang="less" scoped>
@import './../../assets/styles/variables';
.material {
  padding: 32px 0 152px;

  &:before {
    content: '';
    left: 0;
    right: 50%;
    height: 353px;
    top: 114px;
    border-radius: 0 65px 65px 0;
    margin: 0 432px 0 0;
    pointer-events: none;
    border-right: 1px solid #686d75;
    border-top: 1px solid #686d75;
    border-bottom: 1px solid #686d75;
    position: absolute;
    z-index: -1;
  }

  &__wrapper {
    display: flex;
    margin: 0 auto 124px;
  }
}
</style>
