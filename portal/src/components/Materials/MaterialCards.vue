<template>
  <v-row v-if="materials && materials.records" class="materials">
    <v-col v-for="material in materials.records" :key="material.id" lg="3" cols="12">
      <MaterialCard :material="material" :handle-material-click="handleMaterialClick" />
    </v-col>
  </v-row>
</template>

<script>
import MaterialCard from "~/components/Materials/MaterialCard.vue";

export default {
  components: {
    MaterialCard,
  },
  props: {
    materials: {
      type: Object,
      default: null,
    },
  },
  methods: {
    handleMaterialClick(material) {
      if (this.selectFor === "add") {
        this.$store.commit("SET_MATERIAL", material);
      } else {
        this.$router.push(
          this.localePath({
            name: "materials-id",
            params: { id: material.external_id },
          })
        );
      }
      this.$emit("click", material);
    },
  },
};
</script>
