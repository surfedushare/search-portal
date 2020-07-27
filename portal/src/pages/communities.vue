<template>
  <section class="container main">
    <section class="communities">
      <HeaderBlock :title="$t('Communities')" />
      <div class="center_block">
        <Tabs v-if="user.id && myCommunities.length">
          <template v-slot:after-tabs>
            <SwitchInput
              v-model="showDrafts"
              class="draft-switch"
              :label="$t('Show-drafts')"
            />
          </template>
          <Tab :title="$t('All-communities')">
            <ul v-if="communities.length" class="communities__items">
              <li
                v-for="community in communities"
                :key="community.id"
                class="communities__item"
              >
                <CommunityItem :community="community" />
              </li>
            </ul>
            <h3 v-else class="text-center">
              {{ $t('No-communities-available') }}
            </h3>
          </Tab>
          <Tab :title="$t('My-communities')" identifier="my-communities-tab">
            <ul
              v-if="myCommunities.length"
              class="communities__items my-communities"
            >
              <li
                v-for="community in myCommunities"
                :key="community.id"
                class="communities__item"
              >
                <CommunityItem
                  :community="community"
                  :editable="editable(community)"
                />
              </li>
            </ul>
            <h3 v-else class="text-center">
              {{ $t('No-communities-available') }}
            </h3>
          </Tab>
        </Tabs>
        <ul v-else-if="communities.length" class="communities__items">
          <li
            v-for="community in communities"
            :key="community.id"
            class="communities__item"
          >
            <CommunityItem :community="community" />
          </li>
        </ul>
        <h3 v-else class="text-center">
          {{ $t('No-communities-available') }}
        </h3>
      </div>
    </section>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'
import CommunityItem from '~/components/CommunityItem'
import HeaderBlock from '~/components/HeaderBlock'
import SwitchInput from '~/components/switch-input'
import Tabs from '~/components/Tabs'
import Tab from '~/components/Tab'
import { PublishStatus } from '~/utils'

export default {
  name: 'Communities',
  components: {
    CommunityItem,
    HeaderBlock,
    SwitchInput,
    Tab,
    Tabs
  },
  data() {
    return {
      showDrafts: true
    }
  },
  computed: {
    ...mapGetters(['user']),
    communities() {
      return this.$store.getters.getPublicCommunities(this.user)
    },
    myCommunities() {
      if (this.showDrafts) {
        return this.$store.getters.getUserCommunities(this.user)
      }

      return this.$store.getters
        .getUserCommunities(this.user)
        .filter(c => c.publish_status === PublishStatus.PUBLISHED)
    }
  },
  mounted() {
    this.$store.dispatch('getCommunities')
  },
  methods: {
    editable(community) {
      return this.user.communities.some(id => id === community.id)
    }
  }
}
</script>

<style scoped lang="less">
@import url('../variables');

.communities {
  &__center-header {
    padding-bottom: 120px;
    @media @mobile {
      padding-bottom: 30px;
      padding-left: 30px;
      padding-right: 30px;
    }
  }
  &__info {
    border-radius: 20px;
    position: relative;
    background: @light-grey;
    padding: 50px 30px;

    @media @tablet {
      padding: 70px 48px 0;
    }

    h2 {
      @media @mobile {
        font-size: 26px;
      }
    }
    &_bg {
      position: absolute;
      right: 26px;
      top: -51px;
      width: 40%;
      border-radius: 21px;

      @media @mobile {
        display: none;
      }
    }
    &_ttl {
      position: relative;
    }
    &_all {
      text-decoration: none;
      font-weight: bold;
      margin-bottom: 11px;
      display: inline-block;
    }
    &_search {
      margin: 0 66px;
      @media @mobile {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 10px 15px 0 rgba(5, 14, 29, 0.2);
        margin-bottom: 180px;
        margin-left: -20px;
        margin-right: -20px;
      }
      @media @tablet {
        margin-left: -48px;
        margin-right: -48px;
      }

      .search__fields {
        margin-bottom: 33px;
      }
    }
  }
  &__items {
    width: 100%;
    padding: 0;
    list-style: none;
    z-index: 1;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(275px, 300px));
    grid-gap: 1rem;
  }
  &__item {
    background: #fff;
    margin-bottom: 24px;

    @media @mobile {
      width: 100%;
      margin-left: 0;
    }
  }
}

.draft-switch {
  color: black;
  font-weight: bold;
  display: inline-flex;
  margin-left: 20px;
}
</style>
