const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');
const path = require('path');
var BundleTracker = require('webpack-bundle-tracker')

// 웹팩에 읽어야할 파일의 언어를 알려줘야함.
module.exports = {
    entry: "compiled.js",  
    plugins: [
        new HtmlWebpackPlugin({template: './src/index.html'}),
        new BundleTracker({filename: './webpack-state.json'})
    ],
    output: {
        path: path.resolve(__dirname + "/src"),
        filename: "bundle.js"
    },
    // 웹팩 빌드 옵션. producation은 최적화되어 빌드, development는 빠르게 빌드, none은 아무 기능 없이 웹팩을 빌드.
    mode: "none",

    module: {
        rules: [
            {
            test: /\.jsx$|js/,  // 가지고올 파일 확장자 정규식
            exclude: /node_modules/,
            use: [
                    {
                        loader: 'babel-loader',
                        options : {
                            presets: ['@babel/env', '@babel/react']
                        }
                    }
                ]
            },
            // {
            //     test: /\.html$/i,
            //     exclude: /node_modules/,
            //     use: [
            //         {
            //         loader: 'html-loader',
            //         options: { minimize: true }
            //         }
            //     ]
            // }
        ]
    },
    devServer: {
        contentBase: path.join(__dirname, 'src'),
        overlay: true,
        stats: 'errors-only',
        proxy: {
            '/api': 'http://localhost:4000'
        }
    },
    target: 'web',
};

// test: /\.jsx?$/,
// exclude: /(node_modules)/,
// loader: 'babel-loader',
// query: {
//     presets: ['react']
// }
