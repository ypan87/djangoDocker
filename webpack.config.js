const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
    context: __dirname,
    entry: {
        "projectList": ["@babel/polyfill", "./static/js/es6/projectList.js"],
        "userProjectList": ["@babel/polyfill", "./static/js/es6/userProjectList.js"],
        "projectCreate": ["@babel/polyfill", "./static/js/es6/projectCreate.js"],
        "project": ["@babel/polyfill", "./static/js/es6/project.js"],
        "sizerCreate": ["@babel/polyfill", "./static/js/es6/sizerCreate.js"],
        "sizerEdit": ["@babel/polyfill", "./static/js/es6/sizerEdit.js"],
        "login": ["@babel/polyfill", "./static/js/es6/login.js"],
        "register": ["@babel/polyfill", "./static/js/es6/register.js"],
        "forgetPwd": ["@babel/polyfill", "./static/js/es6/forgetPwd.js"],
        "passwordReset": ["@babel/polyfill", "./static/js/es6/passwordReset.js"],
    },
    output: {
        path: path.resolve("./static/webpack_bundles/"),
        filename: "[name]-[hash].js"
    },
    plugins:[
        new BundleTracker({filename: "./webpack-stats.json"}),
        new CleanWebpackPlugin(),
    ],
    module: {
        rules: [
            {
                "test": /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                },
            }
        ]
    }
};