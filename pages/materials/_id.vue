<template>
  <section class="container main material">
    <Navigation
      :materials="materials"
      :material="material"
    />
    <MaterialTitleMobile :material="material"/>
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
          :items-length="4"
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
import MaterialTitleMobile from '~/components/Materials/MaterialTitleMobile';
import Navigation from '~/components/Materials/Navigation';

export default {
  components: {
    Materials,
    Sidebar,
    MaterialInfo,
    Navigation,
    MaterialTitleMobile
  },
  computed: {
    ...mapGetters(['material', 'material_communities', 'materials'])
  },
  watch: {
    material(material) {
      if (material) {
        this.$store.dispatch('getMaterialCommunities', {
          params: {
            material_id: this.material.external_id
          }
        });
      }
    }
  },
  mounted() {
    const { materials } = this;
    if (!materials) {
      this.$store.dispatch('searchMaterials', {
        page_size: 4,
        search_text: []
      });
    }
    this.$store.dispatch('getMaterial', this.$route.params.id);
  }
};
</script>

<style lang="less" scoped>
@import './../../assets/styles/variables';
.material {
  padding: 32px 0 152px;
  @media @tablet, @mobile {
    padding-bottom: 100px;
  }
  &:before {
    content: '';
    left: 0;
    right: 50%;
    height: 353px;
    top: 114px;
    border-radius: 0 65px 65px 0;
    pointer-events: none;
    border-right: 1px solid #686d75;
    border-top: 1px solid #686d75;
    border-bottom: 1px solid #686d75;
    position: absolute;
    z-index: -1;
    margin: 0 40px 0 0;
    @media @desktop {
      margin: 0 432px 0 0;
    }

    @media @tablet {
      margin: 0 270px 0 0;
    }
  }

  &__wrapper {
    margin: 0 auto 50px;
    @media @desktop {
      display: flex;
      margin: 0 auto 124px;
    }
  }
}
.main__materials_title {
  margin: 0 0 32px;
}
</style>
