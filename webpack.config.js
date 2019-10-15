const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
    context: __dirname,
    entry: {
        "projectList": "./static/js/es6/projectList.js",
        "userProjectList": "./static/js/es6/userProjectList.js",
        "projectCreate": "./static/js/es6/projectCreate.js",
        "project": "./static/js/es6/project.js",
        "sizerCreate": "./static/js/es6/sizerCreate.js"
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