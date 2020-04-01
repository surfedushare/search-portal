
<template>
  <section class="container main communities">
    <div v-if="!formData">
      <error status-code="404" message-key="community-not-found"></error>
    </div>
    <div v-else>
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
          <div
            v-if="is_saved"
            class="success" >
            &#10004; {{ $t('Data-saved') }}
          </div>
          <div
            v-show="anyFieldError()"
            >{{ $t('any-field-error') }}
          </div>

          <div >
            <section class="communities__section__blue_box">
              <form
                action="/"
                @submit.prevent="onSubmit"
              >
                <div class="communities__form__buttons">
                  <switch-input :label="$t('public')" v-model="isPublished"/>
                  &nbsp;&nbsp; <router-link :to="getPreviewPath()"><i class="fas fa-eye"></i> {{$t('example')}}</router-link> &nbsp;&nbsp;&nbsp;&nbsp;
                  <button
                    :disabled="is_submitting"
                    type="submit"
                    class="button communities__form__button"
                  >
                    {{ $t('save') }}
                  </button>
                </div>
              </form>
            </section>
          </div>
        </div>

        <div class="tab">
          <button class="tablinks" ref="general-button" @click="openTab('General')">{{$t('general')}}</button>
          <button class="tablinks" ref="collections-button" @click="openTab('Collections')">{{$t('collections')}}</button>
        </div>

        <div class="communities__form tabcontent" id="General" ref="general-tab">
          <div><h1>{{$t('general')}}</h1>
            {{$t('manage-community-information')}}
            <br /><br />
          </div>
          <div>
            <h3>{{$t('dutch')}}</h3>
            <hr>
            <br /><br />
          </div>
          <form
            action="/"
            class="communities__form_in"
            @submit.prevent="onSubmit"
          >

            <div class="communities__form__column">
              <div class="communities__form__row" :class="{field: true, invalid: isFieldValid('title_nl')}">
                <label
                  for="title_nl"
                  class="communities__form__label"
                >
                  {{ $t('Name') }}
                </label>
                <input
                  required
                  id="title_nl"
                  v-model="formData.title_nl"
                  name="name"
                  type="text"
                  class="communities__form__input"
                  :placeholder="$t('community-title-placeholder')"
                >
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('title_nl')" :key="ix">{{ error }}</li>
                </ul>
              </div>

              <div class="communities__form__row" :class="{field: true, invalid: isFieldValid('website_url_nl')}">
                <label
                  for="website_nl"
                  class="communities__form__label"
                >
                  {{ $t('Website') }}
                </label>
                <input
                  id="website_nl"
                  v-model="formData.website_url_nl"
                  name="website"
                  type="url"
                  class="communities__form__input"
                  :placeholder="$t('community-url-placeholder')"
                >
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('website_url_nl')" :key="ix">{{ error }}</li>
                </ul>
              </div>
              <div class="communities__form__row communities__form__file"
                   :class="{field: true, invalid: isFieldValid('logo_nl')}">
                <InputFile
                  ref="file-logo_nl"
                  :imagesrc="formData.logo_nl"
                  :title="$t('Logo')"
                  @remove_image="onRemoveImage('logo_nl', $event)"
                  @add_image="onAddImage('logo_nl', $event)"
                />
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('logo_nl')" :key="ix">{{ error }}</li>
                </ul>
              </div>
            </div>
            <div class="communities__form__column">
              <div class="communities__form__row" :class="{field: true, invalid: isFieldValid('description_nl')}">
                <label
                  for="description_nl"
                  class="communities__form__label"
                >
                  {{ $t('Description') }}
                </label>
                <textarea
                  required
                  id="description_nl"
                  v-model="formData.description_nl"
                  name="description"
                  class="communities__form__textarea"
                  :placeholder="$t('community-description-placeholder')"
                />
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('description_nl')" :key="ix">{{ error }}</li>
                </ul>
              </div>
              <div class="communities__form__row communities__form__file"
                   :class="{field: true, invalid: isFieldValid('featured_image_nl')}">
                <InputFile
                  ref="file-img_nl"
                  :imagesrc="formData.featured_image_nl"
                  :title="$t('Featured-image')"
                  @remove_image="onRemoveImage('featured_nl', $event)"
                  @add_image="onAddImage('featured_nl', $event)"
                />
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('featured_image_nl')" :key="ix">{{ error }}</li>
                </ul>
              </div>
            </div>

          </form>
          <div>
            <br/><br/>
            <h3>{{$t('english')}}</h3>
            <hr>
            <br /><br />
          </div>
          <form
            action="/"
            class="communities__form_in"
            @submit.prevent="onSubmit"
          >

            <div class="communities__form__column">
              <div class="communities__form__row" :class="{field: true, invalid: isFieldValid('title_en')}">
                <label
                  for="title_en"
                  class="communities__form__label"
                >
                  {{ $t('Name') }}
                </label>
                <input
                  required
                  id="title_en"
                  v-model="formData.title_en"
                  name="name"
                  type="text"
                  class="communities__form__input"
                  :placeholder="$t('community-title-placeholder')"
                >
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('title_en')" :key="ix">{{ error }}</li>
                </ul>
              </div>

              <div class="communities__form__row" :class="{field: true, invalid: isFieldValid('website_url_en')}">
                <label
                  for="website_en"
                  class="communities__form__label"
                >
                  {{ $t('Website') }}
                </label>
                <input
                  id="website_en"
                  v-model="formData.website_url_en"
                  name="website"
                  type="url"
                  class="communities__form__input"
                  :placeholder="$t('community-url-placeholder')"
                >
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('website_url_en')" :key="ix">{{ error }}</li>
                </ul>
              </div>
              <div class="communities__form__row communities__form__file"
                   :class="{field: true, invalid: isFieldValid('logo_en')}">
                <InputFile
                  ref="file-logo_en"
                  :imagesrc="formData.logo_en"
                  :title="$t('Logo')"
                  @remove_image="onRemoveImage('logo_en', $event)"
                  @add_image="onAddImage('logo_en', $event)"
                />
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('logo_en')" :key="ix">{{ error }}</li>
                </ul>
              </div>
            </div>
            <div class="communities__form__column">
              <div class="communities__form__row" :class="{field: true, invalid: isFieldValid('description_en')}">
                <label
                  for="description_en"
                  class="communities__form__label"
                >
                  {{ $t('Description') }}
                </label>
                <textarea
                  required
                  id="description_en"
                  v-model="formData.description_en"
                  name="description"
                  class="communities__form__textarea"
                  :placeholder="$t('community-description-placeholder')"
                />
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('description_en')" :key="ix">{{ error }}</li>
                </ul>
              </div>
              <div class="communities__form__row communities__form__file"
                   :class="{field: true, invalid: isFieldValid('featured_image_en')}">
                <InputFile
                  ref="file-img_en"
                  :imagesrc="formData.featured_image_en"
                  :title="$t('Featured-image')"
                  @remove_image="onRemoveImage('featured_en', $event)"
                  @add_image="onAddImage('featured_en', $event)"
                />
                <ul class="errors">
                  <li v-for="(error, ix) in getFieldErrors('featured_image_en')" :key="ix">{{ error }}</li>
                </ul>
              </div>
            </div>

          </form>

        </div>
        <div class="communities__collections tabcontent" id="Collections" ref="collections-tab">
          <br/><br/>
          <div class="collections__add">
            <button
              class="collections__add__link button"
              @click.prevent="showAddCollection"
            >
              {{ $t('New-collection') }}
            </button>
          </div>
          <div>
            <Collections
              v-if="community_collections"
              :collections="community_collections.results"
              :editable-content="true"
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
            submit-method="postCommunityCollection"
            @submitted="saveCollection"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import _ from 'lodash';
