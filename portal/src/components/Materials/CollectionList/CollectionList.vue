<template>
  <div>
    <h3 class="material__info_subttl">{{ $t('In-collection') }}</h3>
    <ul class="material__info_collections">
      <li
        v-for="collection in collections"
        :key="collection.id"
        class="material__info_part_of"
      >
        <router-link
          class="material__info_main"
          :to="
            localePath({
              name: 'collections-id',
              params: { id: collection.id }
            })
          "
        >
          <h3>
            {{ collectionTitle(collection) }}
            <i class="material__info_main_arrow"></i>
          </h3>
          <div>
            {{ $tc('Materials', collection.materials_count) }}
          </div>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'CollectionList',
  props: {
    collections: {
      type: Array
    }
  },
  mounted() {},
  methods: {
    collectionTitle(collection) {
      return this.$i18n.locale === 'nl'
        ? collection.title_nl
        : collection.title_en
    }
  }
}
</script>

<style src="../MaterialInfo/MaterialInfo.component.less" scoped lang="less" />
