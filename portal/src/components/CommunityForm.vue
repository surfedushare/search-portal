<template>
  <form
    v-if="value"
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
              v-model="value.title_nl"
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
              v-model="value.title_en"
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
              v-model="value.website_url_nl"
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
              v-model="value.website_url_en"
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
              id="logo_nl"
              :imagesrc="value.logo_nl"
              :width="120"
              :height="52"
              @remove_image="onRemoveImage('logo_nl')"
              @add_image="onAddImage('logo_nl', $event)"
              @preview_url="onPreviewUrl('logo_nl', $event)"
            />
          </InputLanguageWrapper>
        </ErrorWrapper>
      </div>
      <div class="communities__form__row communities__form__file">
        <ErrorWrapper :errors="getFieldErrors('logo_en')">
          <InputLanguageWrapper language="EN">
            <InputFile
              id="logo_en"
              :imagesrc="value.logo_en"
              :width="120"
              :height="52"
              @remove_image="onRemoveImage('logo_en')"
              @add_image="onAddImage('logo_en', $event)"
              @preview_url="onPreviewUrl('logo_en', $event)"
            />
          </InputLanguageWrapper>
        </ErrorWrapper>
      </div>
    </div>
    <div class="communities__form__column">
      <div id="description_nl" class="communities__form__row">
        <ErrorWrapper :errors="getFieldErrors('description_nl')">
          <RichTextInput
            v-model="value.description_nl"
            :title="$t('Description')"
            language="NL"
            :placeholder="$t('community-description-placeholder')"
          />
        </ErrorWrapper>
      </div>
      <div id="description_en" class="communities__form__row">
        <ErrorWrapper :errors="getFieldErrors('description_en')">
          <RichTextInput
            v-model="value.description_en"
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
              id="featured_image_nl"
              :imagesrc="value.featured_image_nl"
              :width="388"
              :height="227"
              @remove_image="onRemoveImage('featured_image_nl')"
              @add_image="onAddImage('featured_image_nl', $event)"
              @preview_url="onPreviewUrl('featured_image_nl', $event)"
            />
          </InputLanguageWrapper>
        </ErrorWrapper>
      </div>
      <div class="communities__form__row communities__form__file">
        <ErrorWrapper :errors="getFieldErrors('featured_image_en')">
          <InputLanguageWrapper language="EN">
            <InputFile
              id="featured_image_en"
              :imagesrc="value.featured_image_en"
              :width="388"
              :height="227"
              @remove_image="onRemoveImage('featured_image_en')"
              @add_image="onAddImage('featured_image_en', $event)"
              @preview_url="onPreviewUrl('featured_image_en', $event)"
            />
          </InputLanguageWrapper>
        </ErrorWrapper>
      </div>
    </div>
  </form>
</template>
<script>
import ErrorWrapper from '~/components/ErrorWrapper'
import InputFile from '~/components/InputFile'
import InputLanguageWrapper from '~/components/InputLanguageWrapper'
import InputWithCounter from '~/components/InputWithCounter'
import RichTextInput from '~/components/RichTextInput'
import { isEmpty, startsWith } from 'lodash'

export default {
  name: 'CommunityForm',
  components: {
    ErrorWrapper,
    InputFile,
    InputLanguageWrapper,
    InputWithCounter,
    RichTextInput,
  },
  props: {
    value: {
      type: Object,
      default: () => ({}),
    },
    errors: {
      type: Object,
      default: () => ({}),
    },
  },
  methods: {
    getFieldErrors(fieldName) {
      return this.errors[fieldName]
    },
    onRemoveImage(field) {
      this.value[field] = null
    },
    onAddImage(field, file) {
      this.value[field] = file
    },
    onPreviewUrl(field, url) {
      this.value[`${field}_preview`] = url
    },
    onWebsiteURLBlur(language) {
      const hasValue = !isEmpty(this.value['website_url_' + language])
      const hasValidProtocol = startsWith(
        this.value['website_url_' + language],
        'http'
      )
      if (hasValue && !hasValidProtocol) {
        this.value['website_url_' + language] =
          'https://' + this.value['website_url_' + language]
      }
      const oppositeLanguage = language === 'en' ? 'nl' : 'en'
      const hasOppositeValue = !isEmpty(
        this.value['website_url_' + oppositeLanguage]
      )
      if (hasValue && !hasOppositeValue) {
        this.value['website_url_' + oppositeLanguage] =
          this.value['website_url_' + language]
      }
    },
  },
}
</script>
