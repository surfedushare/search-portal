<template>
  <section class="container main material">
    <Navigation :materials="materials" :material="material" />
    <div v-if="material" class="center_block material__wrapper">
      <Sidebar :material="material" :collections="collections" />
      <MaterialInfo :material="material" :communities="communities" />
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
import { uniqBy } from 'lodash'
import Materials from '~/components/Materials'
import Sidebar from '~/components/Materials/Sidebar'
import MaterialInfo from '~/components/Materials/MaterialInfo'
import Navigation from '~/components/Materials/Navigation'

export default {
  components: {
    Materials,
    Sidebar,
    MaterialInfo,
    Navigation
  },
  data() {
    return {
      collections: []
    }
  },
  computed: {
    ...mapGetters(['material', 'materials']),
    communities() {
      // Get communities from collections
      const communities = this.collections
        .map(collection => collection.communities)
        .flat()

      // Remove duplicate communities
      return uniqBy(communities, 'id')
    }
  },
  mounted() {
    this.$store.dispatch('getMaterial', {
      id: this.$route.params.id,
      params: { count_view: true }
    })
    this.$store
      .dispatch('checkMaterialInCollection', this.$route.params.id)
      .then(collections => {
        this.collections = collections.results
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
    display: flex;

    @media @mobile {
      flex-direction: column-reverse;
    }
  }
}
.main__materials_title {
  margin: 0 0 32px;
}
</style>
