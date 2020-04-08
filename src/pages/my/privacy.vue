
<template>
  <section class="container main privacy">
    <div class="center_block">
      <div class="privacy__info">
        <img
          src="/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="/images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
         /images/pictures/rawpixel-760027-unsplash@3x.jpg 3x"
          class="privacy__info_bg">
        <BreadCrumbs
          :items="[{title: $t('Home'), url: localePath('index')}]"
        />
        <h2 class="privacy__info_ttl">{{ $t('My-privacy') }}</h2>
      </div>
      <div class="privacy__form" v-if="permissions.length">
        <form action="/" class="privacy__form_in" @submit.prevent="onSubmit" novalidate>
          <div class="privacy__form__column">
            <div class="privacy__form__row" v-for="permission in permissions" :key="permission.type">
              <p class="privacy__form__label">
                {{ permission[$i18n.locale].title }}
              </p>
              <div class="permission-container">
                <div class="switch-container">
                  <switch-input v-model="permission.is_allowed" v-if="!permission.is_notification_only"></switch-input>
                </div>
                <div class="description" :class="{'notification-only': permission.is_notification_only}">
                  <p>{{ permission[$i18n.locale].description }}
                  (<router-link :to="localePath(permission.more_info_route)">{{ $t('more-info') }}</router-link>)
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="privacy__form__buttons">
            <div
              v-if="is_saved"
              class="success" >
              &#10004; {{ $t('Data-saved') }}
            </div>
            <button
              :disabled="is_submitting"
              type="submit"
              class="button privacy__form__button"
            >
              {{ $t('save') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script>
import { isNil, forEach } from 'lodash';
import { mapGetters } from 'vuex';

import BreadCrumbs from '~/components/BreadCrumbs';
import SwitchInput from '~/components/switch-input';


export default {
  components: {
    BreadCrumbs,
    SwitchInput
  },
  data() {
    return {
      is_saved: false,
      is_submitting: false,
      permissionsKey: 0
    };
  },
  computed: {
    ...mapGetters([
      'user',
      'isAuthenticated'
    ]),
    permissions() {
      if(isNil(this.user) || isNil(this.user.permissions)) {
        return []
      }
      return this.user.permissions;
    }
  },
  methods: {

    onSubmit() {
      this.is_submitting = true;
      this.$store
        .dispatch('postUser')
        .then(() => {
          this.is_saved = true;
          setTimeout(() => {
            this.is_saved = false;
            let authFlowToken = this.$store.getters.auth_flow_token;
            if(!isNil(authFlowToken)) {
              let backendUrl = process.env.VUE_APP_BACKEND_URL;
              this.$store.commit('AUTH_FLOW_TOKEN', null);
              window.location = backendUrl +
                'complete/surf-conext/?partial_token=' + authFlowToken
            }
          }, 1000);
        })
        .finally(() => {
          this.is_submitting = false;
        });
    }
  }
};

</script>
<style lang="less">

@import './../../variables';


.privacy {
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
  }
  &__form {
    margin-bottom: 146px;

    .permission-container {
      display: flex;
      align-items: center;
    }

    .switch-container {
      line-height: 75px;
    }
    .description {
      padding-left: 20px;
    }
    .description.notification-only {
      padding: 0
    }

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
      clear: both;
      overflow: hidden;
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
    &__radio {
      display: none;
    }
    &__radio + label {
      display: inline-block;
      background-repeat: no-repeat;
      background-size: cover;
      width: 40px;
      height: 40px;

      &.allow {
        background-image: url("/images/plus-black.svg");
      }
      &.deny {
        background-image: url("/images/min-black.svg");
      }
    }
    &__radio:checked + label {
      &.allow {
        background-image: url("/images/plus-copy.svg");
      }
      &.deny {
        background-image: url("/images/min.svg");
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
}
</style>
