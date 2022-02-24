let path = require('path')
const BundleTracker = require('webpack-bundle-tracker')
const packageJSON = require('./package.json')

const appDirectory = packageJSON.name + '/'
const djangoPublicPath = '/static/' + appDirectory
const server =
  process.env.npm_config_server || process.env.npm_package_config_server

module.exports = {
  publicPath: server === 'django' ? djangoPublicPath : '/',
  lintOnSave: false,
  transpileDependencies: ['@sentry'], // this makes sure we polyfill certain dependencies
  devServer: {
    proxy: 'http://localhost:8000'
  },
  configureWebpack: {
    devtool: 'source-map',
    resolve: {
      alias: {
        '~': path.resolve(__dirname + '/src')
      }
    },
    module: {
      rules: [
        {
          test: /\.s(c|a)ss$/,
          use: [
            {
              loader: 'sass-loader',
              // Requires >= sass-loader@^8.0.0
              options: {
                implementation: require('sass'),
                sassOptions: { },
                additionalData: "@import '@/styles/variables.scss'"
              },
            },
          ],
        },
      ],
    }
  },
  chainWebpack: config => {
    config
      .plugin('BundleTracker')
      .use(BundleTracker, [{ path: config.output.get('path') }])
  }
}
