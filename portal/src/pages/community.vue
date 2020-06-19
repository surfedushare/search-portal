<template>
  <section class="container main">
    <section class="community">
      <div v-if="!community_details">
        <error status-code="404" message-key="community-not-found" />
      </div>
      <div v-else>
        <div class="center_block">
          <InfoBlock
            :title="community_details.title"
            :content="community_details.description"
            :website_url="community_details.website_url"
            :breadcrumb_items="[
              { title: $t('Home'), url: localePath('index') },
              { title: $t('Communities'), url: localePath('communities') }
            ]"
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
              </template>
            </Collections>
            <Spinner v-if="community_collections_loading" />
          </div>
          <Materials
            v-show="false"
            :materials="materials"
            class="community__materials"
          >
            <template slot="header-info">
              <h2>{{ $t('Newest-open-learning-material') }}</h2>
            </template>
          </Materials>

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
import InfoBlock from '~/components/InfoBlock'
import Themes from '~/components/Themes'
import Disciplines from '~/components/Disciplines'
import Collections from '~/components/Collections'
import Materials from '~/components/Materials'
import Spinner from '~/components/Spinner'
import Error from '~/components/error'
import _ from 'lodash'

export default {
  name: 'Community',
  components: {
    Error,
    Themes,
    Disciplines,
    Collections,
    Materials,
    Spinner,
    InfoBlock
  },
  props: [],
  data() {
    return {
      isLoading: true,
      isSearch: false,
      search: false
    }
  },
  computed: {
    ...mapGetters([
      'community_disciplines',
      'community_themes',
      'community_collections_loading',
      'materials',
      'materials_loading',
      'user'
    ]),
    community_collections() {
      let communityCollections = this.$store.getters.getPublicCollections(
        this.user
      )
      return this.isLoading || !_.isEmpty(communityCollections)
        ? communityCollections
        : null
    },
    community_info() {
      let communityInfo = this.$store.getters.getCommunityInfo(this.user)
      return this.isLoading || !_.isEmpty(communityInfo) ? communityInfo : null
    },
    community_details() {
      // Retrieve the details and exit when invalid or loading
      let communityDetails = this.$store.getters.getCommunityDetails(
        this.user,
        this.$i18n.locale
      )
      if (_.isEmpty(communityDetails)) {
        return this.isLoading ? communityDetails || {} : null
      }
      // Fill some defaults for the details
      communityDetails.featured_image =
        communityDetails.featured_image ||
        '/images/pictures/community-default.jpg'
      return communityDetails
    }
  },
  mounted() {
    const { community } = this.$route.params
    this.$store.dispatch('getCommunity', community).finally(() => {
      this.isLoading = false
    })
    this.$store.dispatch('getCommunityThemes', community)
    this.$store.dispatch('getCommunityDisciplines', community)
    this.$store.dispatch('getCommunityCollections', community)
    this.$store.dispatch('searchMaterials', {
      page_size: 4,
      search_text: []
    })
  }
}
</script>

<style lang="less" scoped>
@import url('../variables');
.community {
  padding: 96px 0 131px;
  &:before {
    content: '';
    left: 0;
    right: 50%;
    height: 353px;
    top: 278px;
    border-radius: 0 65px 65px 0;
    margin: 0 428px 0 0;
    pointer-events: none;
    border-right: 1px solid #686d75;
    border-top: 1px solid #686d75;
    border-bottom: 1px solid #686d75;
    position: absolute;
    z-index: -1;
  }
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
      .bread-crumbs {
        margin-bottom: 5px;
      }
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
    margin-bottom: 37px;
  }
}
</style>
