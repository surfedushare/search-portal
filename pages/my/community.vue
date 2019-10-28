
<template>
  <section class="container main communities">
    <div class="center_block">
      <div class="communities__info">
        <img
          src="/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="/images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
         /images/pictures/rawpixel-760027-unsplash@3x.jpg 3x"
          class="communities__info_bg">
        <BreadCrumbs
          :items="[{title: $t('Home'), url: localePath('index')}]"
        />
        <h2 class="communities__info_ttl">{{ $t('My-community') }}</h2>
      </div>
      <div class="communities__form">
        <form
          action="/"
          class="communities__form_in"
          @submit.prevent="onSubmit"
        >
          <div class="communities__form__column">
            <div class="communities__form__row">
              <label
                for="name"
                class="communities__form__label"
              >
                {{ $t('Name') }}
              </label>
              <input
                required
                id="name"
                v-model="formData.name"
                name="name"
                type="text"
                class="communities__form__input"
              >
            </div>
            <div class="communities__form__row">
              <label
                for="description"
                class="communities__form__label"
              >
                {{ $t('Description') }}
              </label>
              <textarea
                required
                id="description"
                v-model="formData.description"
                name="description"
                required="required"
                class="communities__form__textarea"
              />
            </div>
            <div class="communities__form__row">
              <label
                for="website"
                class="communities__form__label"
              >
                {{ $t('Website') }}
              </label>
              <input
                id="website"
                v-model="formData.website_url"
                name="website"
                type="text"
                class="communities__form__input"
                placeholder="Geef hier de URL "
              >
            </div>
          </div>
          <div class="communities__form__column">
            <div class="communities__form__row communities__form__file">
              <InputFile
                ref="file-logo"
                :imagesrc="formData.logo"
                :title="$t('Logo')"
              />
            </div>
            <div class="communities__form__row communities__form__file">
              <InputFile
                ref="file-img"
                :imagesrc="formData.featured_image"
                :title="$t('Featured-image')"
              />
            </div>
          </div>
          <div class="communities__form__buttons">
            <div
              v-if="is_saved"
              class="success" >
              &#10004; {{ $t('Data-saved') }}
            </div>
            <button
              :disabled="is_submitting"
              type="submit"
              class="button communities__form__button"
            >
              {{ $t('save') }}
            </button>
          </div>
        </form>
      </div>
      <div class="communities__collections">
        <div class="collections__add">
          <button
            class="collections__add__link button"
            @click.prevent="showAddCollection"
          >
            {{ $t('New-collection') }}
          </button>
        </div>
        <div
          v-infinite-scroll="loadMore"
          infinite-scroll-disabled="community_collections_loading"
          infinite-scroll-distance="10"
        >
          <Collections
            v-if="community_collections"
            :collections="community_collections.results"
            :loading="community_collections_loading"
          >
            <template slot="header-info">
              <h2>{{ $t('Collections-2') }}</h2>
            </template>
          </Collections>
        </div>
        <AddCollection
          v-if="isShow"
          :close="close"
          :is-show="isShow"
          :is-shared="true"
          submit-method="postCommunityCollection"
          @submitted="saveCollection"
        />
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import Materials from '~/components/Materials';
import Collections from '~/components/Collections';
import Search from '~/components/FilterCategories/Search';
import AddCollection from '~/components/Popup/AddCollection';
import InputFile from '~/components/InputFile';

