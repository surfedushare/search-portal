<template>
  <section class="container main material">
    <Navigation :materials="materials" :material="material" />
    <div v-if="material" class="center_block material__wrapper">
      <Sidebar :material="material" :collections="collections" />
      <MaterialInfo
        :key="material.external_id"
        :material="material"
        :communities="communities"
        :collections="collections"
      />
    </div>
    <div v-else-if="!material && materialLoaded" class="not-found-section">
      <h1 class="not-found-title">
        {{ $t('Not-found-title') }}
      </h1>
      <router-link :to="localePath('index')" class="button">{{
        $t('Not-found-button')
      }}</router-link>
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
      collections: [],
      materialLoaded: false
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
    this.updateMaterial(this.$route.params.id)
  },
  beforeRouteUpdate(to, from, next) {
    this.updateMaterial(to.params.id)
    next()
  },
  methods: {
    updateMaterial(externalId) {
      this.$store
        .dispatch('getMaterial', {
          id: externalId,
          params: { count_view: true }
        })
        .finally(() => {
          this.materialLoaded = true
        })
      this.$store
        .dispatch('checkMaterialInCollection', externalId)
        .then(collections => {
          this.collections = collections.results
        })
    }
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

.not-found-section {
  display: flex;
  flex-direction: column;
  h1 {
    text-align: center;
    margin: 100px 0 20px;
  }

  .button {
    margin: 0 auto;
  }
}
</style>
