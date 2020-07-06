<template>
  <section class="container main material">
    <Navigation :materials="materials" :material="material" />
    <MaterialTitleMobile :material="material" />
    <div v-if="material" class="center_block material__wrapper">
      <Sidebar :material="material" />
      <MaterialInfo :material="material" />
    </div>
    <div v-show="false" class="main__materials">
      <div class="center_block">
        <h2 class="main__materials_title">
          {{ $t('Also-interesting-for-you') }}
        </h2>
        <Materials v-if="materials" :materials="materials" :items-length="4" />
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'
import Materials from '~/components/Materials'
import Sidebar from '~/components/Materials/Sidebar'
import MaterialInfo from '~/components/Materials/MaterialInfo'
import MaterialTitleMobile from '~/components/Materials/MaterialTitleMobile'
import Navigation from '~/components/Materials/Navigation'

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
  mounted() {
    this.$store.dispatch('getMaterial', {
      id: this.$route.params.id,
      params: { count_view: true }
    })
  }
}
</script>

<style lang="less" scoped>
@import './../variables';
.material {
  padding: 32px 0 60px;
  @media @tablet, @mobile {
    padding-bottom: 100px;
  }

  &__wrapper {
    /* margin: 0 auto 50px; */
    @media @desktop {
      display: flex;
    }
  }
}
.main__materials_title {
  margin: 0 0 32px;
}
</style>
