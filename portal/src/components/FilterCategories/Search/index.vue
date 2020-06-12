<template src="./Search.component.html" />
<script src="./Search.component.js"></script>
<style src="./Search.component.less" scoped lang="less"></style>
<style src="./autosuggest.less" lang="less"></style>
<style lang="less">
  @import './../../../variables';
  .search--hide-categories .v-select.searchable .dropdown-toggle {
    @media @desktop {
      padding-right: 140px;
    }
  }
</style>
