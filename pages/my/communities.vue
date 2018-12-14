
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
                v-model="formData.name"
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
                v-model="formData.description"
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
                v-model="formData.website_url"
                type="text"
                class="communities__form__input"
                placeholder="Geef hier de URL ">
            </div>
          </div>
          <div class="communities__form__column">
            <div class="communities__form__row communities__form__file">
              <InputFile
                ref="file-logo"
                :imagesrc="formData.logo"
                :title="'Logo'"
              />
            </div>
            <div class="communities__form__row communities__form__file">
              <InputFile
                ref="file-img"
                :imagesrc="formData.featured_image"
                :title="'Uitgelichte afbeelding'"
              />
            </div>
          </div>
          <div class="communities__form__buttons">
            <button
              type="submit"
              class="button communities__form__button"
              @click.prevent="onSubmit">Opslaan</button>
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
      isShow: false,
      image_logo: '',
      formData: {
        name: false,
        description: false,
        website_url: false,
        logo: false,
        featured_image: false
      }
    };
  },
  computed: {
    ...mapGetters(['my_collections', 'communities'])
  },
  mounted() {
    this.$store
      .dispatch('getCommunities', { params: { is_admin: true } })
      .then(item => {
        const {
          id,
          name,
          description,
          website_url,
          logo,
          featured_image
        } = item.results[0];
        this.formData.id = id;
        this.formData.name = name;
        this.formData.description = description;
        this.formData.website_url = website_url;
        this.formData.logo = logo;
        this.formData.featured_image = featured_image;
      });
    this.$store.dispatch('getMyCollections');
  },
  methods: {
    showAddCollection() {
      console.log(11111);
      this.isShow = true;
    },
    addCollection() {
      console.log(11111);
    },
    close() {
      this.isShow = false;
    },
    onSubmit() {
      const data = this.normalizeFormData();
      this.$store.dispatch('putCommunities', {
        id: this.formData.id,
        data: data
      });
      // putCommunities
    },
    normalizeFormData() {
      let data = new FormData();

      for (let item in this.formData) {
        const el = this.formData[item];

        if (el) {
          if (Array.isArray(el)) {
            data.append(item, JSON.stringify(el));
            // console.log(data.append(item, JSON.stringify(el)));
          } else {
            data.append(item, el);
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
        data.delete('logo');
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
        data.delete('featured_image');
      }
      return data;
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
