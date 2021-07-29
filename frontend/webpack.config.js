/* 웹서버는 빌드된 파일을 사용하기 때문에 미리 빌드 산출물을 만들어 놔야 한다. */ 
const HtmlWebpackPlugin = require('html-webpack-plugin');  // 웹팩에서 HTML을 다루기 위한 플러그인
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');
// const MiniCssExractPlugin = require('mini-css-extract-plugin');
// const webpack = require('webpack');  
const path = require('path'); // 절대경로 참조를 위해 불러옴
var BundleTracker = require('webpack-bundle-tracker');

// 웹팩에 읽어야할 파일의 언어를 알려줘야함.
module.exports = {
    // entry 웹팩에서 웹 자원을 변환하기 위해 필요한 최초 진입점이나 자바스크립트 파일 경로다. 이를 통해서 모듈을 로딩하고 하나의 파일로 묶는다.
    // 바벨로 번역되서 만든 compiled.js 를 사용할수도 있고 src 폴더를 사용할수도 있다.
    // 생성될 번들 파일은 js 폴더 하위에 index.js 라는 이름으로 생성될 것이며 이 파일은 ./src/index.js를 시작으로 번들링(하나로 합치기) 된다.
    entry: "./src/index.js",    
    // plugin 은 웹팩의 기본적인 동작 외 추가적인 기능을 제공하는 속성이다. loader는 파일을 해석하고 변환하는 과정에 관여하고, plugin은 결과물의 
    // 형태를 바꾸는 역할을 한다.
    plugins: [
        new HtmlWebpackPlugin({
            template: './public/index.html',  //'./src/index.html',
            favicon: './public/favicon.ico',
        }), // ./src/index.html 파일을 참조해 dist 경로에 index.html로 파일을 생성한다.
        new BundleTracker({
            fileName: './webpack-state.json'
        }),
        // 빌드된 번들링 결과물에 대한 manifest.json 파일로 저장하여 관리, 번들링될 때마다 번들 파일의 이름이 바뀌는 경우 참조에 문제가 생길수 있는데 이를 해결함
        // Manifest: Line: 1, column: 1, Syntax error. 에러 대응 
        new WebpackManifestPlugin({
            fileName: "manifest.json",
            basePath: "./dist/"
        }),
        // CSS 파일을 청킹하여 옵션으로 지정한 디렉토리를 생성한다. 한번에 모든 css를 읽는게 아니라 사용자가 필요할 때만 읽게 한다.
        // 웹팩 버전 5 이상에서만 가능하다.
        // new MiniCssExractPlugin({
        //     linkType: false,
        //     filename: 'static/css/[name].[contenthash:8].css',
        //     chunkFilename: 'static/css/[id].[contenthash:8].chunk.css',
        // }),
    ],
    // output 은 entry 로 찾은 모듈을 하나로 묶은 결과물을 반환할 위치다.
    output: {
        path: path.resolve(__dirname,"dist/"),  //path: path.resolve(__dirname + "/src") 또는 ../dist/js/,
        // 
        publicPath:'./', //HTML 등 다른 파일에서 생성된 번들을 참조할 때, /을 기준으로 참조한다. 
        // 브라우저에는 캐싱기능이 있다 hash 는 컴파일될 때마다 웹팩에서 생성된 해시로 변경해주어 브라우저에 캐싱되는 대상의 내용이(파일 내용)
        // 바뀌었다고 알려주는데 도움이 된다.
        // 하지만 기존의 app.js 파일이 남아있기 때문에 이를 제거하는 로직이 필요하다.
        filename: "app[hash].js"  
    },




    
    // resolve.extensions 는 import 할 때 확장자를 붙이지 않아도 되도록 하는 역할을 한다.
    // resolve: {
    //     extensions: ['js','jsx']
    // },
    // 웹팩 빌드 옵션. production 은 최적화되어 빌드, development 는 빠르게 빌드, none은 아무 기능 없이 웹팩을 빌드.
    mode: "development",
    devtool: 'inline-souce-map',  // 소스맵을 생성해 디버깅을 도와준다.
    module: {
        rules: [
            {
            test: /\.jsx$|js/,  // 빌드할 파일 확장자 정규식
            exclude: /node_modules/,  //제외할 파일 정규식
            use: [
                    {
                        // 웹팩은 기본적으로 자바스크립트와 JSON 만 빌드할수 있다. 자바스크립트가 아닌 다른 자원(HTML, CSS, Image)를 빌드할수 있도록
                        // 도와주는 속성이다.
                        loader: 'babel-loader',  // 사용할 로더 이름
                        options : {
                            presets: [
                                [
                                    '@babel/preset-env' ,{
                                        targets: {
                                            browsers: ["last 2 versions", ">=5% in KR"],
                                        },
                                        debug: true,
                                    },],
                                // 로더 옵션 : 바벨을 이용하여 빌드                                 
                                '@babel/preset-react'
                            ],  
                            // @babel/plugin-transform-runtime 추가: 애플리케이션이 컴파일될 때 regeratorRuntime 이 async/await 문법을 번역
                            // 하도록 했는데 해당 ragenerator를 제공하지 않아서 에러가 발생한다.
                            plugins: ['@babel/plugin-proposal-class-properties', '@babel/plugin-transform-runtime'],
                        },
                    },
                ],
            },

            {
                test: /\.(sass|less|css)$/,
                use: [
                    'style-loader',
                    'css-loader',
                    {
                        loader: "postcss-loader",
                        options: {
                            plugins: () => [
                                require("autoprefixer")()
                            ],
                        },
                    },
                    'sass-loader',
                ]
            },

            // {
            //     test: /\.html$/,
            //     use: [
            //         {
            //         loader: 'html-loader',
            //         options: {
            //              minimize: true 
            //             },
            //         },
            //     ],
            // },
        ],
    },

    devServer: {
        contentBase: path.join(__dirname, 'src'),
        overlay: true,
        stats: 'errors-only',
        proxy: {
            // 서버의 도메인 입력 (또는 서버의 ip)
            '/api': 'http://127.0.0.1:4000'  //'http://localhost:4000'
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
