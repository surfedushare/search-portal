<template>
  <div>
    <section class="container center_block search">
      <h2>Ranking tool</h2>
      <Search
        v-if="search"
        v-model="search.search_text"
        class="search__info_search"
        @onSearch="onSearch"
      />
      <div v-if="initialSearchQuery">
        <strong
          >Ranking search results for the query:
          {{ initialSearchQuery }}</strong
        >
        <button type="button" class="button cancel" @click="cancelRanking">
          Cancel
        </button>
        <button type="button" class="button">Save</button>
      </div>
      <div v-if="materials" class="ranking-materials">
        <div class="ranking-search-results">
          <h3>Search results</h3>
          <draggable
            :list="materials"
            :sort="false"
            :group="{
              name: 'rankingtool',
              pull: 'clone',
              put: false
            }"
            :clone="cloneMaterial"
            :move="onMove"
            data-id-attr="search-results"
          >
            <div
              v-for="material in materials"
              :key="material.external_id"
              class="material-container"
            >
              <Material
                :material="material"
                :handle-material-click="handleMaterialClick"
              />
            </div>
          </draggable>
        </div>
        <div class="ranking-dropzone">
          <DropContainer
            title="Most relevant materials"
            identifier="most-relevant"
            :move="onMove"
            :list="mostRelevantMaterials"
          />
          <DropContainer
            title="Relevant materials"
            identifier="relevant"
            :move="onMove"
            :list="relevantMaterials"
          />
          <DropContainer
            title="Non-relevant materials"
            identifier="non-relevant"
            :move="onMove"
            :list="nonRelevantMaterials"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import axios from '~/axios'
import draggable from 'vuedraggable'
import Material from '../components/Materials/Material/Material'
import Search from '~/components/Search'
import DropContainer from '~/components/RankingTool/DropContainer'

const initialState = () => ({
  initialSearchQuery: '',
  materials: null,
  orderedMaterials: [],
  mostRelevantMaterials: [],
  relevantMaterials: [],
  nonRelevantMaterials: [],
  search: {
    search_text: ''
  }
})

export default {
  components: {
    draggable,
    DropContainer,
    Material,
    Search
  },
  data() {
    return initialState()
  },
  methods: {
    onMove(evt) {
      const draggedExternalId = evt.draggedContext.element.external_id
      const draggedFromId = evt.from.getAttribute('data-id-attr')
      const draggedFromSearchResults = draggedFromId === 'search-results'

      const mostRelevantExists = this.mostRelevantMaterials.find(
        material => material.external_id === draggedExternalId
      )

      const relevantExists = this.relevantMaterials.find(
        material => material.external_id === draggedExternalId
      )

      const nonRelevantExists = this.nonRelevantMaterials.find(
        material => material.external_id === draggedExternalId
      )

      if (
        draggedFromSearchResults &&
        (mostRelevantExists || relevantExists || nonRelevantExists)
      ) {
        return false
      }

      return true
    },
    handleMaterialClick() {
      console.log(this.orderedMaterials)
      console.log('click')
    },
    cloneMaterial(material) {
      return { ...material }
    },
    async onSearch() {
      const { data: materials } = await axios.post('materials/search/', {
        search_text: this.search.search_text
      })
      if (!this.initialSearchQuery) {
        this.initialSearchQuery = this.search.search_text
      }
      this.materials = materials.records
    },
    cancelRanking() {
      Object.assign(this.$data, initialState())
    }
  }
}
</script>
<style lang="less" scoped>
@import './../variables';

h2 {
  margin-top: 20px;
}

h3 {
  margin-bottom: 20px;
}

.search__info_search {
  margin-top: 20px;
}

.ranking-materials {
  display: flex;
  margin-left: -20px;
}

.ranking-search-results {
  flex: 1;
  margin-left: 20px;
}

.ranking-dropzone {
  flex: 1;
  margin-left: 20px;
}

.material-container {
  margin-bottom: 20px;

  &:last-child {
    margin-bottom: 0;
  }
}

button.cancel {
  color: @green !important;
  background-color: white !important;
  border: 2px solid @light-grey !important;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
  padding: 17px 23px;
  margin-left: 20px;
  margin-right: 20px;
}
</style>
