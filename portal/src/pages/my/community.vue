<template>
  <section class="container main communities">
    <div v-if="notFound">
      <error status-code="404" message-key="community-not-found" />
    </div>
    <div v-else>
      <HeaderBlock :title="$t('My-community')" />
      <div class="center_block">
        <section v-if="formData" class="communities__section__blue_box">
          <form action="/" @submit.prevent="onSubmit">
            <div class="communities__form__buttons">
              <switch-input v-model="isPublished" :label="$t('public')" />
              &nbsp;&nbsp;
              <router-link :to="getPreviewPath()">
                <i class="fas fa-eye" /> {{ $t('example') }}
              </router-link>
              &nbsp;&nbsp;&nbsp;&nbsp;
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

        <div class="tab">
          <button
            ref="general-button"
            class="tablinks"
            @click="openTab('General')"
          >
            {{ $t('general') }}
          </button>
          <button
            ref="collections-button"
            class="tablinks"
            @click="openTab('Collections')"
          >
            {{ $t('collections') }}
          </button>
        </div>

        <div
          id="General"
          ref="general-tab"
          class="communities__form tabcontent"
        >
          <div>
            <h1>{{ $t('general') }}</h1>
            {{ $t('manage-community-information') }}
            <br /><br />
          </div>
          <form
            v-if="formData"
            action="/"
            class="communities__form_in"
            @submit.prevent="onSubmit"
          >
            <div class="communities__form__column">
              <div class="communities__form__row">
                <label class="communities__form__label">
                  {{ $t('Name') }}
                </label>
                <ErrorWrapper :errors="getFieldErrors('title_nl')">
                  <InputLanguageWrapper language="NL">
                    <InputWithCounter
                      id="title_nl"
                      v-model="formData.title_nl"
                      required
                      name="name"
                      type="text"
                      maxlength="80"
                      :placeholder="$t('community-title-placeholder')"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
              <div class="communities__form__row">
                <ErrorWrapper :errors="getFieldErrors('title_en')">
                  <InputLanguageWrapper language="EN">
                    <InputWithCounter
                      id="title_en"
                      v-model="formData.title_en"
                      required
                      name="name"
                      type="text"
                      :placeholder="$t('community-title-placeholder')"
                      maxlength="80"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
              <div class="communities__form__row">
                <label class="communities__form__label">
                  {{ $t('Website') }}
                </label>
                <ErrorWrapper :errors="getFieldErrors('website_url_nl')">
                  <InputLanguageWrapper language="NL">
                    <input
                      id="website_nl"
                      v-model="formData.website_url_nl"
                      name="website"
                      type="url"
                      class="communities__form__input"
                      :placeholder="$t('community-url-placeholder')"
                      @blur="onWebsiteURLBlur('nl')"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
              <div class="communities__form__row">
                <ErrorWrapper :errors="getFieldErrors('website_url_en')">
                  <InputLanguageWrapper language="EN">
                    <input
                      id="website_en"
                      v-model="formData.website_url_en"
                      name="website"
                      type="url"
                      class="communities__form__input"
                      :placeholder="$t('community-url-placeholder')"
                      @blur="onWebsiteURLBlur('en')"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
              <div class="communities__form__row communities__form__file">
                <label class="communities__form__label">
                  {{ $t('Logo') }}
                </label>
                <ErrorWrapper :errors="getFieldErrors('logo_nl')">
                  <InputLanguageWrapper language="NL">
                    <InputFile
                      ref="file-logo_nl"
                      :imagesrc="formData.logo_nl"
                      @remove_image="onRemoveImage('logo_nl', $event)"
                      @add_image="onAddImage('logo_nl', $event)"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
              <div class="communities__form__row communities__form__file">
                <ErrorWrapper :errors="getFieldErrors('logo_en')">
                  <InputLanguageWrapper language="EN">
                    <InputFile
                      ref="file-logo_en"
                      :imagesrc="formData.logo_en"
                      @remove_image="onRemoveImage('logo_en', $event)"
                      @add_image="onAddImage('logo_en', $event)"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
            </div>
            <div class="communities__form__column">
              <div class="communities__form__row">
                <ErrorWrapper :errors="getFieldErrors('description_nl')">
                  <RichTextInput
                    v-model="formData.description_nl"
                    :title="$t('Description')"
                    language="NL"
                    :placeholder="$t('community-description-placeholder')"
                  />
                </ErrorWrapper>
              </div>
              <div class="communities__form__row">
                <ErrorWrapper :errors="getFieldErrors('description_en')">
                  <RichTextInput
                    v-model="formData.description_en"
                    language="EN"
                    :placeholder="$t('community-description-placeholder')"
                  />
                </ErrorWrapper>
              </div>
              <div class="communities__form__row communities__form__file">
                <label class="communities__form__label">
                  {{ $t('Featured-image') }}
                </label>
                <ErrorWrapper :errors="getFieldErrors('featured_image_nl')">
                  <InputLanguageWrapper language="NL">
                    <InputFile
                      ref="file-img_nl"
                      :imagesrc="formData.featured_image_nl"
                      @remove_image="onRemoveImage('featured_nl', $event)"
                      @add_image="onAddImage('featured_nl', $event)"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
              <div class="communities__form__row communities__form__file">
                <ErrorWrapper :errors="getFieldErrors('featured_image_en')">
                  <InputLanguageWrapper language="EN">
                    <InputFile
                      ref="file-img_en"
                      :imagesrc="formData.featured_image_en"
                      @remove_image="onRemoveImage('featured_en', $event)"
                      @add_image="onAddImage('featured_en', $event)"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
            </div>
          </form>
        </div>
        <div
          id="Collections"
          ref="collections-tab"
          class="communities__collections tabcontent"
        >
          <br /><br />
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
              @input="setCollectionSelection"
            >
              <template slot="header-info">
                <h2>{{ $t('Collections-2') }}</h2>
              </template>
            </Collections>
          </div>
          <AddCollection
            v-if="showPopup"
            :close="close"
            :show-popup="showPopup"
            submit-method="postCommunityCollection"
            @submitted="saveCollection"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import {
  some,
  isNil,
  isEmpty,
  find,
  forEach,
  startsWith,
  endsWith
} from 'lodash'
import { mapGetters } from 'vuex'
import Collections from '~/components/Collections'
import HeaderBlock from '~/components/HeaderBlock'
import AddCollection from '~/components/Popup/AddCollection'
import InputFile from '~/components/InputFile'
import Error from '~/components/error'
import SwitchInput from '~/components/switch-input'
import RichTextInput from '~/components/RichTextInput'
import InputWithCounter from '~/components/InputWithCounter'
import ErrorWrapper from '~/components/ErrorWrapper'
import InputLanguageWrapper from '~/components/InputLanguageWrapper'
import { PublishStatus } from '~/utils'