export default {
  components: {
    Collections,
    BreadCrumbs,
    Materials,
    Search,
    AddCollection,
    InputFile
  },
  data() {
    return {
      is_saved: false,
      is_submitting: false,
      isShow: false,
      image_logo: '',
      formData: {
        name: '',
        description: '',
        website_url: '',
        logo: false,
        featured_image: false
      }
    };
  },
  computed: {
    ...mapGetters([
      'community_collections',
      'community_collections_loading',
      'communities',
      'isAuthenticated',
      'user_loading',
      'user',
      'getUserCommunities'
    ])
  },

  mounted() {
    if(!this.isAuthenticated && !this.user_loading) {
      this.$router.push('/');
      return;
    }
    this.$store.dispatch('getCommunities').then(() => {
      this.setInitialFormData();
    });

  },
  methods: {
    setInitialFormData() {

      if(!this.user) {
        this.formData = {
          name: '',
          description: '',
          website_url: '',
          logo: false,
          featured_image: false
        }
      }

      let communities = this.getUserCommunities(this.user);
      let community = _.find(communities, (community) => {
        return community.id === this.$route.params.community;
      });

      this.formData.id = community.id;
      this.formData.name = community.name;
      this.formData.description = community.description;
      this.formData.website_url = community.website_url;
      this.formData.logo = community.logo;
      this.formData.featured_image = community.featured_image;

    },
    /**
     * Load next collections
     */
    loadMore() {
      const { community_collections, community_collections_loading } = this;
      if (
        community_collections &&
        community_collections.next &&
        !community_collections_loading
      ) {
        this.$store.dispatch('getCommunityCollectionsNextPage');
      }
    },
    /**
     * Show the popup 'Add collection'
     */
    showAddCollection() {
      this.isShow = true;
    },
    /**
     * Close the popup 'Add collection'
     */
    close() {
      this.isShow = false;
    },
    addCollection() {},
    /**
     * Save community data
     */
    onSubmit() {
      this.error = null;
      this.is_submitting = true;

      const data = this.normalizeFormData();
      this.$store
        .dispatch('putCommunities', {
          id: this.formData.id,
          data: data
        })
        .then(() => {
          this.is_submitting = false;
          this.is_saved = true;
          setTimeout(() => {
            this.is_saved = false;
          }, 1000);
        })
        .catch(err => {
          this.error = err;
          this.is_submitting = false;
        });
    },
    /**
     * Generate the FormData
     * @returns {FormData}
     */
    normalizeFormData() {
      let data = new FormData();

      for (let item in this.formData) {
        const el = this.formData[item];
        if (el) {
          if (Array.isArray(el)) {
            data.append(item, JSON.stringify(el));
          } else {
            let ElValue = el ? el : null;
            data.append(item, ElValue);
          }
        }
      }

      if (
        this.$refs['file-logo'].$el.querySelector('input[type="file"]').files[0]
      ) {
        data.set(
          'logo',
          this.$refs['file-logo'].$el.querySelector('input[type="file"]')
            .files[0]
        );
      } else {
        data.set('logo', '');
      }
      if (
        this.$refs['file-img'].$el.querySelector('input[type="file"]').files[0]
      ) {
        data.set(
          'featured_image',
          this.$refs['file-img'].$el.querySelector('input[type="file"]')
            .files[0]
        );
      } else {
        data.set('featured_image', '');
      }
      return data;
    },
    saveCollection(collection) {
      this.$store.dispatch('setCommunityCollection', {
        id: this.formData.id,
        data: [
          {
            id: collection.id
          }
        ]
      });
    }
  }
};
</script>
<style lang="less">
@import './../../assets/styles/variables';
.communities {
  width: 100%;
  padding: 119px 0 47px;

  &__info {
    padding: 64px 38px 0;
    margin: 0 0 93px;
    border-radius: 20px;
    position: relative;
    min-height: 271px;

    &_bg {
      position: absolute;
      right: 26px;
      top: -57px;
      width: 50%;
      border-radius: 21px;
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
      margin: 0 65px;
      .search__fields {
        margin-bottom: 33px;
      }
    }
  }
  &__form {
    margin-bottom: 146px;
    &_in {
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
    }
    &__column {
      width: 45%;
      padding-left: 53px;
      &:first-child {
        width: 55%;
        padding-right: 32px;
        padding-left: 0;
      }
    }
    &__row {
      width: 100%;
      margin-bottom: 16px;
    }
    &__label {
      font-weight: bold;
      color: #353535;
      font-family: @second-font;
      display: block;
      margin-bottom: 8px;
    }
    &__input {
      border: 1px solid #bcbfc2;
      width: 100%;
      border-radius: 7px;
      padding: 12px 24px;
      font-size: 16px;
      line-height: 1.44;
      color: #686d75;
      &:focus {
        outline: none;
      }
    }
    &__textarea {
      border: 1px solid #bcbfc2;
      border-radius: 7px;
      padding: 12px 24px;
      width: 100%;
      height: 110px;
      font-size: 16px;
      line-height: 1.44;
      resize: none;
      color: #686d75;
      &:focus {
        outline: none;
      }
    }
    &__buttons {
      text-align: right;
      width: 100%;
      margin: 10px 0 0;
      .success {
        display: inline-block;
        margin: 0 20px 0 0;
        color: #008800;
      }
    }
    &__button {
      padding: 13px 60px;
    }
  }
  &__collections {
    margin: 0 0 175px;
  }
}
.collections__add {
  display: flex;
  justify-content: flex-end;
  margin-bottom: -55px;
  position: relative;

  &__link {
    padding: 13px 43px 13px 51px;
    background-image: url('/images/plus-black.svg');
    background-position: 10px 50%;
    background-repeat: no-repeat;
    background-size: 24px 24px;
  }
}
</style>
