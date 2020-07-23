<template>
  <div class="wrapper tile__wrapper">
    <div v-if="communityDetails.logo" class="logo">
      <img :src="communityDetails.logo" alt="" />
    </div>
    <h3 class="name">
      {{ communityDetails.title }}
    </h3>
    <div class="count">
      {{ $tc('learning-materials', community.materials_count) }}
    </div>
    <div class="link">
      <router-link
        :key="community.id"
        :to="
          localePath({
            name: 'communities-community',
            params: { community: community.id }
          })
        "
        class="communities__item_link_wrapper"
      >
        {{ $t('See') }}
        <i class="fa fa-chevron-right"></i>
      </router-link>
    </div>
  </div>
</template>
<script>
export default {
  name: 'CommunityItem',
  props: {
    community: {
      type: Object,
      default: () => ({
        nl: {},
        en: {}
      })
    }
  },
  computed: {
    communityDetails() {
      return this.community.community_details.find(
        detail => detail.language_code === this.$i18n.locale.toUpperCase()
      )
    }
  }
}
</script>
<style lang="less" scoped>
@import url('../variables');

.wrapper {
  padding: 20px 20px 20px 40px;
  border-radius: 20px;
  position: relative;
  word-break: break-all;

  &:before {
    content: '';
    position: absolute;
    width: 5px;
    height: 92px;
    background: #0077c8;
    border-radius: 5px;
    top: 25px;
    left: 0;
  }
}
.logo {
  margin-bottom: 22px;
  height: 52px;
  width: 120px;
  background-color: #fafafa;
  img {
    display: block;
    max-width: 100%;
    max-height: 100%;
  }
}
.name {
  margin-bottom: 10px;
}
.count {
  margin-bottom: 10px;
}
.link {
  text-decoration: none;
  font-weight: bold;
  color: @dark-blue;

  i {
    margin-left: 10px;
  }
}
</style>
