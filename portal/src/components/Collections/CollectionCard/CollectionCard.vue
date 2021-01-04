<template>
  <div class="collection-card">
    <button
      v-if="editableContent"
      :class="{ 'select-icon': true, selected: collection.selected }"
      @click="deleteCollectionPopup(collection)"
    >
      Delete
    </button>
    <div
      :class="{ selected: collection.selected }"
      class="collections__item_wrapper tile__wrapper"
    >
      <div class="collections__item_header">{{ $t('Collection') }}</div>
      <h3 class="collections__item_ttl">
        {{ $i18n.locale === 'nl' ? collection.title_nl : collection.title_en }}
      </h3>
      <p class="collections__item_count">
        {{ $tc('items', collection.materials_count) }}
      </p>
    </div>

    <router-link
      :key="`${collection.id}`"
      :to="
        localePath({
          name: editableContent ? 'my-collection' : 'collections-id',
          params: { id: collection.id }
        })
      "
      class="collections__item_ttl_link"
    >
      {{ $i18n.locale === 'nl' ? collection.title_nl : collection.title_en }}
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'CollectionCard',
  props: {
    collection: {
      type: Object,
      default: null,
      required: false
    },
    editableContent: {
      type: Boolean,
      default: false,
      required: false
    },
    deleteCollectionPopup: {
      type: Function,
      default: () => {},
      required: false
    }
  }
}
</script>

<style src="./../Collections.component.less" scoped lang="less"></style>
