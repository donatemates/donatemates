module.exports = {
    entry: './index.jsx',
    output: {
        filename: 'dist/bundle.js', //this is the default name, so you can skip it
        //at this directory our bundle file will be available
        //make sure port 8090 is used when launching webpack-dev-server
        publicPath: 'http://localhost:8080/assets'
    },
    module: {
        loaders: [
            {
                test: /\.(jpg|png)$/,
                loader: 'url-loader',
                options: {
                    limit: 25000,
                },
            },
            {
                test: /\.jsx?$/,
                loader: "babel-loader",
                query: {
                    presets: ['react', 'es2015']
                }
            },
            {
                test: /\.less$/,
                use: [
                    'style-loader',
                    { loader: 'css-loader', options: { importLoaders: 1 } },
                    'less-loader'
                ]
            }
        ]
    }
}
