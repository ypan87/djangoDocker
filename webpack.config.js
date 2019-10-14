const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
    context: __dirname,
    entry: {
        "projectList": "./static/js/es6/projectList.js",
        "userProjectList": "./static/js/es6/userProjectList.js",
    },
    output: {
        path: path.resolve("./static/webpack_bundles/"),
        filename: "[name]-[hash].js"
    },
    plugins:[
        new BundleTracker({filename: "./webpack-stats.json"}),
        new CleanWebpackPlugin(),
    ]
};