import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import Collections from '~/components/Collections';
import AddCollection from '~/components/Popup/AddCollection';
import InputFile from '~/components/InputFile';
import Error from '~/components/error';
import SwitchInput from '~/components/switch-input';
import { PublishStatus } from "~/utils";


export default {
  components: {
    Error,
    Collections,
    BreadCrumbs,
    AddCollection,
    InputFile,
    SwitchInput
  },
  data() {
    return {
      is_saved: false,
      is_submitting: false,
      isShow: false,
      image_logo: '',
      errors: {
        title_nl: '',
        title_en: '',
        description_nl: '',
        description_en: '',
        website_url_nl: '',
        website_url_en: '',
        logo_nl: false,
        logo_en: false,
        featured_image_nl: false,
        featured_image_en: false,
      },
      formData: {
        title_nl: '',
        title_en: '',
        description_nl: '',
        description_en: '',
        website_url_nl: '',
        website_url_en: '',
        logo_nl: false,
        logo_en: false,
        featured_image_nl: false,
        featured_image_en: false,
        publish_status: PublishStatus.DRAFT
      }
    };
  },
  computed: {
    ...mapGetters([
      'community_collections',
      'community_collections_loading',
      'communities',
      'isAuthenticated',
      'user',
      'getUserCommunities'
    ]),
    isPublished: {
      get() {
        return this.formData.publish_status === PublishStatus.PUBLISHED;
      },
      set(value) {
        this.formData.publish_status = (value) ? PublishStatus.PUBLISHED : PublishStatus.DRAFT;
      }
    }
  },
  mounted() {
    if(!this.isAuthenticated) {
      this.$router.push('/');
      return;
    }
    this.$store.dispatch('getCommunities').then(() => {
      this.setInitialFormData();
    });
    this.$store.dispatch('getCommunityCollections', this.$route.params.community);
    // Open the 'general' tab by default
    this.openTab("General");
  },
  methods: {
    getFieldErrors(fieldName){
      return this.errors[fieldName];
    },
    isFieldValid(fieldName){
      return this.getFieldErrors(fieldName).length > 0
    },
    anyFieldError(){
      return _.some(this.errors, item => item.length > 0);
    },
    onRemoveImage(context){
      switch(context) {
        case 'logo_nl':
          this.logo_nl_deleted = true;
          this.logo_nl_added = false;
          break;
        case 'logo_en':
          this.logo_en_deleted = true;
          this.logo_en_added = false;
          break;
        case 'featured_nl':
          this.featured_nl_deleted = true;
          this.featured_nl_added = false;
          break;
        case 'featured_en':
          this.featured_en_deleted = true;
          this.featured_en_added = false;
          break;
      }
    },
    onAddImage(context){
      if (context === 'logo_nl'){
        this.logo_nl_deleted = false;
        this.logo_nl_added = true;
      }
      if (context === 'featured_nl'){
        this.featured_nl_deleted = false;
        this.featured_nl_added = true;
      }
      if (context === 'logo_en'){
        this.logo_en_deleted = false;
        this.logo_en_added = true;
      }
      if (context === 'featured_en'){
        this.featured_en_deleted = false;
        this.featured_en_added = true;
      }
    },
    setInitialFormData() {

      if(!this.user) {
        this.formData = {};
        return;
      }

      let communities = this.getUserCommunities(this.user);
      let community = _.find(communities, (community) => {
        return community.id === this.$route.params.community;
      });

      if(_.isNil(community)) {
        this.formData = {};
        return;
      }
      if(!_.isNil(community.community_details)){
        _.forEach(community.community_details, detail => {
          if (detail.language_code === 'NL'){
            this.formData.title_nl = detail.title;
            this.formData.description_nl = detail.description;
            this.formData.website_url_nl = detail.website_url;
            this.formData.logo_nl = detail.logo;
            this.formData.featured_image_nl = detail.featured_image;
          }
          else if (detail.language_code === 'EN'){
            this.formData.title_en = detail.title;
            this.formData.description_en = detail.description;
            this.formData.website_url_en = detail.website_url;
            this.formData.logo_en = detail.logo;
            this.formData.featured_image_en = detail.featured_image;
          }
        });
      }
      this.formData.external_id = community.id;
      this.formData.publish_status = community.publish_status;
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
      _.forEach(this.errors, (value, key) => {
          this.errors[key] = '';
      });
      this.$store
        .dispatch('putCommunities', {
          id: this.formData.external_id,
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
          _.forEach(err.response.data, (feedback, language) => {
            const response = JSON.parse(feedback.replace(/'/g, "\""));
            _.forEach(response, (item, key) => {
              const error_msg = item;
              let location = key + '_' + language.toLowerCase();
              this.errors[location] = error_msg;
            });
          });
        });
    },
    openTab(tabName) {
      let generaltab = this.$refs["general-tab"];
      let generalbutton = this.$refs["general-button"];
      let collectionstab = this.$refs["collections-tab"];
      let collectionsbutton = this.$refs["collections-button"];
      switch (tabName) {
        case "General":
          generaltab.style.display = "block";
          generalbutton.className += " active";
          collectionstab.style.display = "none";
          collectionsbutton.className -= " active";
          break;
        case "Collections":
          collectionstab.style.display = "block";
          collectionsbutton.className += " active";
          generaltab.style.display = "none";
          generalbutton.className -= " active";
          break;
      }
    },
    /**
     * Generate the FormData
     * @returns {FormData}
     */
    normalizeFormData() {
      let data = new FormData();
      let data_nl = {language_code: 'NL'};
      let data_en = {language_code: 'EN'};

      _.forEach(this.formData, (element, key) => {
        if (!_.isNil(element)) {
          let value = element;
          if (Array.isArray(element)) {
            value = JSON.stringify(element);
          }
          if (!_.startsWith(key, 'logo') && !_.startsWith(key, 'featured')){
            if (_.endsWith(key, '_nl')) {
              data_nl[key.slice(0, -3)] = value;
            } else if (_.endsWith(key, '_en')) {
              data_en[key.slice(0, -3)] = value;
            }
          }
          data.append(key, value);
        }
        // if the value is empty, send it to the backend (so the backend can reject the post)
        else {
          if (_.endsWith(key, '_nl')) {
              data_nl[key.slice(0, -3)] = "";
          } else if (_.endsWith(key, '_en')) {
              data_en[key.slice(0, -3)] = "";
          }
        }
      });
      let deleted_logos = [];
      data.set('logo_nl', '');
      if (this.logo_nl_added) {
        let logo = this.$refs['file-logo_nl'].$el.querySelector('input[type="file"]').files[0];
        data.set('logo_nl', logo);
      }
      else if (this.logo_nl_deleted) {
        deleted_logos.push('logo_nl');
      } else {
        data.delete('logo_nl');
      }

      data.set('logo_en', '');
      if (this.logo_en_added) {
        data.set('logo_en', this.$refs['file-logo_en'].$el.querySelector('input[type="file"]').files[0]);
      }
      else if (this.logo_en_deleted) {
        deleted_logos.push('logo_en');
      } else {
        data.delete('logo_en');
      }

      data.set('featured_image_nl', '');
      if (this.featured_nl_added) {
        data.set('featured_image_nl', this.$refs['file-img_nl'].$el.querySelector('input[type="file"]').files[0]);
      }
      else if (this.featured_nl_deleted) {
        deleted_logos.push('featured_image_nl');
      } else {
        data.delete('featured_image_nl');
      }

      data.set('featured_image_en', '');
      if (this.featured_en_added) {
        data.set('featured_image_en', this.$refs['file-img_en'].$el.querySelector('input[type="file"]').files[0]);
      }
      else if (this.featured_en_deleted) {
        deleted_logos.push('featured_image_en');
      } else {
        data.delete('featured_image_en');
      }

      data.append('community_details_update', JSON.stringify([data_nl, data_en]));
      data.append('deleted_logos', JSON.stringify(deleted_logos));
      return data;
    },
    saveCollection(collection) {
      this.$store.dispatch('setCommunityCollection', {
        id: this.$route.params.community,
        data: [
          {
            id: collection.id,
            title: collection.title
          }
        ]
      });
    },
    getPreviewPath() {
      return this.localePath({
        name: 'communities-community',
        params: {
          community: this.formData.external_id
        }
      })
    }
  }
};
</script>
<style lang="less">
@import './../../variables';
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
  &__section {
    &__blue_box{
      line-height: 75px;
      border: 1px;
      background: @dark-blue;
      width: 40%;
      min-width: 440px;  // or break tablets
      height: 75px;
      border-radius: 20px;
      margin-top: 25px;
      color: white;
      font-size: 18px;
      font-weight: 600;
      a:link{
        color:white;
        text-decoration: none;
      }
      a:visited{
        color:white;
        text-decoration: none;
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
      width: 50%;
      padding-left: 53px;
      &:first-child {
        width: 50%;
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
    &__feedback {
      color: red;
      font-size: 14px;
      padding-left: 10px;
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
      height: 143px;
      font-size: 16px;
      line-height: 1.44;
      resize: none;
      color: #686d75;
      font-family: inherit;
      &:focus {
        outline: none;
      }
    }
    &__buttons {
      text-align: right;
      width: 100%;
      margin: 10px 0 0;
    }
    &__button {
      margin-right: 10px;
      margin-top: 10px;
      height: 55px;
      float: right;
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

@active-tab-indicator-size: 15px;

/* Style the tab */
.tab {
  overflow: hidden;
  padding-bottom: @active-tab-indicator-size;
}

/* Style the buttons that are used to open the tab content */
.tab button {
  position:relative;
  border-radius: 5px;
  background-color: inherit;
  float: left;
  border: 1px solid #ccc;
  outline: none;
  cursor: pointer;
  padding: 14px 50px;
  margin: 0 25px;
  transition: 0.3s;
  font-size: 16px;
  font-weight: bold;
}

/* Change background color of buttons on hover */
.tab button:hover {
  background-color: cornflowerblue;
}

/* Create an active/current tablink class */
.tab button.active {
  background-color: @dark-blue;
  color: white;
}
.tab button.active:after {
  content:'';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -1 * @active-tab-indicator-size;
  width: 0;
  height: 0;
  border-top: solid @active-tab-indicator-size @dark-blue;
  border-left: solid @active-tab-indicator-size transparent;
  border-right: solid @active-tab-indicator-size transparent;
}


/* Style the tab content */
.tabcontent {
  display: none;
  padding: 6px 12px;
  border-top: none;
}

.success {
  display: inline-block;
  color: #008800;
}

.errors {
  color: red;
  font-size: 14px;
  display:none;
  list-style-type: none;
  padding-top: 5px;
  margin-left: -20px;
}
.field.invalid .errors{
  display: block;
}
</style>
