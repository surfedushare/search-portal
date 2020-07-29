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
              <switch-input
                v-model="isPublished"
                class="public-switch"
                :label="$t('public')"
              />
              &nbsp;&nbsp;
              <button
                type="button"
                class="button preview"
                @click="previewMode = !previewMode"
              >
                <i
                  class="fas fa-eye"
                  :class="{
                    'fa-eye': !previewMode,
                    'fa-eye-slash': previewMode
                  }"
                />
                {{ $t('example') }}
              </button>
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

        <div v-if="previewMode">
          <InfoBlock
            class="preview-block"
            :title="formData[`title_${$i18n.locale}`]"
            :content="formData[`description_${$i18n.locale}`]"
            :website_url="formData[`website_url_${$i18n.locale}`]"
            :logo_src="previewImage()"
          />
        </div>
        <div v-show="!previewMode">
          <Tabs>
            <Tab :title="$t('general')" identifier="general">
              <div id="General" class="communities__form">
                <h1>{{ $t('general') }}</h1>
                {{ $t('manage-community-information') }}
                <br /><br />
                <CommunityForm v-model="formData" :errors="errors" />
              </div>
            </Tab>
            <Tab :title="$t('collections')" identifier="collections-tab">
              <div id="Collections" class="communities__collections">
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
            </Tab>
          </Tabs>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { isEmpty, find, forEach } from 'lodash'
import { mapGetters } from 'vuex'
import Collections from '~/components/Collections'
import HeaderBlock from '~/components/HeaderBlock'
import AddCollection from '~/components/Popup/AddCollection'
import Error from '~/components/error'
import SwitchInput from '~/components/switch-input'
import CommunityForm from '~/components/CommunityForm'
import InfoBlock from '~/components/InfoBlock'
import Tabs from '~/components/Tabs'
import Tab from '~/components/Tab'
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
    SwitchInput,
    CommunityForm,
    InfoBlock,
    Tabs,
    Tab
  },
  data() {
    return {
      isSubmitting: false,
      showPopup: false,
      errors: {},
      formData: null,
      notFound: false,
      currentTab: 'general',
      previewMode: false
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
    previewImage() {
      const image = this.formData[`featured_image_${this.$i18n.locale}`]
      if (image instanceof File) {
        return this.formData[`featured_image_${this.$i18n.locale}_preview`]
      }

      return image
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
        .dispatch('putCommunity', {
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
      border: 1px;
      background: @dark-blue;
      width: 40%;
      min-width: 440px; // or break tablets
      border-radius: 20px;
      margin-top: -20px;
      margin-bottom: 30px;
      color: white;
      font-size: 16px;
      font-weight: 600;
      @media @mobile {
        margin-top: 0;
      }
      button.preview {
        background: @dark-blue;
        color: white;
        border: 1px solid white;
        border-radius: 10px;
        line-height: 1em;
        padding: 16px 23px;
        margin-right: 10px;

        i {
          margin-right: 10px;
        }

        &:hover:not([disabled]) {
          background: darken(@dark-blue, 5%);
        }
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
      margin-right: -50px;
    }
    &__column {
      flex: 1;
      min-width: 400px;
      margin-right: 50px;
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
      align-items: center;
      padding: 10px;
    }
  }
  &__collections {
    margin: 0 0 175px;
  }
}
.public-switch {
  flex: 1;
  justify-content: center;

  input + .slider {
    background-color: #2196f3;
  }
  input:checked + .slider {
    background-color: #ffc300;
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
