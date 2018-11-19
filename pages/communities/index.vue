<template>
  <section class="container main">
    <div>
      <Search />
      <PopularList />
    </div>
  </section>
</template>

<script>
import Search from '~/components/FilterCategories/Search/index.vue'
import PopularList from '~/components/Communities/PopularList'

export default {
  components: {
    Search,
    PopularList
  }
}
</script>