const defaultFormData = {
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

export default {
  components: {
    HeaderBlock,
    Error,
    Collections,
    AddCollection,
    InputFile,
    SwitchInput,
    RichTextInput,
    InputWithCounter,
    ErrorWrapper,
    InputLanguageWrapper
  },
  data() {
    return {
      is_submitting: false,
      showPopup: false,
      image_logo: '',
      errors: {},
      formData: null,
      notFound: false
    }
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
        return this.formData.publish_status === PublishStatus.PUBLISHED
      },
      set(value) {
        this.formData.publish_status = value
          ? PublishStatus.PUBLISHED
          : PublishStatus.DRAFT
      }
    }
  },
  mounted() {
    if (!this.isAuthenticated) {
      this.$router.push('/')
      return
    }
    this.$store.dispatch('getCommunities').then(() => {
      this.setInitialFormData()
    })
    this.$store.dispatch(
      'getCommunityCollections',
      this.$route.params.community
    )
    // Open the 'general' tab by default
    this.openTab('General')
  },
  methods: {
    getFieldErrors(fieldName) {
      return this.errors[fieldName]
    },
    isFieldValid(fieldName) {
      return this.getFieldErrors(fieldName) != null
    },
    anyFieldError() {
      return some(this.errors, item => item.length > 0)
    },
    onRemoveImage(context) {
      switch (context) {
        case 'logo_nl':
          this.logo_nl_deleted = true
          this.logo_nl_added = false
          break
        case 'logo_en':
          this.logo_en_deleted = true
          this.logo_en_added = false
          break
        case 'featured_nl':
          this.featured_nl_deleted = true
          this.featured_nl_added = false
          break
        case 'featured_en':
          this.featured_en_deleted = true
          this.featured_en_added = false
          break
      }
    },
    onAddImage(context) {
      if (context === 'logo_nl') {
        this.logo_nl_deleted = false
        this.logo_nl_added = true
      }
      if (context === 'featured_nl') {
        this.featured_nl_deleted = false
        this.featured_nl_added = true
      }
      if (context === 'logo_en') {
        this.logo_en_deleted = false
        this.logo_en_added = true
      }
      if (context === 'featured_en') {
        this.featured_en_deleted = false
        this.featured_en_added = true
      }
    },
    setInitialFormData() {
      if (!this.user) {
        this.notFound = true
        return
      }

      const communities = this.getUserCommunities(this.user)
      const community = find(communities, community => {
        return community.id === this.$route.params.community
      })

      if (!community) {
        this.notFound = true
        return
      }
      if (community.community_details) {
        const formData = {
          external_id: community.id,
          publish_status: community.publish_status
        }
        community.community_details.forEach(detail => {
          if (detail.language_code === 'NL') {
            formData.title_nl = detail.title
            formData.description_nl = detail.description
            formData.website_url_nl = detail.website_url
            formData.logo_nl = detail.logo
            formData.featured_image_nl = detail.featured_image
          } else if (detail.language_code === 'EN') {
            formData.title_en = detail.title
            formData.description_en = detail.description
            formData.website_url_en = detail.website_url
            formData.logo_en = detail.logo
            formData.featured_image_en = detail.featured_image
          }
        })
        this.formData = formData
      } else {
        this.formData = defaultFormData
      }
    },
    showAddCollection() {
      this.showPopup = true
    },
    close() {
      this.showPopup = false
    },
    addCollection() {},
    /**
     * Save community data
     */
    onSubmit() {
      this.is_submitting = true

      const data = this.normalizeFormData()
      this.errors = {}
      this.$store
        .dispatch('putCommunities', {
          id: this.formData.external_id,
          data: data
        })
        .then(() => {
          this.is_submitting = false
          this.$store.commit('ADD_MESSAGE', {
            level: 'info',
            message: 'Data-saved'
          })
        })
        .catch(err => {
          this.is_submitting = false
          if (err.response.data) {
            this.$store.commit('ADD_MESSAGE', {
              level: 'error',
              message: 'any-field-error'
            })
          }
          const errors = {}
          forEach(err.response.data, (feedback, language) => {
            const response = JSON.parse(feedback.replace(/'/g, '"'))
            forEach(response, (errorMsg, key) => {
              let location = key + '_' + language.toLowerCase()
              errors[location] = errorMsg
            })
          })
          this.errors = errors
        })
      if (!isEmpty(this.selection)) {
        let deletePayload = {
          id: this.$route.params.community,
          data: this.selection
        }
        this.$store
          .dispatch('deleteCommunityCollections', deletePayload)
          .then(() => {
            this.$store.dispatch(
              'getCommunityCollections',
              this.$route.params.community
            )
          })
      }
    },
    openTab(tabName) {
      const generaltab = this.$refs['general-tab']
      const generalbutton = this.$refs['general-button']
      const collectionstab = this.$refs['collections-tab']
      const collectionsbutton = this.$refs['collections-button']
      switch (tabName) {
        case 'General':
          generaltab.style.display = 'block'
          generalbutton.className += ' active'
          collectionstab.style.display = 'none'
          collectionsbutton.className -= ' active'
          break
        case 'Collections':
          collectionstab.style.display = 'block'
          collectionsbutton.className += ' active'
          generaltab.style.display = 'none'
          generalbutton.className -= ' active'
          break
      }
    },
    /**
     * Generate the FormData
     * @returns {FormData}
     */
    normalizeFormData() {
      let data = new FormData()
      let data_nl = { language_code: 'NL' }
      let data_en = { language_code: 'EN' }

      forEach(this.formData, (element, key) => {
        if (!isNil(element)) {
          let value = element
          if (Array.isArray(element)) {
            value = JSON.stringify(element)
          }
          if (!startsWith(key, 'logo') && !startsWith(key, 'featured')) {
            if (endsWith(key, '_nl')) {
              data_nl[key.slice(0, -3)] = value
            } else if (endsWith(key, '_en')) {
              data_en[key.slice(0, -3)] = value
            }
          }
          data.append(key, value)
        }
        // if the value is empty, send it to the backend (so the backend can reject the post)
        else {
          if (endsWith(key, '_nl')) {
            data_nl[key.slice(0, -3)] = ''
          } else if (endsWith(key, '_en')) {
            data_en[key.slice(0, -3)] = ''
          }
        }
      })
      let deleted_logos = []
      data.set('logo_nl', '')
      if (this.logo_nl_added) {
        let logo = this.$refs['file-logo_nl'].$el.querySelector(
          'input[type="file"]'
        ).files[0]
        data.set('logo_nl', logo)
      } else if (this.logo_nl_deleted) {
        deleted_logos.push('logo_nl')
      } else {
        data.delete('logo_nl')
      }

      data.set('logo_en', '')
      if (this.logo_en_added) {
        data.set(
          'logo_en',
          this.$refs['file-logo_en'].$el.querySelector('input[type="file"]')
            .files[0]
        )
      } else if (this.logo_en_deleted) {
        deleted_logos.push('logo_en')
      } else {
        data.delete('logo_en')
      }

      data.set('featured_image_nl', '')
      if (this.featured_nl_added) {
        data.set(
          'featured_image_nl',
          this.$refs['file-img_nl'].$el.querySelector('input[type="file"]')
            .files[0]
        )
      } else if (this.featured_nl_deleted) {
        deleted_logos.push('featured_image_nl')
      } else {
        data.delete('featured_image_nl')
      }

      data.set('featured_image_en', '')
      if (this.featured_en_added) {
        data.set(
          'featured_image_en',
          this.$refs['file-img_en'].$el.querySelector('input[type="file"]')
            .files[0]
        )
      } else if (this.featured_en_deleted) {
        deleted_logos.push('featured_image_en')
      } else {
        data.delete('featured_image_en')
      }

      data.append(
        'community_details_update',
        JSON.stringify([data_nl, data_en])
      )
      data.append('deleted_logos', JSON.stringify(deleted_logos))
      for (var pair of data.entries()) {
        console.log(pair[0] + ', ' + pair[1])
      }
      return data
    },
    saveCollection(collection) {
      this.$store.dispatch('setCommunityCollection', {
        id: this.$route.params.community,
        data: [
          {
            id: collection.id,
            title_nl: collection.title_nl,
            title_en: collection.title_en
          }
        ]
      })
    },
    getPreviewPath() {
      return this.localePath({
        name: 'communities-community',
        params: {
          community: this.formData.external_id
        }
      })
    },
    setCollectionSelection(selection) {
      this.selection = selection
    },
    onWebsiteURLBlur(language) {
      const hasValue = !isEmpty(this.formData['website_url_' + language])
      const hasValidProtocol = startsWith(
        this.formData['website_url_' + language],
        'http'
      )
      if (hasValue && !hasValidProtocol) {
        this.formData['website_url_' + language] =
          'https://' + this.formData['website_url_' + language]
      }
      const oppositeLanguage = language === 'en' ? 'nl' : 'en'
      const hasOppositeValue = !isEmpty(
        this.formData['website_url_' + oppositeLanguage]
      )
      if (hasValue && !hasOppositeValue) {
        this.formData['website_url_' + oppositeLanguage] = this.formData[
          'website_url_' + language
        ]
      }
    }
  }
}
</script>
<style lang="less">
@import './../../variables';
.communities {
  width: 100%;

  &__section {
    &__blue_box {
      line-height: 75px;
      border: 1px;
      background: @dark-blue;
      width: 40%;
      min-width: 440px; // or break tablets
      border-radius: 20px;
      margin-top: -80px;
      margin-bottom: 30px;
      color: white;
      font-size: 18px;
      font-weight: 600;
      @media @mobile {
        margin-top: 0;
      }
      a:link {
        color: white;
        text-decoration: none;
      }
      a:visited {
        color: white;
        text-decoration: none;
      }
    }
  }
  &__form {
    margin-bottom: 60px;
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
      font-family: @main-font;
      border: 1px solid #e5e5e5;
      width: 100%;
      border-radius: 7px;
      padding: 10px;
      font-size: 16px;
      line-height: 1.44;
      color: #686d75;
      &:focus {
        outline: none;
      }
    }
    &__buttons {
      width: 100%;
      display: flex;
      justify-content: space-between;
      padding: 10px;
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

  button {
    padding-left: 40px;
  }

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
  position: relative;
  display: inline-block;
  border-radius: 5px;
  background-color: inherit;
  border: 1px solid #ccc;
  outline: none;
  cursor: pointer;
  padding: 14px 50px;
  margin-right: 25px;
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
  content: '';
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
  color: @red;
  font-size: 14px;
  display: none;
  list-style-type: none;
  padding-top: 5px;
  margin-left: -20px;
}

.field.invalid {
  .errors {
    display: block;
  }
  input,
  textarea,
  .form__file {
    border: 1px @red solid;
  }
}

.language {
  margin-bottom: 20px;

  hr {
    border-top: 1px solid @dark-grey;
  }
}
</style>
