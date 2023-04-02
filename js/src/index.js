import * as API from "./api";
import "lightbox2";

class Racine {
    constructor(apiToken) {
        this.apiClient = new API.ApiClient(window.location.origin);
        this.apiClient.authentications["bearerAuth"].accessToken = apiToken;

        this.samplesApi = new API.SamplesApi(this.apiClient);
        this.sharesAPI = new API.SharesApi(this.apiClient);
        this.actionsAPI = new API.ActionsApi(this.apiClient);

        // Switch of automatic scroll restoration...
        // so that, if a popstate event occurs but the user does not want to leave the page, automatic scrolling to the top
        // is avoided. However, this means that if we navigate back to some page that was previously scrolled to a specific
        // location, we lose this information and the page is opened at 0 scroll position. This could be solved e.g. by
        // storing the scroll position in the history state variable.
        if ('scrollRestoration' in history) {
            history.scrollRestoration = 'manual';
        }
        // add event handler for history
        window.addEventListener("popstate", function (event) {
            if (event.state != null) {
                var res;
                if (typeof event.state.term !== "undefined") {
                    res = load_searchresults(event.state.term, false);
                } else if (typeof event.state.id !== "undefined") {
                    res = load_sample(event.state.id, false, false, true);
                } else {
                    res = load_welcome(false);
                }
                if (!res)  // the user wants to stay on the page to make modifications
                    push_current_state();
            }
            else
                location.href = "/";
        });

        // figure out what page to load
        if (typeof sample_id !== "undefined") {
            load_sample(sample_id, true);
        } else if (typeof term !== "undefined") {
            load_searchresults(term, true);
        } else {
            load_welcome(true);
        }

        // add window unload handler (which asks the user to confirm leaving the page when one of the CKEditor instances
        // has been modified
        window.addEventListener('beforeunload', before_unload_handler);

        // set up search field in header bar
        create_searchsample($('#navbar-search'));

        $('#navbar-search').bind('typeahead:selected', function (event, suggestion) {
            $(this).typeahead('val', '');    // clear the search field
            load_sample(suggestion.id);
        });

        $('#navbar-search').keypress(function (event) {
            if (event.which == 13) {
                // if currently viewing a sample (not welcome page) then change the navbar background to transparent
                if (typeof sample_id !== "undefined")
                    $('#nav-entry' + sample_id).css("background-color", "transparent");

                if ($(this).val() === '') {
                    error_dialog('Please specify a search term');
                } else {
                    load_searchresults($(this).val(), true);  // load the searchresults page
                    $(this).typeahead('val', '');    // clear the search field
                }
            }
        });

        function shareselected(event, suggestion) {
            R.sharesAPI.createShare(
                { "sampleid": sample_id, "username": $('#username').val() },
                function (error, data, response) {
                    if (!response)
                        error_dialog("Server error. Please check your connection.");
                    else if (response.error) {
                        if (response.body.message)
                            error_dialog(response.body.message);
                        else
                            error_dialog(response.error);
                    } else {
                        $('#sharelist').append(
                            '<div class="sharelistentry" id="sharelistentry' + data.shareid + '">' +
                            '<a data-type="share" data-id="' + data.shareid + '" data-toggle="modal" ' +
                            'data-target="#confirm-delete" href="">' +
                            '<i class="glyphicon glyphicon-remove"></i>' +
                            '</a>\n' + data.username +
                            '</div>'
                        );
                    }
                    $('#userbrowser').modal('hide');
                }
            );
        }

        // new sample dialog
        var newsampleparent = $('#newsampleparent');
        var newsampleparentid = $('#newsampleparentid')
        create_selectsample(newsampleparent, newsampleparentid);
        CKEDITOR.replace('newsampledescription', ckeditorconfig);

        $('#newsample').on('show.bs.modal', function (event) {
            // set the parent field to the current sample
            if (typeof sample_id !== 'undefined') {
                $('#newsampleparent').typeahead('val', $('#samplename').text());
                $('#newsampleparentid').val(sample_id);
            }
        });

        $('#newsample').on('shown.bs.modal', function () {
            // workaround for a bug in CKEditor -> if we don't do this after the editor is shown, a <br /> tag is inserted
            // if we tab to the editor
            CKEDITOR.instances['newsampledescription'].setData('');

            // put the cursor in the sample name field
            $('#newsamplename').focus();
        });

        $('#newsample').on('hide.bs.modal', function () {
            // clear the dialog
            $('#newsampleclear').trigger('click');
        });

        $('#newsampleclear').click(function (event) {
            event.preventDefault();

            $('#newsamplename').val('');
            newsampleparent.typeahead('val', '');
            newsampleparent.markvalid();
            newsampleparentid.val('');
            CKEDITOR.instances['newsampledescription'].setData('');
        });
        $('#newsamplesubmit').click(function (event) {
            event.preventDefault();

            var newsampleform = $('#newsampleform');

            // clean up error messages
            newsampleform.find('.form-group').removeClass('has-error');
            newsampleform.find('span.help-block').remove();

            // make sure content of editor is transmitted
            CKEDITOR.instances['newsampledescription'].updateElement();

            var formdata = {};
            newsampleform.serializeArray().map(function (x) { formdata[x.name] = x.value; });

            R.samplesAPI.createSample(formdata, function (error, data, response) {
                if (!response)
                    error_dialog("Server error. Please check your connection.");
                else if (response.error) {
                    if (response.body.error) {
                        // form failed validation; because of invalid data or expired CSRF token
                        for (field in response.body.error) {
                            if (field === 'csrf_token') {
                                error_dialog('The CSRF token has expired. Please reload the page to create a new sample.');
                                continue;
                            }
                            // get form group
                            var formgroupid = (field !== 'newsampleparentid' ? field : 'newsampleparent');
                            var formgroup = $('#' + formgroupid).closest('.form-group');
                            // add the has-error to the form group
                            formgroup.addClass('has-error')
                            // add the error message to the form group
                            for (i in response.body.error[field]) {
                                formgroup.append(
                                    '<span class="help-block">' +
                                    response.body.error[field][i] +
                                    '</span>'
                                );
                            }
                        }
                    } else {
                        error_dialog(response.error);
                    }
                } else {
                    $('#newsample').modal('hide');  // hide and clear the dialog
                    load_sample(data.sampleid);
                    load_navbar();
                }
            });
        });

        // "mark as news" dialog
        $('#dlg_markasnews_submit').click(function (event) {
            event.preventDefault();

            var dlg_markasnews_form = $('#dlg_markasnews_form');
            var actionid = $("#actionid").val();
            var flag_element = $('#togglenews-' + actionid);

            // clean up error messages
            dlg_markasnews_form.find('.form-group').removeClass('has-error');
            dlg_markasnews_form.find('span.help-block').remove();

            var formdata = {};
            dlg_markasnews_form.serializeArray().map(function (x) { formdata[x.name] = x.value; });

            R.actionsAPI.markActionAsNews(formdata, function (error, data, response) {
                if (!response)
                    error_dialog("Server error. Please check your connection.");
                else if (response.body && response.body.error) {
                    // form failed validation; because of invalid data or expired CSRF token
                    for (field in response.body.error) {
                        if (field === 'csrf_token') {
                            error_dialog('The CSRF token has expired. Please reload the page.');
                            continue;
                        }
                        // get form group
                        var formgroup = $('#' + field).closest('.form-group');
                        // add the has-error to the form group
                        formgroup.addClass('has-error')
                        // add the error message to the form group
                        for (i in response.body.error[field]) {
                            formgroup.append(
                                '<span class="help-block">' +
                                response.body.error[field][i] +
                                '</span>'
                            );
                        }
                    }
                } else {
                    // hide the dialog
                    $('#dlg_markasnews').modal('hide');

                    // toggle the flag
                    flag_element.removeClass('markasnews');
                    flag_element.addClass('unmarkasnews');
                }
            });
        });

        // datepicker
        $("#expires").attr("autocomplete", "off");
        $("#expires").datepicker({ dateFormat: "yy-mm-dd" });

        // set up the OK button and the enter button
        $('#userbrowserok').click(shareselected);
        $('#username').keyup(function (ev) { if (ev.keyCode == 13) shareselected(); });

        // user browser (for sample sharing)
        $('#userbrowser').on('show.bs.modal', function (event) {
            // empty the text field and disable autocompletion
            $('#username').val('');
            $('#username').typeahead('destroy');

            // empty recent collaborators list
            $('#recent-collaborators').html('');

            // update autocompletion for the text field and recent collaborators list
            $.ajax({
                url: "/userlist",
                type: "post",
                data: { "mode": "share", "sampleid": sample_id },
                success: function (data) {
                    // set up autocompletion
                    $('#username').typeahead({
                        minLength: 1,
                        highlight: true
                    },
                        {
                            name: 'users',
                            source: substringMatcher(data.users),
                            templates: {
                                suggestion: function (data) {
                                    return '<div><img src="/static/images/user.png" width="24px" height="24px">' + data + '</div>';
                                }
                            }
                        });
                    // make recent collaborators list
                    if (data.recent.length > 0)
                        $('#recent-collaborators').append('<div>Recent collaborators:<br>&nbsp</div>');
                    for (i in data.recent)
                        $('#recent-collaborators').append('<div class="user" data-name="' + data.recent[i] + '"><img src="/static/images/user.png">' + data.recent[i] + '</div>');
                    // set up click event
                    $('.user').one('click', function (event) {
                        $('#username').val($(this).data('name'));
                        shareselected();
                    });
                }
            });
        });

        // once the modal dialog is open, put the cursor in the username field
        $('#userbrowser').on('shown.bs.modal', function (event) { $('#username').focus(); });

        // sample and action deletion
        $('#confirm-delete').on('show.bs.modal', function (e) {
            $(this).find('.btn-ok').attr('id', $(e.relatedTarget).data('id'));
            $(this).find('.btn-ok').data('type', $(e.relatedTarget).data('type'));
            $('.debug-id').html('Delete <strong>' + $(e.relatedTarget).data('type') + '</strong> ID: <strong>' + $(this).find('.btn-ok').attr('id') + '</strong>');
        });

        $('.btn-ok').click(function (event) {
            var type = $(this).data('type');
            var id = $(this).attr('id');

            switch (type) {
                case "action":
                    R.actionsAPI.deleteAction(id, function (error, data, response) {
                        if (!response)
                            error_dialog("Server error. Please check your connection.");
                        else if (response.error) {
                            if (response.body.message)
                                error_dialog(response.body.message);
                            else
                                error_dialog(response.error);
                        } else {
                            $('#' + id + '.list-entry').remove();
                        }
                        $('#confirm-delete').modal('hide');
                    });
                    break;
                case "sample":
                    R.samplesAPI.deleteSample(id, function (error, data, response) {
                        if (!response)
                            error_dialog("Server error. Please check your connection.");
                        else if (response.error) {
                            if (response.body.message)
                                error_dialog(response.body.message);
                            else
                                error_dialog(response.error);
                        } else {
                            load_welcome(true);
                            load_navbar(undefined, undefined, false, true);
                        }
                        $('#confirm-delete').modal('hide');
                    });
                    break;
                case "share":
                    R.sharesAPI.deleteShare(id, function (error, data, response) {
                        if (!response)
                            error_dialog("Server error. Please check your connection.");
                        else if (response.error) {
                            if (response.body.message)
                                error_dialog(response.body.message);
                            else
                                error_dialog(response.error);
                        } else {
                            $('#sharelistentry' + id).remove();
                            if (response.status == 205) { // if the user removed himself from the sharer list
                                load_welcome(true);
                                load_navbar(undefined, undefined, false, true);
                            }
                            $('#confirm-delete').modal('hide');
                        }
                    });
                    break;
            }
        });
    }
}

export default Racine;