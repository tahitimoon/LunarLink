"use strict";
const utils = require("./utils");
const webpack = require("webpack");
const config = require("../config");
const merge = require("webpack-merge");
const path = require("path");
const baseWebpackConfig = require("./webpack.base.conf");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const FriendErrorsPlugin = require("friendly-errors-webpack-plugin");
const portfinder = require("portfinder");
const MonacoWebpackPlugin = require("monaco-editor-webpack-plugin");
const HOST = process.env.HOST;
const PORT = process.env.PORT && Number(process.env.PORT);

const devWebpackConfig = merge(baseWebpackConfig, {
    module: {
        rules: utils.styleLoaders({
            sourceMap: config.dev.cssSourceMap,
            usePostCSS: true
        })
    },
    devtool: config.dev.devtool,

    devServer: {
        clientLogLevel: "warning",
        historyApiFallback: {
            rewrites: [
                {
                    form: /.*/,
                    to: path.posix.join(
                        config.dev.assetsPublicPath,
                        "index.html"
                    )
                }
            ]
        },
        hot: true,
        contentBase: false, // since we use CopyWebpackPlugin.
        compress: true,
        host: HOST || config.dev.host,
        port: PORT || config.dev.port,
        open: config.dev.errorOverlay,
        overlay: config.dev.errorOverlay
            ? { warnings: false, errors: true }
            : false,
        publicPath: config.dev.assetsPublicPath,
        proxy: config.dev.proxyTable,
        quiet: true,
        watchOptions: {
            poll: config.dev.poll
        }
    },
    plugins: [
        new webpack.DefinePlugin({
            "process.env": require("../config/dev.env")
        }),
        new MonacoWebpackPlugin(),
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NamedModulesPlugin(),
        new webpack.NoEmitOnErrorsPlugin(),
        new HtmlWebpackPlugin({
            filename: "index.html",
            template: "index.html",
            inject: true
        }),
        new CopyWebpackPlugin([
            {
                from: path.resolve(__dirname, "../static"),
                to: config.dev.assetsSubDirectory,
                ignore: [".*"]
            }
        ])
    ]
});

module.exports = new Promise((resolve, reject) => {
    portfinder.basePort = process.env.PORT || config.dev.port;
    portfinder.getPort((err, port) => {
        if (err) {
            reject(err);
        } else {
            process.env.PORT = `${port}`;
            devWebpackConfig.devServer.port = port;

            devWebpackConfig.plugins.push(
                new FriendErrorsPlugin({
                    compilationSuccessInfo: {
                        messages: [
                            `Your application is running here: http://${devWebpackConfig.devServer.host}:${port}`
                        ]
                    },
                    onErrors: config.dev.notifyOnErrors
                        ? utils.createNotifierCallback()
                        : undefined
                })
            );

            resolve(devWebpackConfig);
        }
    });
});
