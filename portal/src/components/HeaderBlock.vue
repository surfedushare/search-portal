<template>
  <div class="center_block center-header">
    <div class="header-block">
      <img
        class="bg"
        src="../assets/images/pictures/rawpixel-760027-unsplash.jpg"
        srcset="
          ../assets/images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
          ../assets/images/pictures/rawpixel-760027-unsplash@3x.jpg 3x
        "
      />
      <h2 class="header-title">
        {{ title }}
      </h2>
    </div>
  </div>
</template>

<script>
export default {
  name: "HeaderBlock",
  props: {
    title: {
      type: String,
      default: "",
    },
  },
};
</script>
<style scoped lang="less">
@import url("../variables");
.center-header {
  padding: 80px 0;

  @media @mobile {
    padding: 30px;
  }
}
.header-block {
  border-radius: 20px;
  position: relative;
  background: @light-grey;
  padding: 50px 30px;

  @media @mobile {
    padding: 20px;
  }

  h2 {
    @media @mobile {
      font-size: 26px;
    }
  }
  .bg {
    position: absolute;
    right: 26px;
    top: -35px;
    max-width: 370px;
    max-height: 220px;
    border-radius: 21px;

    @media @mobile {
      display: none;
    }
  }
}
</style>
