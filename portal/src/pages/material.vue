<template>
  <section class="edusources-container main material">
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
    <div v-else-if="!material && isReady" class="not-found-section">
      <h1 class="not-found-title">
        {{ $t('Not-found-title') }}
      </h1>
      <router-link :to="localePath('index')" class="button">
        {{
          $t('Not-found-button')
        }}
      </router-link>
    </div>
    <div v-if="materials.records.length" class="main__materials">
      <div class="center_block">
        <h2 class="main__materials_title">
          {{ $t('Also-interesting-for-you') }}
        </h2>
        <Materials
          :materials="materials"
          :items-length="4"
          @click="onMoreLikeThisClick"
        />
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
import PageMixin from '~/pages/page-mixin'

export default {
  components: {
    Materials,
    Sidebar,
    MaterialInfo,
    Navigation,
  },
  mixins: [PageMixin],
  dependencies: ['$log'],
  data() {
    return {
      collections: [],
      materials: {
        records: [],
      },
    }
  },
  computed: {
    ...mapGetters(['material']),
    communities() {
      // Get communities from collections
      const communities = this.collections
        .map((collection) => collection.communities)
        .flat()

      // Remove duplicate communities
      return uniqBy(communities, 'id')
    },
  },
  metaInfo() {
    const defaultTitle = this.$root.$meta().title
    return {
      title: this.material ? this.material.title || defaultTitle : defaultTitle,
    }
  },
  created() {
    this.pageLoad = new Promise((resolve, reject) => {
      this.updateMaterial(this.$route.params.id).then(resolve).catch(reject)
    })
  },
  beforeRouteUpdate(to, from, next) {
    this.pageLoad = new Promise((resolve, reject) => {
      this.updateMaterial(to.params.id).then(resolve).catch(reject)
    })
    next()
  },
  methods: {
    async updateMaterial(externalId) {
      const materialLoad = this.$store.dispatch('getMaterial', {
        id: externalId,
        params: { count_view: true },
      })
      const material = await materialLoad
      const materials = await this.$store.dispatch('getSimilarMaterials', {
        external_id: this.$route.params.id,
        language: material.language,
      })
      materials.records = materials.results
      this.materials = materials

      const collections = await this.$store.dispatch(
        'checkMaterialInCollection',
        externalId
      )
      this.collections = collections.results
      return materialLoad
    },
    onMoreLikeThisClick(material) {
      this.$log.customEvent('Waypoint', 'Click', material.external_id, null, {
        dimension2: 'more_like_this',
      })
    },
  },
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
.main__materials {
  margin: 60px 0 0;
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
