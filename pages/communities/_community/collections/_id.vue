<template>
  <section class="container main collection">
    <Collection :collection="collection" />
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import injector from 'vue-inject';
import Collection from '~/components/Collections/Collection';


$log = injector.get('$log');


export default {
  components: {
    Collection
  },
  computed: {
    ...mapGetters(['collection'])
  },
  mounted() {
    $log.warn("Unexpectedly using pages/_community/collections/_id.vue");
  }
};
</script>
