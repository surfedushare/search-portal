<template>
  <section class="container main">
    <div>
      <div class="main__info center_block">
        <h3>Open leermaterialen</h3>
        <div class="block">
          <h3>13.231 open leermaterialen uit het hoger onderwijs</h3>
          <ul>
            <li>Vrij te gebruiken</li>
            <li>Op kwaliteit beoordeeld</li>
            <li>Inspiratie op jouw vakgebied</li>
          </ul>
        </div>
        <Search />
      </div>
      <div class="center_block">
        <Themes />
        <PopularList />
      </div>
      <Materials class="center_block" />
    </div>
  </section>
</template>

<script>
import Search from '~/components/FilterCategories/Search/index.vue'
import PopularList from '~/components/Communities/PopularList'
import Materials from '~/components/Materials'
import Themes from '~/components/Themes'

export default {
  components: {
    Search,
    PopularList,
    Materials,
    Themes
  }
}
</script>
