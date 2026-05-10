const path = require('path')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const { DefinePlugin } = require('webpack')
const Dotenv = require('dotenv-webpack')

module.exports = {
  entry: './src/main.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.[contenthash].js',
    publicPath: '/'
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: [
          process.env.NODE_ENV === 'production' ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
          'postcss-loader'
        ]
      },
      {
        test: /\.scss$/,
        use: [
          process.env.NODE_ENV === 'production' ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
          'postcss-loader',
          'sass-loader'
        ]
      },
      {
        test: /\.(png|jpe?g|gif|svg)$/,
        loader: 'file-loader',
        options: {
          name: 'assets/[name].[ext]'
        }
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      template: './index.html',
      filename: 'index.html'
    }),
    new MiniCssExtractPlugin({
      filename: 'style.[contenthash].css'
    }),
    new Dotenv({
      path: `./.env${process.env.NODE_ENV ? `.${process.env.NODE_ENV}` : ''}`,
      expand: false
    })
  ],
  resolve: {
    extensions: ['.vue', '.js', '.json'],
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  devServer: {
    historyApiFallback: true,
    proxy: [
      {
        context: ['/api'],
        target: process.env.VUE_APP_API_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    ],
    port: 8080
  }
}
