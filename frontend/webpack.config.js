const path = require('path')
const fs = require('fs')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const { DefinePlugin } = require('webpack')
const Dotenv = require('dotenv-webpack')

let proxyTarget = 'http://100.122.225.103:8000'
const envDevPath = path.resolve(__dirname, '.env.development')
if (fs.existsSync(envDevPath)) {
  const envContent = fs.readFileSync(envDevPath, 'utf-8')
  const match = envContent.match(/VUE_APP_API_TARGET\s*=\s*(.+)/)
  if (match && match[1]) {
    proxyTarget = match[1].trim()
  }
}

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
        exclude: /node_modules\/(?!simple-mind-map)/
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
        target: proxyTarget,
        changeOrigin: true,
        secure: false
      }
    ],
    port: 8080,
    client: {
      overlay: {
        errors: true,
        warnings: false
      }
    }
  }
}
