<template>
  <section class="container main">
    <section class="communities">
      <div class="center_block center-header communities__center-header">
        <div class="communities__info ">
          <img
            class="communities__info_bg"
            src="/images/pictures/rawpixel-760027-unsplash.jpg"
            srcset="
              /images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
              /images/pictures/rawpixel-760027-unsplash@3x.jpg 3x
            "
          />
          <BreadCrumbs
            :items="[{ title: $t('Home'), url: localePath('index') }]"
          />
          <h2 class="communities__info_ttl">
            {{ !userCommunities ? $t('Communities') : $t('My-communities') }}
          </h2>
        </div>
      </div>
      <div class="center_block">
        <ul class="communities__items" v-if="communities.length">
          <li
            v-for="community in communities"
            :key="community.id"
            class="communities__item tile tile--items-in-line-3 materials__item--items-in-line-3"
          >
            <div class="communities__item_wrapper tile__wrapper">
              <div
                class="communities__item_logo"
                v-if="getCommunityDetail(community, $i18n.locale, 'logo')"
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
              <div
                class="communities__item_description html-content"
                v-html="
                  getCommunityDetail(community, $i18n.locale, 'description')
                "
                v-show="false"
              ></div>
              <div class="arrow-link communities__item_link">
                {{ $t('See') }}
              </div>
            </div>
            <router-link
              :to="
                localePath({
                  name: userCommunities
                    ? 'my-community'
                    : 'communities-community',
                  params: { community: community.id }
                })
              "
              class="communities__item_link_wrapper"
              :key="`${community.id}`"
              @click.native="setCommunity(community)"
            >
              {{ $t('See') }}
            </router-link>
          </li>
        </ul>
        <h3
          class="text-center"
          v-else-if="userCommunities"
          v-html="$t('html-No-communities-available-logged-in')"
        ></h3>
        <h3 class="text-center" v-else>{{ $t('No-communities-available') }}</h3>
      </div>
    </section>
  </section>
</template>

<script>
import BreadCrumbs from '~/components/BreadCrumbs'
import { mapGetters } from 'vuex'
import _ from 'lodash'

export default {
  name: 'communities',
  components: {
    BreadCrumbs
  },
  mounted() {
    this.$store.dispatch('getCommunities')
  },
  data() {
    return {
      userCommunities: this.$route.name.startsWith('my')
    }
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
  }
}
</script>

<style scoped lang="less">
@import url('../variables');

.communities {
  padding: 96px 0 199px;

  @media @mobile {
    overflow: hidden;
    padding-bottom: 100px;
  }
  &:before {
    content: '';
    left: 0;
    right: 50%;
    height: 353px;
    top: 354px;
    border-radius: 0 65px 65px 0;
    margin: 0 432px 0 0;
    pointer-events: none;
    border-right: 1px solid #686d75;
    border-top: 1px solid #686d75;
    border-bottom: 1px solid #686d75;
    position: absolute;
    z-index: -1;
  }

  &__center-header {
    padding-bottom: 32px;
    @media @mobile {
      padding-left: 30px;
      padding-right: 30px;
    }
  }
  &__info {
    padding: 70px 36px 0;
    margin: 0 0 80px;
    border-radius: 20px;
    position: relative;

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
      width: 50%;
      border-radius: 21px;

      @media @mobile {
        right: -20px;
        z-index: -1;
      }
      @media @mobile {
        right: -50px;
      }
    }
    &_ttl {
      padding: 0 0 49px;
      position: relative;
      &:before {
        content: '';
        min-width: 100%;
        position: absolute;
        background-color: rgba(244, 244, 244, 0.9);
        right: -48px;
        left: -48px;
        top: -98px;
        bottom: -70px;
        border-radius: 20px;
        z-index: -1;
      }
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
    display: flex;
    justify-content: left;
    flex-wrap: wrap;
    padding: 0;
    list-style: none;
    z-index: 1;

    @media @mobile {
      display: block;
    }
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
