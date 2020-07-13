<template>
  <section class="container main">
    <section class="communities">
      <HeaderBlock
        :title="!userCommunities ? $t('Communities') : $t('My-communities')"
      />
      <div class="center_block">
        <ul v-if="communities.length" class="communities__items">
          <li
            v-for="community in communities"
            :key="community.id"
            class="communities__item tile tile--items-in-line-3 materials__item--items-in-line-3"
          >
            <div class="communities__item_wrapper tile__wrapper">
              <div
                v-if="getCommunityDetail(community, $i18n.locale, 'logo')"
                class="communities__item_logo"
              >
                <img
                  :src="
                    `${getCommunityDetail(community, $i18n.locale, 'logo')}`
                  "
                  alt=""
                />
              </div>
              <h3 class="communities__item_name">
                {{ getCommunityDetail(community, $i18n.locale, 'title') }}
              </h3>
              <div class="communities__item_count">
                {{ $tc('learning-materials', community.materials_count) }}
              </div>
              <!-- eslint-disable vue/no-v-html -->
              <div
                v-show="false"
                class="communities__item_description html-content"
                v-html="
                  getCommunityDetail(community, $i18n.locale, 'description')
                "
              />
              <!-- eslint-enable vue/no-v-html -->
              <div class="arrow-link communities__item_link">
                {{ $t('See') }}
              </div>
            </div>
            <router-link
              :key="`${community.id}`"
              :to="
                localePath({
                  name: userCommunities
                    ? 'my-community'
                    : 'communities-community',
                  params: { community: community.id }
                })
              "
              class="communities__item_link_wrapper"
              @click.native="setCommunity(community)"
            >
              {{ $t('See') }}
            </router-link>
          </li>
        </ul>
        <!-- eslint-disable vue/no-v-html -->
        <h3
          v-else-if="userCommunities"
          class="text-center"
          v-html="$t('html-No-communities-available-logged-in')"
        />
        <!-- eslint-enable vue/no-v-html -->
        <h3 v-else class="text-center">
          {{ $t('No-communities-available') }}
        </h3>
      </div>
    </section>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'
import _ from 'lodash'
import HeaderBlock from '~/components/HeaderBlock'

export default {
  name: 'Communities',
  components: {
    HeaderBlock
  },
  data() {
    return {
      userCommunities: this.$route.name.startsWith('my')
    }
  },
  computed: {
    communities() {
      if (this.userCommunities) {
        return this.$store.getters.getUserCommunities(this.user)
      } else {
        return this.$store.getters.getPublicCommunities(this.user)
      }
    },
    ...mapGetters(['user'])
  },
  watch: {
    $route() {
      this.userCommunities = this.$route.name.startsWith('my')
    }
  },
  mounted() {
    this.$store.dispatch('getCommunities')
  },
  methods: {
    /**
     * Set community on click
     * @param community - {Object}
     */
    setCommunity(community) {
      this.$store.commit('SET_COMMUNITY', community)
    },
    getCommunityDetail(community, language, detail) {
      let communityDetails = _.find(community.community_details, {
        language_code: language.toUpperCase()
      })
      return communityDetails[detail] || null
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
    &_wrapper {
      padding: 28px 25px 45px 48px;
      border-radius: 20px;
      position: relative;
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
    &_logo {
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
    &_name {
      line-height: 1.2;
      margin-bottom: 36px;
    }
    &_count {
      margin-bottom: 14px;
    }
    &_description {
      margin-bottom: 37px;
    }
    &_link {
      text-decoration: none;
      font-weight: bold;
      color: @dark-blue;

      &_wrapper {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        color: transparent;
      }
    }
  }
}
</style>
