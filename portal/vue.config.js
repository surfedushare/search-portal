let path = require('path');
const BundleTracker = require("webpack-bundle-tracker");
const packageJSON = require('./package.json');

const appDirectory = packageJSON.name + '/';
const djangoPublicPath = '/static/' + appDirectory;
const distDirectory = './dist/';
const webpackStatsFile = distDirectory + packageJSON.name + '.webpack-stats.json';


module.exports = {

  publicPath: (process.env.NODE_ENV === 'production' && process.env.npm_package_config_mode === 'django') ?
    djangoPublicPath : '/',
  outputDir: distDirectory,
  lintOnSave: false,

  configureWebpack: {
    resolve: {
      alias: {
        "~": path.resolve(__dirname + '/src')
      }
    }
  },
  chainWebpack: config => {

    config
      .plugin('BundleTracker')
      .use(BundleTracker, [{filename: webpackStatsFile}]);

  }

};
