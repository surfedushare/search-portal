
<template>
  <section class="container main communities">
    <div class="center_block">
      <div class="communities__info">
        <img
          src="./../../assets/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="./../../assets/images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
         ./../../assets/images/pictures/rawpixel-760027-unsplash@3x.jpg 3x"
          class="communities__info_bg">
        <BreadCrumbs
          :items="[{title:`Home`, url: `/`} ]"/>
        <h2 class="communities__info_ttl">Mijn Community</h2>
        <Search
          :hide-categories="true"
          :hide-filter="true"
          class="communities__info_search"
          active-category-external-id="lom.technical.format"
        />
      </div>
      <div class="communities__form">
        <form
          action="/"
          class="communities__form_in"
        >
          <div class="communities__form__column">
            <div class="communities__form__row">
              <label
                for="name"
                class="communities__form__label">
                Naam
              </label>
              <input
                id="name"
                type="text"
                class="communities__form__input"
                placeholder="Landelijk Overleg Opleidingen Verpleegkunde">
            </div>
            <div class="communities__form__row">
              <label
                for="description"
                class="communities__form__label">
                Omschrijving
              </label>
              <textarea
                id="description"
                class="communities__form__textarea"
                placeholder="De community hbovpk is hét digitale ontmoetingspunt voor hbo-docenten verpleegkunde. Doel van de community is delen van kennis en leermaterialen en het uitwisselen van ervaringen. "/>
            </div>
            <div class="communities__form__row">
              <label
                for="website"
                class="communities__form__label">
                Website
              </label>
              <input
                id="website"
                type="text"
                class="communities__form__input"
                placeholder="Geef hier de URL ">
            </div>
          </div>
          <div class="communities__form__column">
            <div class="communities__form__row communities__form__file">
              <label
                for="logo"
                class="communities__form__file_label">
                Logo
              </label>
              <input
                id="logo"
                type="file"
                class="communities__form__file_input"
              >
              <span class="communities__form__file_text">
                File upload
              </span>
              <div class="communities__form__file_buttons">
                <a
                  href="#"
                  class="communities__form__file_button _delete"/>
                <a
                  href="#"
                  class="communities__form__file_button _upload">
                  upload
                </a>
              </div>
            </div>
            <div class="communities__form__row communities__form__file">
              <label
                for="featured_image"
                class="communities__form__file_label">
                Uitgelichte afbeelding
              </label>
              <input
                id="featured_image"
                type="file"
                class="communities__form__file_input"
              >
              <span class="communities__form__file_text">
                File upload
              </span>
              <div class="communities__form__file_buttons">
                <a
                  href="#"
                  class="communities__form__file_button _delete"/>
                <a
                  href="#"
                  class="communities__form__file_button _upload">
                  upload
                </a>
              </div>
            </div>
          </div>
          <div class="communities__form__buttons">
            <button class="button communities__form__button">Opslaan</button>
          </div>
        </form>
      </div>
      <div class="communities__collections">
        <div class="collections__add">
          <button
            class="collections__add__link button"
            @click.prevent="showAddCollection"
          >
            Nieuwe collectie
          </button>
        </div>
        <Collections :collections="my_collections.results" >
          <template slot="header-info">
            <h2>Collecties</h2>
          </template>
        </Collections>
        <AddCollection
          v-if="isShow"
          :close="close"
          :is-show="isShow"
          :is-shared="true"
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

export default {
  components: {
    Collections,
    BreadCrumbs,
    Materials,
    Search,
    AddCollection
  },
  data() {
    return {
      isShow: false
    };
  },
  computed: {
    ...mapGetters(['my_collections', 'my_collection_materials'])
  },
  mounted() {
    // this.$store.dispatch('getMaterialInMyCollection', this.$route.params.id);
    this.$store.dispatch('getMyCollections');
  },
  methods: {
    showAddCollection() {
      this.isShow = true;
    },
    addCollection() {},
    close() {
      this.isShow = false;
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
    &_bg {
      position: absolute;
      right: 26px;
      top: -57px;
      width: 510px;
      border-radius: 21px;
      height: 298px;
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
    &__file {
      border: none;
      border-radius: 20px;
      background-color: rgba(244, 244, 244, 0.9);
      padding: 12px 24px;
      margin: 24px 0 28px;
      font-size: 16px;
      line-height: 1.44;
      color: #686d75;
      position: relative;
      &_label {
        margin: 10px 0 28px;
        display: block;
        font-family: @second-font;
        font-weight: bold;
        color: #353535;
      }
      &_input {
        position: absolute;
        opacity: 0;
        height: 100%;
        width: 100%;
        top: 0;
        left: 0;
        &:focus {
          outline: none;
        }
      }
      &_text {
        margin: 0 0 13px;
        display: block;
      }
      &_buttons {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin: 0 -4px 0 0;
        position: relative;
      }
      &_button {
        display: inline-block;
        min-height: 20px;
        min-width: 20px;
        background-size: 20px;
        font-weight: bold;
        &._delete {
          background: url('./../../assets/images/trash.svg') no-repeat 0 50%;
        }
        &._upload {
          background: url('./../../assets/images/open-link.svg') no-repeat 100%
            50%;
          background-size: 15px;
          padding: 0 18px 0 0;
          margin-left: 12px;
        }
      }
    }
    &__buttons {
      text-align: right;
      width: 100%;
      margin: 10px 0 0;
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
    background-image: url('./../../assets/images/plus-black.svg');
    background-position: 10px 50%;
    background-repeat: no-repeat;
    background-size: 24px;
  }
}
</style>
