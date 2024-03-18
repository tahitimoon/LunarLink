"use strict";
// 一些工具函数，用于辅助开发
const path = require("path");
const config = require("../config");
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const packageConfig = require("../package.json");

exports.assetsPath = function(_path) {
    const assetsSubDirectory =
        process.env.NODE_ENV === "production"
            ? config.build.assetsSubDirectory
            : config.dev.assetsSubDirectory;

    return path.posix.join(assetsSubDirectory, _path);
};

exports.cssLoaders = function(options) {
    options = options || {};

    const cssLoader = {
        loader: "css-loader",
        options: {
            sourceMap: options.sourceMap
        }
    };

    const postcssLoader = {
        loader: "postcss-loader",
        options: {
            sourceMap: options.sourceMap
        }
    };

    function generateLoaders(loader, loaderOptions) {
        const loaders = options.usePostCSS
            ? [cssLoader, postcssLoader]
            : [cssLoader];

        if (loader) {
            loaders.push({
                loader: loader + "-loader",
                options: Object.assign({}, loaderOptions, {
                    sourceMap: options.sourceMap
                })
            });
        }

        if (options.extract) {
            return ExtractTextPlugin.extract({
                use: loaders,
                fallback: "vue-style-loader"
            });
        } else {
            return ["vue-style-loader"].concat(loaders);
        }
    }

    return {
        css: generateLoaders(),
        postcss: generateLoaders(),
        less: generateLoaders("less"),
        sass: generateLoaders("sass", { indentedSyntax: true }),
        scss: generateLoaders("sass"),
        stylus: generateLoaders("stylus"),
        styl: generateLoaders("stylus")
    };
};

exports.styleLoaders = function(options) {
    const output = [];
    const loaders = exports.cssLoaders(options);

    for (const extension in loaders) {
        const loader = loaders[extension];
        output.push({
            test: new RegExp("\\." + extension + "$"),
            use: loader
        });
    }

    return output;
};

exports.createNotifierCallback = () => {
    const notifier = require("node-notifier");

    return (severity, errors) => {
        if (severity !== "error") return;

        const error = errors[0];
        const filename = error.file && error.file.split("!").pop();

        notifier.notify({
            title: packageConfig.name,
            message: severity + ": " + error.name,
            subtitle: filename || "",
            icon: path.join(__dirname, "logo.png")
        });
    };
};
