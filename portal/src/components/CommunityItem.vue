<template>
  <div
    :class="draft ? 'draft' : 'published'"
    class="wrapper tile__wrapper"
    @click="navigateToCommunity"
  >
    <div v-if="communityDetails.logo" class="logo">
      <img :src="communityDetails.logo" alt="" />
    </div>
    <h3 class="name">
      {{ communityDetails.title }}
    </h3>
    <div class="count">
      {{ $tc('learning-materials', community.materials_count) }}
    </div>
    <div class="actions">
      <span>
        {{ $t('See') }}
        <i class="fa fa-chevron-right"></i>
      </span>
      <router-link
        v-if="editable"
        :key="community.id"
        :to="
          localePath({
            name: 'my-community',
            params: { community: community.id }
          })
        "
        class="button edit"
        @click.native="$event.stopImmediatePropagation()"
      >
        <i class="fa fa-pencil-alt"></i>
      </router-link>
    </div>
  </div>
</template>
<script>
import { PublishStatus } from '~/utils'

export default {
  name: 'CommunityItem',
  props: {
    community: {
      type: Object,
      default: () => ({
        nl: {},
        en: {}
      })
    },
    editable: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    communityDetails() {
      return this.community.community_details.find(
        detail => detail.language_code === this.$i18n.locale.toUpperCase()
      )
    },
    draft() {
      return this.community.publish_status == PublishStatus.DRAFT
    }
  },
  methods: {
    navigateToCommunity() {
      this.$router.push(
        this.localePath({
          name: 'communities-community',
          params: { community: this.community.id }
        })
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
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  &:before {
    content: '';
    position: absolute;
    width: 5px;
    height: 92px;
    border-radius: 5px;
    top: 25px;
    left: 0;
  }

  &.draft:before {
    background: lighten(@dark-grey, 20%);
  }

  &.published:before {
    background: #0077c8;
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
.actions {
  text-decoration: none;
  font-weight: bold;
  color: @dark-blue;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;

  .button.edit {
    margin-left: 10px;
    padding: 10px;
  }
}
</style>
