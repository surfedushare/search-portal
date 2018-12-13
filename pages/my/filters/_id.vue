
<template>
  <section class="container main collections my_filter">
    <div
      class="center_block">
      <div
        v-if="data"
        class="my_filter__info" >
        <div class="my_filter__info_title">
          <BreadCrumbs
            :items="[
              {title:`Mijn selecties`, url: `/my/filters/`},
              {title:`Selectie`, url: `/my/filters/${data.id}`}]"
          />
          <h2
            ref="title"
            :contenteditable="contenteditable"
            class="my_filter__info_ttl"
            @blur="onChangeTitle"
          >
            {{ filter_title }}
          </h2>
          <p
            v-if="materials"
            class="my_filter__info_subttl"
          >
            {{ data.materials_count }} resultaten
          </p>
        </div>
        <div class="my_filter__info_filter">
          <div class="my_filter__info_filter__edit">
            <a
              v-if="contenteditable"
              class="my_filter__info_filter__link"
              href="#"
              @click.prevent="setEditable(false)"
            >
              Annuleren
            </a>
            <a
              v-else
              href="#"
              class="my_filter__info_filter__link"
              @click.prevent="setEditable(true)"
            >
              Bewerken
            </a>
          </div>
          <div class="my_filter__info_filter__delete">
            <a
              href="#"
              class="my_filter__info_filter__link"
              @click.prevent="deleteFilter"
            >
              Verwijderen
            </a>
          </div>
          <div class="my_filter__info_filter__button">
            <button
              :disabled="materials && !materials.records_total"
              class="button"
              @click.prevent="saveFilter"
            >
              Opslaan
            </button>
          </div>
        </div>
      </div>

      <masonry
        :cols="{default: 4, 1000: 3, 700: 2, 400: 1}"
        :gutter="{default: '60px', 700: '15px'}"
        :class="{'filter-categories--loading': materials_loading || !all_filters}"
      >
        <div
          v-for="category in all_filters"
          v-if="!category.hide"
          :key="category.external_id"
          class="filter-categories__item"
        >
          <h4
            class="filter-categories__item_title"
          >
            {{ category.title }}
          </h4>
          <ul class="filter-categories__subitems">
            <li
              v-for="filter in category.items"
              :key="filter.external_id"
              class="filter-categories__subitem"
            >
              <input
                :id="filter.external_id"
                :value="filter.external_id"
                :checked="filter.checked"
                type="checkbox"
                @change="onChange($event, filter, category.external_id)"
              >
              <label :for="filter.external_id">
                {{ filter.title }}&nbsp;({{ filter.count }})
                <span
                  v-if="category.external_id === 'lom.rights.copyrightandotherrestrictions'"
                  :class="filter.external_id"
                  class="filter-categories__subitem_icon filter-categories__subitem_icon--inline"
                />
              </label>
            </li>
          </ul>
        </div>
      </masonry>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';

