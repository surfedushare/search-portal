<template src="./Search.component.html" />
<script src="./Search.component.js">
</script>
<style src="./Search.component.less" scoped lang="less">
</style>
<style lang="less">
@import './../../../assets/styles/variables';
.search {
  .v-select {
    flex-wrap: wrap;
    overflow: hidden;
    position: relative;

    .vs__actions {
      width: 40px;
      height: 40px;
      padding: 0 0 0 10px;

      .open-indicator {
        display: none;
      }
    }

    .selected-tag {
      background: @dark-blue;
      color: #fff;
      border: 0;
      border-radius: 20px;
      font-family: @second-font;
      font-size: 12px;
      font-weight: bold;
      height: 25px;
      line-height: 25px;
      padding: 0 33px;
      position: relative;
      max-width: 200px;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      display: inline-block;

      .close {
        position: absolute;
        left: 5px;
        top: 50%;
        transform: translate(0, -50%);
        color: transparent;
        width: 15px;
        height: 15px;
        text-shadow: none;
        opacity: 1;
        background: url('./../../../assets/images/close-white.svg') 50% 50%
          no-repeat;
        background-size: 15px 15px;
      }
    }

    /* List Items */
    li {
      line-height: 1.42857143; /* Normalize line height */
    }
    li > a {
      display: block;
      padding: 10px 66px;
      clear: both;
      color: @dark-grey; /* Overrides most CSS frameworks */
      white-space: nowrap;
    }

    .dropdown-menu .active > a {
      color: @dark-grey;
      background: rgba(50, 50, 50, 0.1);
    }
    .dropdown-menu > .highlight > a {
      background: @dark-blue url('./../../../assets/images/search-white.svg')
        21px 50% no-repeat;
      background-size: 20px 20px;
      &:hover {
        background: @dark-blue url('./../../../assets/images/search-white.svg')
          21px 50% no-repeat;
        background-size: 20px 20px;
        color: #fff;
      }
    }
    .dropdown-menu > li > a {
      background: url('./../../../assets/images/search-grey.svg') 21px 50%
        no-repeat;
      background-size: 20px 20px;
    }
  }

  .v-select input[type='search'],
  .v-select input[type='search']:focus {
    font-size: 16px;
    font-family: @second-font;
  }
}
.search .v-select.searchable .dropdown-toggle {
  width: 100%;
  border: 0;
  background: url('./../../../assets/images/search-grey.svg') 14px 50% no-repeat;
  font-size: 16px;
  height: 67px;
  padding-left: 40px;
  background-size: 20px 20px;
  @media @desktop {
    height: 99px;
    padding: 0 400px 0 59px;
    background-position-x: 21px;
    background-size: initial;
  }
  align-items: center;
}

.search--hide-categories .v-select.searchable .dropdown-toggle {
  @media @desktop {
    padding-right: 140px;
  }
}

.search .v-select .dropdown-menu {
  display: block;
  position: relative;
  top: 0;
  left: 0;
  border: 0;
  box-shadow: none;
  border-radius: 0;
  margin: 0 0 20px;
}
</style>
