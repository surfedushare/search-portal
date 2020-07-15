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
                :disabled="isSubmitting"
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
            class="tablinks"
            :class="{ active: currentTab === 'general' }"
            @click="currentTab = 'general'"
          >
            {{ $t('general') }}
          </button>
          <button
            class="tablinks"
            :class="{ active: currentTab === 'collections' }"
            @click="currentTab = 'collections'"
          >
            {{ $t('collections') }}
          </button>
        </div>

        <div
          v-show="currentTab === 'general'"
          id="General"
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
                      :imagesrc="formData.logo_nl"
                      @remove_image="onRemoveImage('logo_nl')"
                      @add_image="onAddImage('logo_nl', $event)"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
              <div class="communities__form__row communities__form__file">
                <ErrorWrapper :errors="getFieldErrors('logo_en')">
                  <InputLanguageWrapper language="EN">
                    <InputFile
                      :imagesrc="formData.logo_en"
                      @remove_image="onRemoveImage('logo_en')"
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
                      :imagesrc="formData.featured_image_nl"
                      @remove_image="onRemoveImage('featured_nl')"
                      @add_image="onAddImage('featured_nl', $event)"
                    />
                  </InputLanguageWrapper>
                </ErrorWrapper>
              </div>
              <div class="communities__form__row communities__form__file">
                <ErrorWrapper :errors="getFieldErrors('featured_image_en')">
                  <InputLanguageWrapper language="EN">
                    <InputFile
                      :imagesrc="formData.featured_image_en"
                      @remove_image="onRemoveImage('featured_en')"
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
          v-show="currentTab === 'collections'"
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
import { isEmpty, find, forEach, startsWith } from 'lodash'
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
  logo_nl: null,
  logo_en: null,
  featured_image_nl: null,
  featured_image_en: null,
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
      isSubmitting: false,
      showPopup: false,
      errors: {},
      formData: null,
      notFound: false,
      currentTab: 'general'
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
  },
  methods: {
    getFieldErrors(fieldName) {
      return this.errors[fieldName]
    },
    onRemoveImage(field) {
      this.formData[field] = null
    },
    onAddImage(field, file) {
      this.formData[field] = file
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
    /**
     * Save community data
     */
    onSubmit() {
      this.isSubmitting = true

      const data = this.normalizeFormData()
      this.errors = {}
      this.$store
        .dispatch('putCommunities', {
          id: this.formData.external_id,
          data: data
        })
        .then(() => {
          this.$store.commit('ADD_MESSAGE', {
            level: 'info',
            message: 'Data-saved'
          })
        })
        .catch(err => {
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
              const errorKey = key + '_' + language.toLowerCase()
              errors[errorKey] = errorMsg
            })
          })
          this.errors = errors
        })
        .finally(() => {
          this.isSubmitting = false
        })
      if (!isEmpty(this.selection)) {
        const deletePayload = {
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
    normalizeFormData() {
      const data = new FormData()

      data.append('external_id', this.formData.external_id)
      data.append('publish_status', this.formData.publish_status)
      data.append('title_nl', this.formData.title_nl)
      data.append('title_en', this.formData.title_en)
      data.append('description_nl', this.formData.description_nl)
      data.append('description_en', this.formData.description_en)
      data.append('website_url_nl', this.formData.website_url_nl)
      data.append('website_url_en', this.formData.website_url_en)

      const data_nl = {
        language_code: 'NL',
        title: this.formData.title_nl,
        website_url: this.formData.website_url_nl,
        description: this.formData.description_nl
      }

      const data_en = {
        language_code: 'EN',
        title: this.formData.title_en,
        website_url: this.formData.website_url_en,
        description: this.formData.description_en
      }

      const fileFields = [
        'logo_nl',
        'logo_en',
        'featured_image_nl',
        'featured_image_en'
      ]

      const deleted_logos = []

      fileFields.forEach(field => {
        const fieldData = this.formData[field]

        if (fieldData instanceof File) {
          data.set(field, fieldData)
        } else if (!fieldData) {
          deleted_logos.push(field)
        }
      })

      data.append(
        'community_details_update',
        JSON.stringify([data_nl, data_en])
      )
      data.append('deleted_logos', JSON.stringify(deleted_logos))

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