export default {
  components: {
    BreadCrumbs
  },
  data() {
    return {
      checked_filter: [],
      checked_categories_filter: [],
      filters_count: false,
      contenteditable: false,
      data: null,
      filter_title: null
    };
  },
  computed: {
    ...mapGetters([
      'active_filter',
      'materials',
      'filters',
      'filter_categories',
      'materials_loading',
      'user',
      'isAuthenticated'
    ]),
    all_filters() {
      const { filters_count, filter_categories, data } = this;
      if (filters_count && filter_categories) {
        const { results } = filter_categories;

        return results.map(category => {
          const current_filter = filters_count.find(
            filter => filter.external_id === category.external_id
          );
          return {
            ...category,
            ...current_filter,
            items: category.items.reduce((prev, item) => {
              const current_item =
                current_filter.items.find(
                  filter => filter.external_id === item.external_id
                ) || {};

              if (current_item && current_item.count) {
                const ids =
                  data && data.items
                    ? data.items.map(item => item.category_item_id)
                    : false;
                prev.push({
                  ...item,
                  ...current_item,
                  checked: ids ? ids.indexOf(item.id) !== -1 : false
                });
              }

              return prev;
            }, [])
          };
        });
      }

      return false;
    }
  },
  watch: {
    isAuthenticated(isAuthenticated) {
      if (isAuthenticated) {
        this.getData();
      }
    },
    contenteditable(isEditable) {
      const { title } = this.$refs;
      this.$nextTick().then(() => {
        title.focus();
      });
      if (!isEditable) {
        this.resetData();
      }
    },
    collection(collection) {
      if (collection) {
        this.setTitle(collection.title);
      }
    }
  },
  mounted() {
    if (this.isAuthenticated) {
      this.getData();
    }
  },
  methods: {
    getData() {
      this.$store
        .dispatch('searchMaterials', {
          return_records: false,
          search_text: []
          // filters: [
          //   {
          //     external_id: 'lom.classification.obk.educationallevel.id',
          //     items: [
          //       'be140797-803f-4b9e-81cc-5572c711e09c',
          //       'f33b30ee-3c82-4ead-bc20-4255be9ece2d',
          //       'de952b8b-efa5-4395-92c0-193812130c67',
          //       'f3ac3fbb-5eae-49e0-8494-0a44855fff25',
          //       'a598e56e-d1a6-4907-9e2c-3da64e59f9ae',
          //       '00ace3c7-d7a8-41e6-83b1-7f13a9af7668',
          //       '654931e1-6f8b-4f72-aa4b-92c99c72c347',
          //       '8beca7eb-95a5-4c7d-9704-2d2a2fc4bc65',
          //       'bbbd99c6-cf49-4980-baed-12388f8dcff4',
          //       '18656a7c-95a5-4831-8085-020d3151aceb',
          //       '2998f2e0-449d-4911-86a2-f4cbf1a20b56'
          //     ]
          //   }
          // ]
        })
        .then(data => {
          this.filters_count = data.filters.slice(0);
        });

      this.$store
        .dispatch('getDetailFilter', {
          id: this.$route.params.id
        })
        .then(data => {
          this.setDefaultData(data);
          this.setTitle(data.title);
        })
        .catch(err => {
          if (err.response.status === 404) {
            this.$router.push('/my/filters/');
          }
        });

      this.$store.dispatch('getFilterCategories');
    },
    setDefaultData(data) {
      this.data = Object.assign({}, data, {
        items: data.items.slice(0)
      });
    },
    onChange($event, filter, external_id) {
      const { checked } = $event.target;
      if (checked) {
        this.data.items.push({
          category_item_id: filter.id
        });
      } else {
        this.data.items = this.data.items.filter(
          item => item.category_item_id !== filter.id
        );
      }

      this.changeCheckedCategories(checked, filter, external_id);
      this.setEditable(true);
    },
    changeCheckedCategories(checked, filter, external_id) {
      const { checked_categories_filter } = this;
      const current_category_index = checked_categories_filter.findIndex(
        filter => filter.external_id === external_id
      );

      if (current_category_index !== -1) {
        let items = checked_categories_filter[
          current_category_index
        ].items.slice(0);

        if (checked) {
          items.push(filter.external_id);
        } else {
          items = items.filter(item => item !== filter.external_id);
        }

        this.checked_categories_filter = checked_categories_filter.map(
          (category, index) => {
            if (index === current_category_index) {
              return {
                ...category,
                items: items
              };
            }
            return category;
          }
        );
      } else {
        this.checked_categories_filter.push({
          external_id: external_id,
          items: [filter.external_id]
        });
      }

      this.$store
        .dispatch('searchMaterials', {
          return_records: false,
          search_text: [],
          filters: this.checked_categories_filter
        })
        .then(data => {
          this.data.materials_count = data.records_total;
        });
    },
    saveFilter() {
      this.$store.dispatch('saveMyFilter', this.data).then(() => {
        // this.$router.push('/my/filters/');
      });
    },
    deleteFilter() {
      this.$store.dispatch('deleteMyFilter', this.$route.params.id).then(() => {
        this.$router.push('/my/filters/');
      });
    },
    setEditable(isEditable) {
      this.contenteditable = isEditable;
    },
    setTitle(title) {
      this.filter_title = title;
      if (this.$refs.title) {
        this.$refs.title.innerText = title;
      }
    },
    onChangeTitle() {
      this.setTitle(this.$refs.title.innerText);
    },
    resetData() {
      const { active_filter } = this;
      this.setTitle(this.data.title);
      this.setDefaultData(active_filter);
      const ids = active_filter.items.map(item => item.category_item_id);

      if (ids && ids.length) {
        this.checked_categories_filter = this.checked_categories_filter.reduce(
          (prev, next) => {
            const items = next.items.filter(
              item => ids.indexOf(item.external_id) !== -1
            );

            if (items && items.length) {
              prev.push({
                ...next,
                items
              });
            }

            return prev;
          },
          []
        );
      } else {
        this.checked_categories_filter = [];
      }
    }
  }
};
</script>

<style lang="less">
@import './../../../assets/styles/variables';
.my_filter {
  width: 100%;
  padding: 101px 0 47px;

  &__info {
    padding: 59px 45px 95px 103px;
    margin: 0 0 113px;
    border-radius: 20px;
    position: relative;
    display: flex;
    justify-content: space-between;
    background: url('./../../../assets/images/filters.svg') 54px 96px no-repeat;
    background-size: 30px 30px;

    .bread-crumbs {
      margin-bottom: 0;
    }
    &:before {
      content: '';
      min-width: 100%;
      position: absolute;
      background-color: rgba(244, 244, 244, 0.9);
      right: 0;
      left: 0;
      top: 0;
      bottom: 0;
      border-radius: 20px;
      z-index: -1;
    }
    &_ttl {
      padding: 0 0 8px;
      position: relative;

      &:focus {
        outline: none;
      }
    }
    &_subttl {
      padding: 0 0 7px;
      font-size: 20px;
      line-height: 1.15;
      font-family: @main-font;
      position: relative;
    }
    &_title {
      display: inline-block;
      vertical-align: top;
      min-width: 50%;
      flex: 1 1 auto;
    }

    &_filter {
      width: 45%;
      display: flex;
      margin: 0;
      padding-top: 15px;
      align-items: center;
      justify-content: flex-end;
      &__link {
        font-weight: bold;
        padding-left: 30px;
        position: relative;
        font-size: 16px;
        font-family: @second-font;
      }
      &__edit {
        a {
          background: url('./../../../assets/images/edit.svg') no-repeat 0 50%;
          background-size: 30px 30px;
        }
      }
      &__delete {
        margin-left: 32px;
        a {
          background: url('./../../../assets/images/trash.svg') no-repeat 0 50%;
          background-size: 30px 30px;
        }
      }
      &__button {
        margin-left: 50px;
        a {
          padding: 13px 60px;
        }
      }
    }
  }
  &__add {
    display: flex;
    justify-content: flex-end;
    margin-bottom: -55px;
    &__link {
      padding: 13px 43px 13px 51px;
      background-image: url('./../../../assets/images/plus-black.svg');
      background-position: 10px 50%;
      background-repeat: no-repeat;
      background-size: 24px;
    }
  }
}
</style>
<style src="./../../../components/FilterCategories/FilterCategories.component.less" scoped lang="less">
</style>
