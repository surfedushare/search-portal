<template>
  <section class="container main">
    <div>
      <div class="main__info">
        <div class="center_block">
          <h2>Open leermaterialen</h2>
          <div class="main__info_block">
            <h2 class="main__info_title">13.231 open leermaterialen uit het hoger onderwijs</h2>
            <ul>
              <li class="main__info_item">Vrij te gebruiken</li>
              <li class="main__info_item">Op kwaliteit beoordeeld</li>
              <li class="main__info_item">Inspiratie op jouw vakgebied</li>
            </ul>
          </div>
          <Search class="main__info_search" />
        </div>
      </div>
      <div class="center_block main__thems_and_communities">
        <Themes class="main__thems" />
        <PopularList class="main__communities" />
      </div>
      <div class="main__materials">
        <Materials class="center_block" />
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import Search from '~/components/FilterCategories/Search/index.vue';
import PopularList from '~/components/Communities/PopularList';
import Materials from '~/components/Materials';
import Themes from '~/components/Themes';

export default {
  components: {
    Search,
    PopularList,
    Materials,
    Themes
  },
  computed: {
    ...mapGetters(['theme'])
  },
  mounted() {
    this.$store.dispatch('getTheme', this.$route.params.id);
  }
};
</script>
