function async_api_callback(loc, callback, ajax_params) {
    $.ajax({
        url: loc,
        type: "get",
        success: function(data, textStatus, jqXHR) {
            switch (jqXHR.status) {
                case 200:       // the server is ready
                    callback(data, textStatus, jqXHR);
                    break;
                case 202:       // we still have to wait
                    setTimeout(async_api_callback, 100, loc, callback, ajax_params);
                    break;
                default:
                    console.error("Unexpected status value during async API call.");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("Some error occured during async API call.", jqXHR);
            if(jqXHR.status == 400) {
                // TODO: get rid of this bug (see asyncapi.py)
                async_api_call(ajax_params);  // for now just send the original request again
            }
        }
    });
}

function async_api_call(ajax_params) {
    var ajax_params_copy = {};
    Object.assign(ajax_params_copy, ajax_params);
    var callback = ajax_params['success'];
    ajax_params['success'] = function(data, textStatus, jqXHR) {
        var loc = jqXHR.getResponseHeader('Location');
        setTimeout(async_api_callback, 100, loc, callback, ajax_params_copy);
    };
    $.ajax(ajax_params);
}