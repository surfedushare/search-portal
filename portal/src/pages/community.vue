<template>
  <section class="container main">
    <section class="community">
      <div v-if="!community_details && isReady">
        <error status-code="404" message-key="community-not-found" />
      </div>
      <div v-else-if="community_details">
        <div class="center_block">
          <InfoBlock
            :title="community_details.title"
            :content="community_details.description"
            :website_url="community_details.website_url"
            :logo_src="community_details.featured_image"
          />

          <div>
            <Collections
              v-if="community_collections"
              :collections="community_collections"
              class="community__collections"
            >
              <template slot="header-info">
                <h2>{{ $t('Collections-2') }}</h2>
                <button
                  v-if="isReady && community_info.publisher"
                  class="button"
                  @click="goToCommunitySearch()"
                >
                  {{ $t('Search-in-community-materials') }}
                </button>
              </template>
            </Collections>
            <Spinner v-if="community_collections_loading" />
          </div>

          <template>
            <div v-show="false" class="community__row">
              <Themes :themes="community_themes" class="community__themas" />
              <div class="community__themas_and_disciplines">
                <Disciplines
                  class="community__disciplines"
                  :disciplines="community_disciplines"
                />
              </div>
            </div>
          </template>
        </div>
      </div>
    </section>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'
import PageMixin from '~/pages/page-mixin'
import InfoBlock from '~/components/InfoBlock'
import Themes from '~/components/Themes'
import Disciplines from '~/components/Disciplines'
import Collections from '~/components/Collections'
import Spinner from '~/components/Spinner'
import Error from '~/components/error'
import { isEmpty } from 'lodash'
import { localePath } from '~/i18n/plugin.routing'

export default {
  name: 'Community',
  components: {
    Error,
    Themes,
    Disciplines,
    Collections,
    Spinner,
    InfoBlock
  },
  mixins: [PageMixin],
  props: [],
  data() {
    return {
      isSearch: false,
      search: false
    }
  },
  computed: {
    ...mapGetters([
      'community_disciplines',
      'community_themes',
      'community_collections_loading',
      'user'
    ]),
    community_collections() {
      return this.$store.getters.getPublicCollections(this.user)
    },
    community_info() {
      return this.$store.getters.getCommunityInfo(this.user) || null
    },
    community_details() {
      // Retrieve the details and exit when invalid or loading
      let communityDetails = this.$store.getters.getCommunityDetails(
        this.user,
        this.$i18n.locale
      )
      if (isEmpty(communityDetails)) {
        return communityDetails || null
      }
      // Fill some defaults for the details
      communityDetails.featured_image =
        communityDetails.featured_image ||
        '/images/pictures/community-default.jpg'
      return communityDetails
    }
  },
  created() {
    const { community } = this.$route.params
    this.pageLoad = this.$store.dispatch('getCommunity', community)
    this.$store.dispatch('getCommunityThemes', community)
    this.$store.dispatch('getCommunityDisciplines', community)
    this.$store.dispatch('getCommunityCollections', community)
  },
  metaInfo() {
    const defaultTitle = this.$root.$meta().title
    return {
      title: this.community_details
        ? this.community_details.title || defaultTitle
        : defaultTitle
    }
  },
  methods: {
    goToCommunitySearch() {
      const searchRoute = localePath({
        name: 'communities-search',
        params: { filterId: this.community_info.publisher }
      })
      this.$router.push(searchRoute)
    }
  }
}
</script>

<style lang="less" scoped>
@import url('../variables');
.community {
  padding-bottom: 80px;
  margin-top: 60px;

  &__info {
    padding: 0 36px 0;
    border-radius: 20px;
    position: relative;

    @media @desktop {
      margin: 0 0 205px;
    }
    &_wrapper {
      display: flex;
      justify-content: flex-start;
      padding-top: 40px;
      position: relative;
      &:before {
        content: '';
        min-width: 100%;
        position: absolute;
        background-color: rgba(244, 244, 244, 0.9);
        right: -36px;
        left: -36px;
        top: 0;
        bottom: -70px;
        border-radius: 20px;
        z-index: -1;
      }
    }
    &_logo {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 230px;
      height: 136px;
      background: rgba(255, 255, 255, 0.5);
      border-radius: 10px;
      margin-right: 32px;
      img {
        max-width: 100%;
        max-height: 100%;
        border-radius: 10px;
      }
    }
    &_title {
      display: inline-block;
      vertical-align: top;
      float: left;
      width: calc(100% - 272px);
      padding: 10px 0 0 0;
      @media @mobile {
        width: 100%;
        padding: initial;
      }
    }
    &_bg {
      position: absolute;
      right: 26px;
      top: -51px;
      width: 50%;
      border-radius: 21px;
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
      .search__fields {
        margin-bottom: 33px;
      }
      @media @mobile {
        margin: 0 -17px;
      }
    }
  }
  &__row {
    width: 100%;
    display: flex;
    justify-content: space-between;
    margin-bottom: 80px;
    align-items: flex-start;

    @media @mobile {
      display: initial;
    }
  }
  &__description {
    margin-top: 127px;
    width: calc(50% - 15px);
    border-radius: 20px;
    background-color: rgba(244, 244, 244, 0.9);
    padding: 123px 100px 45px 48px;
    position: relative;

    @media @mobile {
      width: 100%;
    }

    &:before {
      content: '';
      background: url('/images/combined-shape.svg') no-repeat 0 0;
      position: absolute;
      left: 55px;
      top: -38px;
      width: 119px;
      height: 109px;
      transform: scaleX(-1);
      z-index: 1;
      @media @mobile {
        left: 30px;
      }
    }
    &:after {
      content: '';
      position: absolute;
      background: url('/images/message.svg') no-repeat 0 0;
      left: 72px;
      top: -15px;
      height: 33px;
      width: 35px;
      transform: scaleX(-1);
      z-index: 2;
      @media @mobile {
        left: 48px;
      }
    }

    &_img {
      width: 388px;
      height: 227px;
      border-radius: 20px;
      position: absolute;
      display: block;
      top: -127px;
      right: 40px;
      background: rgba(245, 245, 245, 0.7);
      @media @mobile {
        width: 55%;
        top: -38px;
        right: 30px;
        height: auto;
      }
    }
    &_ttl {
      margin-bottom: 19px;
    }
    &_txt {
      margin-bottom: 13px;
    }
    &_link {
      font-weight: bold;
      text-decoration: none;
    }
  }
  &__themas_and_disciplines {
    width: 80%;
    @media @mobile {
      width: 100%;
    }
  }
  &__collections {
    margin-bottom: 20px;
  }
}
</style>
