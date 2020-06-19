<template>
  <section class="container main themes">
    <div v-if="!theme && !isLoading">
      <error status-code="404" message-key="theme-not-found"></error>
    </div>
    <div v-else-if="theme && !isLoading" class="theme">
      <div class="center_block center-header">
        <div class="theme__info ">
          <img
            src="/images/pictures/rawpixel-760027-unsplash.jpg"
            srcset="
              /images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
              /images/pictures/rawpixel-760027-unsplash@3x.jpg 3x
            "
            class="theme__info_bg"
          />
          <BreadCrumbs
            :items="[{ title: $t('Home'), url: localePath('index') }]"
          />
          <h2 class="theme__info_ttl">
            {{ getTitleTranslation(theme, $i18n.locale) }}
          </h2>
          <Search
            class="theme__info_search"
            :placeholder="$t('Search-in-theme')"
            v-model="search"
            active-category-external-id="lom.technical.format"
          />
        </div>
      </div>
      <div class="center_block theme__row">
        <div class="theme__description">
          <h2>
            {{ $t('About-the-theme') }} <br />{{
              getTitleTranslation(theme, $i18n.locale)
            }}
          </h2>
          <p>
            <span
              class="html-content"
              v-html="getDescriptionTranslation(theme, $i18n.locale)"
            >
            </span>
          </p>
        </div>
        <Disciplines
          class="theme__disciplines"
          :disciplines="themeDisciplines"
          :theme="theme"
        />
      </div>
      <div class="theme__materials_and_communities theme__row center_block">
        <Collections
          :collections="themeCollections"
          :items-in-line="2"
          class="theme__materials"
        >
          <template slot="header-info">
            <h2>{{ $t('Collections-2') }}</h2>
          </template>
        </Collections>

        <PopularList class="theme__communities" :communities="themeCommunities">
          <template slot="header-info">
            <h2>{{ $t('Communities') }}</h2>
            <div class="popular-list__description">
              {{ $t('Subject-communities-within-the-theme') }}
              {{ getTitleTranslation(theme, $i18n.locale) }}
            </div>
          </template>
        </PopularList>
      </div>
      <div class="theme__collections theme__row center_block">
        <Materials
          :materials="materials"
          :items-in-line="4"
          class="theme__materials"
        >
          <template slot="header-info">
            <h2>{{ $t('Newest-open-learning-material-for-theme') }}</h2>
            <p class="materials__description">
              {{ $t('Featured-learning-materials-in-the-theme') }}
              {{ getTitleTranslation(theme, $i18n.locale) }}
            </p>
          </template>
        </Materials>
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'
import _ from 'lodash'
import Search from '~/components/FilterCategories/Search'
import PopularList from '~/components/Communities/PopularList'
import Materials from '~/components/Materials'
import Disciplines from '~/components/Disciplines'
import Collections from '~/components/Collections'
import BreadCrumbs from '~/components/BreadCrumbs'
import Error from '~/components/error'

export default {
  name: 'theme',
  props: [],
  components: {
    Search,
    PopularList,
    Materials,
    Disciplines,
    Collections,
    BreadCrumbs,
    Error
  },
  mounted() {
    let themeId = this.$route.params.id

    this.$store.dispatch('getFilterCategories').then(() => {
      this.$store
        .dispatch('getTheme', themeId)
        .then(theme => {
          let themeCategory = this.$store.getters.getCategoryById(
            theme.external_id
          )
          themeCategory.selected = true

          this.theme = theme
          this.$store.dispatch('searchMaterials', {
            page_size: 4,
            search_text: [],
            ordering: '-lom.lifecycle.contribute.publisherdate',
            filters: this.$store.getters.search_filters,
            return_filters: false
          })
        })
        .finally(() => {
          this.isLoading = false
        })
    })

    // TODO: all data fetched below is also in the getFilterCategories above
    // We should remove these calls and use the getFilterCategories
    // That means switching from theme.id to theme.external_id
    this.$store.dispatch('getThemeDisciplines', themeId)
    this.$store.dispatch('getThemeCommunities', {
      id: this.$route.params.id,
      params: { page_size: 2 }
    })
    this.$store.dispatch('getThemeCollections', themeId)
  },
  data() {
    return {
      isLoading: true,
      search: {
        filters: [
          {
            external_id: 'lom.technical.format',
            items: []
          }
        ]
      }
    }
  },
  methods: {
    getTitleTranslation(theme, language) {
      if (
        !_.isNil(theme.title_translations) &&
        !_.isEmpty(theme.title_translations)
      ) {
        return theme.title_translations[language]
      }
      return theme.title
    },
    getDescriptionTranslation(theme, language) {
      if (
        !_.isNil(theme.description_translations) &&
        !_.isEmpty(theme.description_translations)
      ) {
        return theme.description_translations[language]
      }
      return theme.description
    }
  },
  computed: {
    ...mapGetters([
      'theme',
      'themeDisciplines',
      'themeCommunities',
      'themeCollections',
      'materials',
      'filter'
    ])
  }
}
</script>

<style scoped lang="less">
@import url('../variables');
.theme {
  padding: 96px 0 152px;
  @media @mobile {
    overflow: hidden;
  }
  &__info {
    h2 {
      @media @mobile {
        font-size: 26px;
      }
    }

    padding: 64px 48px 0;
    margin: 0 0 125px;
    border-radius: 20px;
    position: relative;
    @media @mobile {
      margin: -20px -20px -100px;
    }
    &_bg {
      position: absolute;
      right: 26px;
      top: -51px;
      width: 50%;
      border-radius: 21px;
      @media @mobile {
        padding: 0;
        z-index: -1;
        right: -20px;
      }
      @media @mobile {
        right: -50px;
      }
    }
    &_ttl {
      padding: 0 0 55px;
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
      margin: 0 56px;
      .search__fields {
        @media @desktop {
          margin-bottom: 33px;
        }
      }
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
    }
  }
  &__row {
    justify-content: space-between;
    @media @desktop {
      display: flex;
      margin: 0 auto 114px;
      align-items: flex-start;
    }
  }
  &__description {
    background-color: rgba(244, 244, 244, 0.9);
    position: relative;
    border-radius: 20px;
    padding: 75px 15px 15px 15px;
    margin-bottom: 45px;
    @media @desktop {
      width: calc(50% - 37px);
      margin: 40px 0 0 23px;
      padding: 66px 26px 67px 79px;
    }

    h2 {
      line-height: 1.2;
      margin-bottom: 17px;
    }

    &:before {
      content: '';
      background: url('/images/combined-shape.svg') no-repeat 0 0;
      position: absolute;
      left: -23px;
      top: -40px;
      width: 119px;
      height: 109px;
    }
    &:after {
      content: '';
      position: absolute;
      background: url('/images/message.svg') no-repeat 0 0;
      left: 44px;
      top: -17px;
      height: 33px;
      width: 35px;
    }
  }
  &__disciplines {
    @media @desktop {
      width: calc(50% - 60px);
      padding: 29px 10px 0 54px;
    }
  }
  &__materials_and_communities {
    display: none;
    margin: 0 auto 99px;
  }
  &__materials {
    @media @desktop {
      width: calc(100% - 15px);
    }
  }
  &__communities {
    @media @desktop {
      width: calc(50% - 115px);
    }
  }
  &__collections {
    width: 100%;
    margin: 0 auto;
  }
}
</style>
