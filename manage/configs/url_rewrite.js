// Edge Node.js 4.3 Function for URL re-writes

exports.handler = (event, context, callback) => {
    var request = event.Records[0].cf.request;
    var parts = request.uri.split("?");
    parts = parts[0].split("/");
    if (parts[1] == "static"){
        callback(null, request);
    } else if (parts.indexOf("static") != -1){
        // Hit a rando URL. Do a redirect instead.
        const response = {
        status: '305',
        statusDescription: '305 Found',
        httpVersion: request.httpVersion,
        uri: "/404",
       };
       callback(null, response);
    }
    else{
        request.uri = "/index.html";
        callback(null, request);
    }
};