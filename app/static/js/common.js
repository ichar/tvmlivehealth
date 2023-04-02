// *******************
// COMMON DECLARATIONS
// -------------------
// Version: 2.00
// Date: 12-11-2021

var keywords = new Object();
var script_version = 1;
var default_timeout = 100;
var default_loader_timeout = 300;

var IsDebug = 0;                   // Turn on/off Debug-mode  
var IsDeepDebug = 0;               // Turn on/off DeepDebug-mode  
var IsTrace = 0;                   // Turn on/off Trace-mode
var IsLog = 0;                     // Turn on/off console log
var IsTraceCommit = 0;             // Alert Field's state controller Commit-errors
var IsTraceRollback = 0;           // Alert Field's state controller Rollback-errors
var IsTraceErrorException = 0;     // Alert(show) error exception
var IsForcedRefresh = 0;           // Forced refresh any images in filesystem-cache (load with timestamp-link)
var IsHideContextMenu = 0;         // Hide default context menu and trigger right-mouse event for make custom menu: 0|1|2
var IsAdmin = 0;                   // User Admin permissions
var IsOperator = 0;                // User Operator permissions
var IsAssumeExchangeError = 0;     // Exchange errors allowed or not (for localhost debug reasons)
var IsXMLDump = 0;                 // For 'internal' only - dump request/response or not
var IsCleanBefore = 1;             // For 'internal' only - how to referesh items (clean before or not)
var IsCheckImageTimeout = 0;       // Wait images will be refreshed before init a new state
var IsTriggeredSubmit = 0;         // Show/Hide startup page
var IsShowLoader = 0;              // Apply submit image
var IsActiveScroller = 1;          // Activate (show/hide) scroller on main container
var IsWithoutProgress = 0;         // Apply progress styles or not 


// ----------------
//  Public Options:
// ----------------

var IsOptionRowspan = 0;           // Use rowspan check
var IsNoDropdown = 1;
var IsSidebarEnabled = 1;

// ----------
//  Browsers:
// ----------

var IsMSIE = 0;
var is_webkit = 0;

// ---------------------------------------------------------
//  Line Page Submit Type:
//  0 - page submit, 1 - startup action, 2 - selected action
// ---------------------------------------------------------
var default_submit_mode = 0;
var default_action = null;         // Action code for default refreshing (SUBLINE), submit mode > 0
var default_log_action = null;     // Action code for refreshing Log Tab area
var default_print_action = null;   // Action code for printing Log Tab area
var default_handler = null;        // Handler for Log Action, optionally
var default_params = null;         // Params for Log Action, optionally
var default_input_name = '';       // Name of LINE input tag

var should_be_updated = false;     // Optional flag to update LINE

var current_context = '';          // Current context name
var placeholder = '';              // Search placeholder text

var selected_menu_action = null;   // Selected DataMenu Action
var selected_control = null;       // Selected form's control

var semaphore_state = null;
var treeview_state = null;

var active_dialog = null;          // Active dialog for error keypress 
var loader_page = '';

var documents_dialog_active = 1;   // Default for Documents Schedule dialog
var decrees_dialog_active = 1;     // Default for Decrees Schedule dialog

// ==========================================================================================================

// ----------------
// Global Constants
// ----------------

var TID = new Array();

var LINE = '';
var SUBLINE = '';
var TABLINE = 'tabline';
var REFERENCE = 'reference';

var isWebServiceExecute = false;
var isSubmitted = false;
var isKeyboardDisabled = false;
var isConfirmation = false;
var isDropdownActive = false;
var isCallback = false;

var confirm_action = '';
var confirm_response = null;

var DEFAULT_HTML_SPLITTER = '_';

var CSS_INVISIBLE = 'invisible';

var schedule_documents = [0, 0];   // Schedule document templates count
var schedule_decrees = [0, 0];     // Schedule decree templates count 

// ------------
// Module items
// ------------

var model = 0;
var root = '';
var back = '';
var baseURI = '';
var loaderURI = '';

var design_settings = new Object();

var page_state = -1;
var page_scroll_top = 0;

var is_loaded_success = false;
var is_show_error = false;
var is_link = false;
var is_scroll_top = false;
var is_on_refresh = false;

var no_window_scroll = false;

// ----------------
// Global Functions
// ----------------

function interrupt(start, mode, timeout, callback, index, type) {
    //
    //  start [true, false] - фаза исполнения: true-старт, false-финиш
    //  mode - индекс алгоритма
    //  timeout - длительность таймаута
    //  callback - функция обратного вызова[9] (строка) или строковый параметр[-1]
    //  index - индекс таймаута
    //  type - тип функции: 0/1, setTimeout/setInterval
    //
    if (start) {
        var i = !is_null(index) ? index : TID.length;
        //var s = "interrupt(false, "+mode+", 0, "+(callback ? "'"+callback+"'" : 'null')+", "+i+")";
        var delay = timeout ? timeout : default_timeout;
        var func = function() { interrupt(false, mode, 0, callback, i, type); };
        if (i == TID.length) TID.push(null);
        //TID[i] = (type === 1) ? window.setInterval(func, delay) : window.setTimeout(func, delay);
        if (type == 1)
            TID[i] = window.setInterval(func, delay);
        else
            TID[i] = window.setTimeout(func, delay);

        if (IsLog)
            console.log('start:'+mode+', index:'+i+', len:'+TID.length);

    } else if (mode) {
        if (IsLog)
            console.log('interrupt:'+mode+', TID:'+TID.join('-'));

        if (mode == -1) {
            if (!callback) callback = '';
            window.location.replace(callback);
        } else if (mode == 1) {
            interrupt(false, 0, 0, null, index);
            $ShowOnStartup();
        } else if (mode == 2) {
            interrupt(false, 0, 0, null, index);
            $ReferenceDialog.submit('refresh');
        } else if (mode == 3) {
            interrupt(false, 0, 0, null, index);
            $LineSelector.onReset();
        } else if (mode == 4) {
            interrupt(false, 0, 0, null, index);
            $onClickTreeView();
        } else if (mode == 5) {
            interrupt(false, 0, 0, null, index);
            $SublineSelector._refresh(0);
        } else if (mode == 9)
            $Semaphore.run(index);

    } else if (TID.length > index && TID[index] != null) {
        if (type == 1)
            window.clearInterval(TID[index]);
        else 
            window.clearTimeout(TID[index]);

        if (index == TID.length-1)
            TID.splice(index, 1);
        else
            TID[index] = null;

        if (IsLog)
            console.log('stop index:'+index+', len:'+TID.length);
    }
}
function beep() {
    var data = "||uQRAAAAWMSLwUIYAAsYkXgoQwAEaYLWfkWgAI0wWs|ItAAAGDgYtAgAyN+QWaAAihwMWm4G8QQRDiMcCBcH3Cc+CDv|7xA4Tvh9Rz|y8QADBwMWgQAZG|ILNAARQ4GLTcDeIIIhxGOBAuD7hOfBB3|94gcJ3w+o5|5eIAIAAAVwWgQAVQ2ORaIQwEMAJiDg95G4nQL7mQVWI6GwRcfsZAcsKkJvxgxEjzFUgfHoSQ9Qq7KNwqHwuB13MA4a1q|DmBrHgPcmjiGoh||EwC5nGPEmS4RcfkVKOhJf+WOgoxJclFz3kgn||dBA+ya1GhurNn8zb||9NNutNuhz31f||||9vt|||z+IdAEAAAK4LQIAKobHItEIYCGAExBwe8jcToF9zIKrEdDYIuP2MgOWFSE34wYiR5iqQPj0JIeoVdlG4VD4XA67mAcNa1fhzA1jwHuTRxDUQ||iYBczjHiTJcIuPyKlHQkv|LHQUYkuSi57yQT||uggfZNajQ3Vmz+Zt||+mm3Wm3Q576v||||+32|||5|EOgAAADVghQAAAAA||uQZAUAB1WI0PZugAAAAAoQwAAAEk3nRd2qAAAAACiDgAAAAAAABCqEEQRLCgwpBGMlJkIz8jKhGvj4k6jzRnqasNKIeoh5gI7BJaC1A1AoNBjJgbyApVS4IDlZgDU5WUAxEKDNmmALHzZp0Fkz1FMTmGFl1FMEyodIavcCAUHDWrKAIA4aa2oCgILEBupZgHvAhEBcZ6joQBxS76AgccrFlczBvKLC0QI2cBoCFvfTDAo7eoOQInqDPBtvrDEZBNYN5xwNwxQRfw8ZQ5wQVLvO8OYU+mHvFLlDh05Mdg7BT6YrRPpCBznMB2r||xKJjyyOh+cImr2|4doscwD6neZjuZR4AgAABYAAAABy1xcdQtxYBYYZdifkUDgzzXaXn98Z0oi9ILU5mBjFANmRwlVJ3|6jYDAmxaiDG3|6xjQQCCKkRb|6kg|wW+kSJ5||rLobkLSiKmqP|0ikJuDaSaSf|6JiLYLEYnW|+kXg1WRVJL|9EmQ1YZIsv|6Qzwy5qk7|+tEU0nkls3|zIUMPKNX|6yZLf+kFgAfgGyLFAUwY||uQZAUABcd5UiNPVXAAAApAAAAAE0VZQKw9ISAAACgAAAAAVQIygIElVrFkBS+Jhi+EAuu+lKAkYUEIsmEAEoMeDmCETMvfSHTGkF5RWH7kz|ESHWPAq|kcCRhqBtMdokPdM7vil7RG98A2sc7zO6ZvTdM7pmOUAZTnJW+NXxqmd41dqJ6mLTXxrPpnV8avaIf5SvL7pndPvPpndJR9Kuu8fePvuiuhorgWjp7Mf|PRjxcFCPDkW31srioCExivv9lcwKEaHsf|7ow2Fl1T|9RkXgEhYElAoCLFtMArxwivDJJ+bR1HTKJdlEoTELCIqgEwVGSQ+hIm0NbK8WXcTEI0UPoa2NbG4y2K00JEWbZavJXkYaqo9CRHS55FcZTjKEk3NKoCYUnSQ0rWxrZbFKbKIhOKPZe1cJKzZSaQrIyULHDZmV5K4xySsDRKWOruanGtjLJXFEmwaIbDLX0hIPBUQPVFVkQkDoUNfSoDgQGKPekoxeGzA4DUvnn4bxzcZrtJyipKfPNy5w+9lnXwgqsiyHNeSVpemw4bWb9psYeq||uQZBoABQt4yMVxYAIAAAkQoAAAHvYpL5m6AAgAACXDAAAAD59jblTirQe9upFsmZbpMudy7Lz1X1DYsxOOSWpfPqNX2WqktK0DMvuGwlbNj44TleLPQ+Gsfb+GOWOKJoIrWb3cIMeeON6lz2umTqMXV8Mj30yWPpjoSa9ujK8SyeJP5y5mOW1D6hvLepeveEAEDo0mgCRClOEgANv3B9a6fikgUSu|DmAMATrGx7nng5p5iimPNZsfQLYB2sDLIkzRKZOHGAaUyDcpFBSLG9MCQALgAIgQs2YunOszLSAyQYPVC2YdGGeHD2dTdJk1pAHGAWDjnkcLKFymS3RQZTInzySoBwMG0QueC3gMsCEYxUqlrcxK6k1LQQcsmyYeQPdC2YfuGPASCBkcVMQQqpVJshui1tkXQJQV0OXGAZMXSOEEBRirXbVRQW7ugq7IM7rPWSZyDlM3IuNEkxzCOJ0ny2ThNkyRai1b6ev||3dzNGzNb||4uAvHT5sURcZCFcuKLhOFs8mLAAEAt4UWAAIABAAAAAB4qbHo0tIjVkUU||uQZAwABfSFz3ZqQAAAAAngwAAAE1HjMp2qAAAAACZDgAAAD5UkTE1UgZEUExqYynN1qZvqIOREEFmBcJQkwdxiFtw0qEOkGYfRDifBui9MQg4QAHAqWtAWHoCxu1Yf4VfWLPIM2mHDFsbQEVGwyqQoQcwnfHeIkNt9YnkiaS1oizycqJrx4KOQjahZxWbcZgztj2c49nKmkId44S71j0c8eV9yDK6uPRzx5X18eDvjvQ6yKo9ZSS6l||8elePK|Lf||IInrOF|FvDoADYAGBMGb7FtErm5MXMlmPAJQVgWta7Zx2go+8xJ0UiCb8LHHdftWyLJE0QIAIsI+UbXu67dZMjmgDGCGl1H+vpF4NSDckSIkk7Vd+sxEhBQMRU8j|12UIRhzSaUdQ+rQU5kGeFxm+hb1oh6pWWmv3uvmReDl0UnvtapVaIzo1jZbf|pD6ElLqSX+rUmOQNpJFa|r+sa4e|pBlAABoAAAAA3CUgShLdGIxsY7AUABPRrgCABdDuQ5GC7DqPQCgbbJUAoRSUj+NIEig0YfyWUho1VBBBA||uQZB4ABZx5zfMakeAAAAmwAAAAF5F3P0w9GtAAACfAAAAAwLhMDmAYWMgVEG1U0FIGCBgXBXAtfMH10000EEEEEECUBYln03TTTdNBDZopopYvrTTdNa325mImNg3TTPV9q3pmY0xoO6bv3r00y+IDGid|9aaaZTGMuj9mpu9Mpio1dXrr5HERTZSmqU36A3CumzN|9Robv|Xx4v9ijkSRSNLQhAWumap82WRSBUqXStV|YcS+XVLnSS+WLDroqArFkMEsAS+eWmrUzrO0oEmE40RlMZ5+ODIkAyKAGUwZ3mVKmcamcJnMW26MRPgUw6j+LkhyHGVGYjSUUKNpuJUQoOIAyDvEyG8S5yfK6dhZc0Tx1KI|gviKL6qvvFs1+bWtaz58uUNnryq6kt5RzOCkPWlVqVX2a|EEBUdU1KrXLf40GoiiFXK|||qpoiDXrOgqDR38JB0bw7SoL+ZB9o1RCkQjQ2CBYZKd|+VJxZRRZlqSkKiws0WFxUyCwsKiMy7hUVFhIaCrNQsKkTIsLivwKKigsj8XYlwt|WKi2N4d||uQRCSAAjURNIHpMZBGYiaQPSYyAAABLAAAAAAAACWAAAAApUF|Mg+0aohSIRobBAsMlO||Kk4soosy1JSFRYWaLC4qZBYWFRGZdwqKiwkNBVmoWFSJkWFxX4FFRQWR+LsS4W|rFRb|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||VEFHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAU291bmRib3kuZGUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMjAwNGh0dHA6Ly93d3cuc291bmRib3kuZGUAAAAAAAAAACU=";
    var snd = new Audio("data:audio/wav;base64,"+data.replace(/^\|$/g,'/'));
    snd.play();
}

function $_mobile() {
    return $IS_FRAME == 1 ? false : ($IS_MOBILE ? true : false);
}

function $_window_orientation() {
    return typeof(window.orientation) !== 'undefined' ? (
        window.orientation == 0 || window.orientation == 180 ? 'portrait' : 'landscape') : (
        screen.msOrientation || screen.mozOrientation || (screen.orientation || {}).type);
}

function $_window_portrait() {
    return $_window_orientation().startswith('portrait');
}

function $_window_landscape() {
    return $_window_orientation().startswith('landscape');
}

function $_screen_with_scroll(mode, offset) {
    if (['height', 'H'].indexOf(mode) > -1)
        //return $_height('max') > window.screen.height;
        return document.body.clientHeight + (offset || 0) > $_height('available');
    //return $_width('max') > window.screen.width;
    return document.body.clientWidth + (offset || 0) > $_width('available');
}

function $_get_css_size(value, x) {
    return value.toString()+(x ? x : "px");
}

function $_screen_center(mode) {
    var m = mode || 'available';
    return { 'W':$_width(m), 'H':$_height(m) };
}

function $_height(m) {
    var f = $_mobile();
    if (m == 'screen-max')
        return Math.max(window.screen.availHeight, verge.viewportH());
    if (m == 'screen-min' || m == 'mobile')
        return Math.min(window.screen.availHeight, verge.viewportH());
    if (m == 'max')
        return Math.max(
            verge.viewportH(),
            window.screen.height, 
            window.screen.availHeight, 
            document.body.clientHeight, 
            document.documentElement.clientHeight,
            window.innerHeight,
            window.outerHeight
        );
    if (m == 'available' && f) {
        var mode = $_window_portrait() ? 'screen-max' : 'client';
        //var mode = 'screen-max';
        return $_height(mode);
    }
    if (m == 'client' || m == 'available')
        return document.documentElement.clientHeight || $_height('screen-min');
    else
        return Math.min(
            verge.viewportH(),
            window.screen.height,
            window.screen.availHeight,
            document.body.clientHeight,
            document.documentElement.clientHeight,
            window.innerHeight,
            window.outerHeight
        );
}
/***
 * 
 * verge.viewportH() == document.documentElement.clientHeight == window.innerHeight (available screen height)
 * window.screen.height != window.screen.availHeight (device screen height)
 * window.screen.height == window.outerHeight is max (window is maximized)!
 * window.screen.availHeight and document.body.clientHeight is almost the same (with scrollbar offset)
 * document.body.clientHeight == document.documentElement.scrollHeight == document.body.offsetHeight (just the same)
 * 
 ****/
function show_height() {
    alert(joinToPrint(['height:',
	'viewport:',
        verge.viewportH(),
        document.documentElement.clientHeight,
	'screen:',
        window.screen.height,
	'avail:',
        window.screen.availHeight,
    'client:',
        document.body.clientHeight,
        document.documentElement.scrollHeight,
        document.body.offsetHeight,
	'inner-outer:',
        window.innerHeight,
        window.outerHeight,
    ' max:',
        $_height('max')
    ]));
}

function show_width() {
    alert(joinToPrint(['width:',
    'viewport:',
        verge.viewportW(),
        document.documentElement.clientWidth,
    'screen:',
        window.screen.width,
    'avail:',
        window.screen.availWidth,
    'client:',
        document.body.clientWidth,
        document.documentElement.scrollWidth,
        document.body.offsetWidth,
    'inner-outer:',
        window.innerWidth,
        window.outerWidth,
    ' max:',
        $_width('max')
    ]));
}

function win_is_max_height() {
    return window.outerHeight >= window.screen.height && 
        document.documentElement.scrollHeight >= window.innerHeight &&
        verge.viewportH() == window.innerHeight;
}

function $_width(m) {
    var f = $_mobile();
    if (m == 'screen-max')
        return Math.max(window.screen.availWidth, verge.viewportW());
    if (m == 'screen-min' || m == 'mobile')
        return Math.min(window.screen.availWidth, verge.viewportW());
    if (m == 'max')
        return Math.max(
            verge.viewportW(),
            window.screen.width,
            window.screen.availWidth,
            document.body.clientWidth,
            document.documentElement.clientWidth
        );
    if (m == 'available' && f) {
        //var mode = $_window_portrait() ? 'screen-max' : 'screen-min';
        var mode = 'screen-max';
        return $_width(mode);
    }
    if (m == 'client' || m == 'available')
        return document.documentElement.clientWidth;
    else
        return Math.min(
            verge.viewportW(),
            window.screen.width, 
            window.screen.availWidth, 
            document.body.clientWidth, 
            document.documentElement.clientWidth
        );
}

function $_get_item_id(ob, index) {
    var x = (is_exist(ob) && ob.attr('id')) || 0;
    //var x = ob.attr('id') || 0;
    var id = (x && x.indexOf(DEFAULT_HTML_SPLITTER) > -1 && x.startswith('row')) ? 
        x.split(DEFAULT_HTML_SPLITTER) : x;
    if (index < 0) {
        return id.slice(1, index).join(DEFAULT_HTML_SPLITTER);
    }
    return id[index || 1] || id;
}

function $_get_item_number(ob, index) {
    var x = (!is_empty(ob) && ob.attr('id')) || 0;
    //var x = ob.attr('id') || 0;
    var id = (x && x.indexOf(DEFAULT_HTML_SPLITTER) > -1 && x.startswith('row')) ? 
        x.split(DEFAULT_HTML_SPLITTER) : x;
    var num = 0;
    if (index) {
        if (index == -1 || index > 1) {
            num = id.slice(index);
        }
        else {
            num = id.slice(1);
        }
        //alert(num);
    }
    else {
        num = id;
    }
    return num;
}

function $_maximize() {
    window.moveTo(0, 0);
    window.resizeTo($_width('max'), $_height('max'));
}

function $_set_body_value(id, value) {
    $("#"+id).each(function() { $(this).val(value); });
}

function $_box_position(ob, id) {
    var scrolltop = int($(window).scrollTop());
    var p = { top: 0, left: 0, height: 0, width: 0 };

    if (is_null(ob)) {
        if (IsDebug)
            alert("$_box_position: object is undefined!" + id);
        return p;
    }

    var c = ob.get(0).getBoundingClientRect();
    
    p.top = c.top + scrolltop;
    p.left = c.left;
    p.height = ob.height();
    p.width = ob.width();

    return p;
}

function $_show_window_in_center(container, mode, without_scroll) {
    var page = $("#html-container");
    var sh = 20;
    var sw = 0;
    var center = $_screen_center(mode);
    var top = int((center.H-container.height())/2) - sh;
    var left = int((center.W-container.width())/2) - sw;

    if ($_screen_with_scroll('H') && is_null(without_scroll))
        top += $(window).scrollTop();

    container
        .css('top', $_get_css_size(top)).css('left', $_get_css_size(left))
        .show();
}

function $_init() {
    // ------------------------------------------
    // PAGE STARTER. Call it to begin manage page
    // ------------------------------------------
    is_webkit = !(isIE || IsMSIE) ? true : false;

    // ===============
    // Design Settings
    // ===============

    var ratio = window.devicePixelRatio;

    design_settings = {
        'dialog' : {
            'body_default_width' : 1280,
            'offset_height' : 8,
            'top' : 40,
            'container_limit_height' : 800,
            'scrool_width' : 16,
            'window_ratio' : (ratio > 1 ? ratio : 1),
        }
    };

    $Images.init();

    $MenuSelector.init(current_context);
}

function $_change_location(state, url) {
    //var location = ''; //window.location.href.split(window.location.pathname)[0];
    window.history.pushState(state, '');
    window.location.replace(url);
}

function $onImagesPreload() {
    $ShowPageSubmitMessages();
    
    $Init();

    if (typeof($_show_page) === 'function')
        return;
        
    $ShowPage(0);
}

function $onMenuSelect(ob) {
    var url = ob.prop("href");
    if (!is_empty(url))
        window.location.replace(url);
}

// ===============
// Action Handlers
// ===============

function $CurrentContext() {
    // ------------------------------------------------------------------
    // Returns the page current context: bankperso|provision|workflow|...
    // ------------------------------------------------------------------
    return current_context || 'default';
}

function $ShowPage(disable) {
    // ------------------------------------
    // Hides or shows global HTML-CONTAINER
    // ------------------------------------
    if (disable === null)
        return;
    var startup_page_container = $("#html-container");
    if (disable)
        startup_page_container.hide();
    else
        startup_page_container.removeClass("hidden").show();
}

function $ShowOnStartup() {
    // -----------------------------------------------------------------------------
    // Handles default startup action of the page: default_log_action (show subline)
    // -----------------------------------------------------------------------------
    selected_menu_action = default_log_action;
    $Handle(
        selected_menu_action, default_handler, default_params
    );
}

function $ShowSubline(action) {
    // ------------------------------------------
    // Handles given action or default_log_action
    // ------------------------------------------
    selected_menu_action = !is_null(action) ? action : default_log_action;
    $Go(
        selected_menu_action
    );
}

function $ShowPageSubmitMessages() {
    // -----------------------------------------------
    // Shows error after submit or page submit message
    // -----------------------------------------------
    function _get_object(id) {
        var ob = $("#"+id);
        return is_exist(ob) ? ob.val() : null;
    }

    var errors = _get_object('errors');
    var OK = _get_object('OK');

    if (!is_empty(errors))
        $ShowError(errors, true, true, false);

    else if (!is_empty(OK))
        $NotificationDialog.open(OK);
}

function $ShowSystemMessages(reset, error) {
}

function $TriggerActions(disable) {
    if (IsTriggeredSubmit && default_submit_mode == 0)
        $ShowPage(disable);
}

function $ShowError(msg, is_ok, is_error, is_session_close) {
    if (is_show_error || !msg)
        return;

    if (!is_null(active_dialog))
        active_dialog.dialog("option", "closeOnEscape", false);

    var container = $("#error-container");

    $("#error-text").html(msg);

    if (is_ok) {
        $("#error-button").append(
            '<button id="error-button-ok" class="ui-button-text" onclick="javascript:$HideError();">'+keywords['OK']+'</button>'
        );
    }
    if (is_error)
        container.removeClass("warning").addClass("error");
    else
        container.removeClass("error").addClass("warning");

    $_show_window_in_center(container, null, true);
    
    is_show_error = true;

    $("#error-button-ok").focus();

    if (is_session_close && !$IS_DEMO) interrupt(true, -1, 5000, '', 0);
}

function $HideError() {
    $("#error-container").hide();
    $("#error-button").html('');

    if (!is_null(active_dialog))
        active_dialog.dialog("option", "closeOnEscape", true);

    is_show_error = false;

    $SetFocus();
}

function $ShowLoader(start) {
    //alert('loader:'+start+':'+isWebServiceExecute);

    if (is_show_error)
        return;

    if (start) {
        var loader = $("#page-loader");
        var container = $("#html-container");
        if (start == -1) { 
            isWebServiceExecute = false;
            if (IsShowLoader)
                loader.hide();
            else
                container.removeClass("inprogress");
            $InProgress(null);
        } else {
            isWebServiceExecute = true;
            if (IsShowLoader)
                $_show_window_in_center(loader, 'available');
            else
                container.addClass("inprogress");
        }
    }
}

function $ActivateInfoData(show) {
    var container = $("#info-data");

    if (is_null(container))
        return;

    if (show)
        container.show();
    else {
        container.hide();
        return;
    }

    $PageScroller.reset(true);
}

function $RemoveInfoData() {
    var container = $("#info-data");

    if (is_null(container))
        return;

    container.empty().hide();
}

function $InProgress(ob, mode) {
    if (IsWithoutProgress)
        return;
    if (!is_null(ob) && mode == 1) {
        ob.addClass("inprogress");
        selected_control = ob;
    }
    else if (!is_null(selected_control)) {
        selected_control.removeClass("inprogress");
        selected_control = null;
    }
}

function $SetFocus(ob) {}

var flash_timer = null;

function $HideFlash() {
    if (!is_null(flash_timer)) {
        clearTimeout(flash_timer);
        flash_timer = null;
    }

    $("#page_flash_section")
        .addClass('hidden');
}

function $AddFlash(message, css, timeout, callback) {
    if (is_empty(message))
        return;

    if (is_empty(css))
        css = 'flash';

    var container = $("#page_flash_section");

    container.html('');
    container.append('<div class="'+css+'">'+message+'</div>');
    container.removeClass('hidden');

    if (is_empty(timeout))
        return;

    if (timeout > 0)
        flash_timer = setTimeout(function() { $HideFlash(); callback(); }, timeout);
}

function $ResetSearch(deactivate) {
    //
    // Set Search icon and clean search context box
    //
    if (deactivate)
        $_deactivate_search();

    var search = $("#search-context");

    if (search.val()) {
        var src = $SCRIPT_ROOT+'/static/img/';

        if (is_search_activated) {
            $("#search-icon")
                .attr('title', keywords['Cancel search'])
                .attr('src', src+'db-close.png');
        } else {
            $("#search-icon")
                .attr('title', keywords['Search'])
                .attr('src', src+'db-search.png');
            search.val('');
        }
    }
}

function $HideLogPage() {
    var ob = SelectedGetItem(SUBLINE, 'ob');
    
    if (IsLog)
        console.log('$HideLogPage:'+is_null(ob));
    
    if (!is_null(ob))
        $onToggleSelectedClass(SUBLINE, ob, 'remove', null);
}

function $ShowLogPage() {
    var ob = SelectedGetItem(SUBLINE, 'ob');

    if (IsLog)
        console.log('$ShowLogPage:'+is_null(ob));
    
    if (!is_null(ob))
        $onToggleSelectedClass(SUBLINE, ob, 'add', null);

    if (is_scroll_top) {
        $(window).scrollTop(0);
        is_scroll_top = false;
    }
}

function $ResetLogPage() {
    $("#command").each(function() { $(this).val(''); });
}

function $Go(action) {
    if (IsLog) {
        console.log('$Go.action', action);
    }
    $web_logging(action);
}

function $Handle(action, handler, params) {
    if (IsLog) {
        console.log('$Handle.action:', action, handler, params);
    }
    $web_logging(action, handler, params);
}

// =======================
// Event's Action Handlers
// =======================

function $onParentFormSubmit(id) {
    // -------------------------------------------
    // Submit of current selected form by given id XXX
    // -------------------------------------------
    var frm = $("#"+(id || 'filter-form'));
    var action = frm.attr('action');

    $SidebarControl.onBeforeSubmit();

    var is_run = 1;

    try { 
        is_run = performance.navigation.type == 0 ? 1 : 0; 
    }
    catch(err) {}

    if (IsDeepDebug)
        alert('$onParentFormSubmit.begin:'+id+':'+[is_run, action].join(':'));

    if (is_run)
        $("#OK", frm).val('run');

    var ob = $("#window_scroll", frm);
    var top = is_on_refresh ? page_scroll_top : $(window).scrollTop();

    if (is_exist(ob))
        ob.val(!no_window_scroll ? top : '');

    if (IsDeepDebug)
        alert('$onParentFormSubmit.end:'+frm.attr('id')+':'+ob.val()+':'+top);

    frm.submit();
}

function $onLineFormSubmit() {
    // ---------------------------------------------
    // Checks mode of submit: 0|1|2 - submit||loader
    // ---------------------------------------------
    if (IsLog)
        console.log('$onLineFormSubmit:'+default_submit_mode);

    switch (default_submit_mode) {
        case 0:
            $onParentFormSubmit();
            break;
        case 1:
        case 2:
            $Handle(default_action, default_handler, default_params);
            break;
    }
}

function $onPageLinkSubmit(link) {
    // --------------------------------
    // Submit by link. Changes location
    //  Note! window.location is not a string!!!
    // --------------------------------
    //alert('$onPageLinkSubmit.link:'+link);

    var x = link.split('?');
    var url = x[0];
    var qs = x.length > 1 ? strip(x[1]) : '';

    var sidebar = $_mobile() ? 0 : $SidebarControl.get_state();

    //url = url+'?'+(!is_empty(qs) ? qs+'&' : '')+'sidebar='+sidebar;

    url = url + makeLocation(qs, 'sidebar', sidebar);

    //alert('$onPageLinkSubmit.url:'+url);

    window.location.replace(url);
}

function $onToggleSelectedClass(key, ob, action, command, force) {
    // --------------------------------------
    // Set current selected HTML control item
    // --------------------------------------
    //      key     : type of control: LINE, SUBLINE, TABLINE, REFERENCE
    //      ob      : selected (a new) item HTML control
    //      action  : action to perform: submit|clear|add|remove
    //      command : command to submit
    //      force   : forced flag
    //
    // It used together with db.controller classes: $LineSelector, $SublineSelector.
    // On run `SelectedGetItem` function keeps current (selected before) item. 
    // Current item and his children has CSS `selected` class.
    // Action `submit` valid for LINE key only!

    var id = null;
    var tag = 'TR';
    if (is_exist(ob)) {
        id = $_get_item_id(ob);
        tag = ob[0].tagName;
    } else {
        id = SelectedGetItem(key, 'id');
    }

    var mask = ([LINE, SUBLINE, TABLINE, REFERENCE].indexOf(key) > -1 || tag == 'TR') ? 'td' : 'dd';
    var input = "input[name^='"+default_input_name+"']";

    if (IsLog)
        console.log('$onToggleSelectedClass:', key, 'id['+id+']', 'action:', action, 'mask:', mask, 'ob:', ob, tag);

    if (is_null(id))
        return;

    if (is_null(ob))
        ob = SelectedGetItem(key, 'ob');

    function make(ob, action, mode) {
        // Toggles `selected` class and updates `default_input_name` inputs 
        // with the given control `id` for:
        //      key=LINE and mode=1
        // If ob == null, current item has not been selected before.

        if (is_null(ob))
            return;

        if (IsLog)
            console.log('$onToggleSelectedClass.make:'+action+':'+id);

        $(mask, ob).each(function() {
            if (IsLog)
                console.log('$onToggleSelectedClass', key, ob, action, $(this));
            // Check prop 'rowspan' for joined table columns
            if (IsOptionRowspan && ($(this).hasClass("noselected") || $(this).prop('rowspan') > 1))
                $.noop();
            else if (action == 'add') {
                $(this).addClass("selected");
                if (key == LINE && mode == 1)
                    $(input).each(function() { $(this).val(id); });
            }
            else {
                $(this).removeClass("selected");
            }
        });

        if (action == 'add') {
            ob.addClass("selected");
            SelectedSetItem(key, 'ob', ob);
        }
        else {
            ob.removeClass("selected");
            SelectedSetItem(key, 'ob', null);
        }
    }

    $("#command").val(!is_null(command) ? command : '');

    switch (action) {
        case 'submit':
            if (isWebServiceExecute || key != LINE)
                return;

            $(input).each(function() { $(this).val(id); });

            if (force) {
                $onParentFormSubmit();
                return;
            }

            if (default_submit_mode > 0) {
                make(SelectedGetItem(key, 'ob'), 'remove', 0);
                SelectedReset();
                make(ob, 'add', 0);
            }

            $onLineFormSubmit();
            break;
        case 'clean':
            $(input).each(function() { $(this).val(''); });
            SelectedSetItem(key, 'ob', null);
            break;
        default:
            make(ob, action, 1);
    }
}

function $setPaginationFormSubmit(page) {
    $("input[name='page']").each(function() { $(this).val(is_null(page) ? '1' : page.toString()); });
}

function $onOpenHelp() {
    // ---------------------------------
    // Handler for click Help (Shift-F1)
    // ---------------------------------
    $HelpDialog.open();
    return true;
}

function $onRefreshClick(command) {
    // ------------------------------------------
    // Handler for click Refresh main-menu button
    // ------------------------------------------
    $("#command").val(command || 'refresh');
    $onParentFormSubmit();
}

function $onResetClick() {
    // ----------------------------------------
    // Handler for click Reset main-menu button
    // ----------------------------------------
    $("#command").val('init-filter');

    var link = window.location.toString();
    var x = link.split('?');
    var url = x[0];
    var qs = x.length > 1 ? strip(x[1]) : '';

    var sidebar = $SidebarControl.get_state();

    //url = url+'?'+'sidebar='+sidebar;

    url = url + makeLocation('', 'sidebar', sidebar);

    //alert('$onPageLinkSubmit.url:'+url);

    $("form#init-form").attr('action', url);

    $onParentFormSubmit('init-form');
}

function $onExportClick() {
    // -----------------------------------------
    // Handler for click Export main-menu button
    // -----------------------------------------
    $("#command").val('export');
    $onParentFormSubmit();
}

function $onControlPanelClick(ob) {
    // ----------------------------------
    // Handler for manage main menu items
    // ----------------------------------
    if (isDropdownActive)
        return;

    var id = ob.attr('id');
    var dropdown = (
        id == "admin-panel-dropdown" ? $("#admin-panel") : (
        id == "services-dropdown" ? $("#services") : (
        id == "actions-dropdown" ? $("#actions") : null
        )));

    if (is_null(dropdown))
        return;
    var dropdown_id = dropdown.attr('id');
    //
    // Was another selected item open before?
    //
    var is_selected = !(is_null(selected_dropdown) || selected_dropdown[0].attr('id') == dropdown_id);

    isDropdownActive = true;

    if (is_selected)
        selected_dropdown[0].slideToggle('slow');

    dropdown.slideToggle('slow', function() {
        isDropdownActive = false;
    });

    //
    // Is selected item closed?
    //
    var is_closed = !is_null(selected_dropdown) && selected_dropdown[1] == dropdown_id;

    selected_dropdown = is_closed ? null : new Array(dropdown, dropdown_id);
}

// =======================
// Common Event Listeners
// =======================

if (IsHideContextMenu == 1 || IsHideContextMenu == 2) {
    if (document.addEventListener) {
        document.addEventListener('contextmenu', function(e) {
            //alert("You've tried to open context menu before"); //here you draw your own menu
            e.preventDefault();
        }, false);
}
if (IsHideContextMenu == 2) {
        document.attachEvent('oncontextmenu', function() {
            alert("You've tried to open context menu after");
            window.event.returnValue = false;
        });
    }
}

jQuery(function($) 
{
    $("li.dropdown").on('click', function(e) {
        //alert(IsNoDropdown+':0'); XXX
        cls ='open';
        if (!IsNoDropdown) {
            var ob = $(this);
            if (!ob.hasClass(cls))
                ob.addClass(cls);
            else
                ob.removeClass(cls);
        }
    });

    $("li.dropdown").on("mouseleave", function(e) {
        //alert(IsNoDropdown+':1'); XXX
        cls ='open';
        if (IsNoDropdown) {
            var ob = $(this);
            if (ob.hasClass(cls))
                ob.removeClass(cls);
        }
    });

    $("#sidebar-navigator").click(function(e) {
        var ob = $(this);
        if (is_null($SidebarDialog) || !$SidebarDialog.is_active) {
            $SidebarControl.onNavigatorClick(false);
        } else {
            $SidebarDialog.activate(ob);
        }
    });

    $("#sidebarFrame").on("mouseover", function(e) {
        //alert('over');
        $SidebarControl.onFrameMouseOver();
        e.stopPropagation();
    }).on("mouseout", function(e) {

        /*
        console.log(getObjectValueByKey(e.target, 'id'));
        console.log($(this).has(e.target).length);
        console.log(isIE, IsMSIE, isFirefox);
        */
        if ($_mobile() || $(this).has(e.target).length == 0) //!(isIE || IsMSIE || isFirefox) || 
            $SidebarControl.onFrameMouseOut();
        e.stopPropagation();
/*
    }).on("mouseleave", function(e) {

        //console.log(getObjectValueByKey(e.target, 'id'));
        //console.log($(this).has(e.target).length);
        //console.log(isIE, IsMSIE, isFirefox);

        //if ($_mobile() || $(this).has(e.target).length == 0) //!(isIE || IsMSIE || isFirefox) || 
        $SidebarControl.onFrameMouseOut();
        e.stopPropagation();
*/
    });

    $("#sidebarMobilePointer").click(function(e) {
        $SidebarControl.onFrameMouseOver();
    });

    $("#sidebarPointer").click(function(e) {
        $SidebarControl.onActivatePointer($(this));
        e.stopPropagation();
    });

    // ---------
    // Main Menu
    // ---------

    $("a.mainmenu").click(function(e) {
        //alert('mainmenu');
        var link = $(this).prop('href');
        var target = $(this).prop('target');

        if (is_empty(target)) {
            $onPageLinkSubmit(link, target);
            e.preventDefault();
            return false;
        }

        return true;
    });

    // -----------------
    // Top Command Panel
    // -----------------

    $("#refresh").click(function(e) {
        $onRefreshClick();
        e.preventDefault();
    });

    $("#init-filter").click(function(e) {
        $onResetClick();
        e.preventDefault();
    });

    $("#export").click(function(e) {
        $onExportClick();
        e.preventDefault();
    });

    $("#back").click(function(e) {
        window.location.replace(back || root);
        e.preventDefault();
    });

    $("#reload").click(function(e) {
        window.location.reload();
        e.preventDefault();
    });

    $("div[id^='history']", this).click(function(e) {
        var id = $(this).attr('id');
        if (id == 'history:forward')
            window.history.forward();
        else if (id == 'history:back') {
            if (window.history.length > 0) window.history.back();
        }
        else if (typeof history_callback === 'function')
            history_callback(id);
    });

    // ---------------------
    // Search context events
    // ---------------------

    function $onSearchSubmit(e) {
        var s = strip($("#search-context").val());

        $ResetLogPage();

        if (is_search_focused || is_null(e)) {
            search_context = s;
            $("#search-context").val(s);
            if (is_empty(s))
                $("input[id='reset_search']").each(function() { $(this).val('1'); });
            else
                $("input[id='searched']").each(function() { $(this).val(s); });
            $LineSelector.onFormSubmit();
            $setPaginationFormSubmit(1);
            $onParentFormSubmit('filter-form');
        }
    }

    $("#search-context").focusin(function(e) {
        is_search_focused = true;
    }).focusout(function(e) {
        is_search_focused = false;
    });

    $("#search-icon").click(function(e) {
        $onSearchSubmit(null);
        $onParentFormSubmit('filter-form');
    });

    $("#search-form").submit(function(e) {
        $onSearchSubmit(e);
    });

    // -------------------
    // Dropdown Containers
    // -------------------

    $(".dropdown-link").click(function(e) {
        $onControlPanelClick($(this));
        e.preventDefault();
    });

    $("#schedule-refresh").click(function(e) {
        $SidebarControl.onRefreshPointer($(this));
        e.preventDefault();
    });

    $("#schedule-close").click(function(e) {
        $SidebarControl.onActivatePointer($(this));
        e.preventDefault();
    });

    // ---------------
    // Activate window
    // ---------------

    $(window).focus(function() {
        if (is_on_refresh)
            return;

        page_scroll_top = $(window).scrollTop();

        if (typeof($_activate) === 'function' && $_activate(1)) {
            is_on_refresh = true;

            $HideError();
            $ShowPage(1);
            $onRefreshClick();
        }
        else
            $Semaphore.start(true);
    }).blur(function() {
        $Semaphore.stop(false);
    });

    // -------------
    // Resize window
    // -------------

    $(window).on("resize", function() {
        $SidebarControl.resize();
    });

    // ---------------
    // Navigator links
    // ---------------

    $("a.page").click(function(e) {
        var link = $(this).prop('href');
        $onPageLinkSubmit(link);
        e.preventDefault();
        return false;
    });

    // ---------------
    // Keyboard Events
    // ---------------

    $(window).keydown(function(e) {
        var exit = false;

        //if (!e.shiftKey) alert(e.keyCode);

        if (e.keyCode==116) {                                    // F5 !!! IMPORTANT !e.ctrlKey && 
            $onRefreshClick();
            exit = true;
        }

        if (e.shiftKey && e.keyCode==112)                        // Shift-F1
            exit = $onOpenHelp();

        if ($ConfirmDialog.is_focused() || $NotificationDialog.is_focused() || page_is_focused(e) || isKeyboardDisabled)
            return;

        try {
            if ($BaseDialog.is_focused() || is_search_focused)
                return;
        } 
        catch (err) {
            alert('common exception: is_focused');
            return;
        }

        if (e.shiftKey && [67, 79].indexOf(e.keyCode) > -1) {    // Shift-C,Shift-O
            if (!is_null($SidebarDialog) && $SidebarDialog.is_active) {
                if (IsSidebarEnabled)
                    $SidebarControl.onNavigatorClick(false);
                exit = true;
            } else return;
        }

        else if (e.shiftKey && e.keyCode==82) {                  // Shift-R
            $onResetClick();
            exit = true;
        }

        else if (e.shiftKey && e.keyCode==83) {                  // Shift-S
            var focused = $("#search-context");
            $SidebarControl.onFrameMouseOver(focused);
            focused.focus();
            exit = true;
        }

        else if (e.shiftKey && e.keyCode==77) {                  // Shift-M
            var container = $("#messages_container");
            if (is_exist(container))
                container.toggleClass('hidden');
            exit = true;
        }

        else if (e.ctrlKey || e.shiftKey) {
            if (isWebServiceExecute)
                return;
            /*
            if (e.keyCode > 0)
                alert(e.ctrlKey+':'+e.keyCode);

            else if (e.keyCode==13)                             // Ctrl-Enter
            */

            // -----------------------
            // Tabline Selector moving
            // -----------------------

            if (e.keyCode==38)                                  // Ctrl-Up
                exit = $LineSelector.up();
            else if (e.keyCode==40)                             // Ctrl-Down
                exit = $LineSelector.down();
            else if (e.ctrlKey && e.keyCode==36)                // Ctrl-Home
                exit = $LineSelector.home();
            else if (e.shiftKey && e.keyCode==33)               // Shift-PgUp
                exit = $LineSelector.pgup();
            else if (e.shiftKey && e.keyCode==34)               // Shift-PgDown
                exit = $LineSelector.pgdown();
            else if (e.ctrlKey && e.keyCode==35)                // Ctrl-End
                exit = $LineSelector.end();

            // -------------
            // Tab Switching
            // -------------

            else if (e.shiftKey && e.keyCode==9)                // Shift-Tab
                exit = $TabSelector.tab() || true;
            else if (e.ctrlKey && e.keyCode==37)                // Ctrl-Left
                exit = $TabSelector.left();
            else if (e.ctrlKey && e.keyCode==39)                // Ctrl-Right
                exit = $TabSelector.right();
            /*
            else if (e.shiftKey && e.keyCode==37)               // Shift-Left
                exit = $MenuSelector.left();
            else if (e.shiftKey && e.keyCode==39)               // Shift-Right
                exit = $MenuSelector.right();
            */
        }

        else if (e.altKey) {
            if (isWebServiceExecute)
                return;
            /*
            if (e.keyCode > 0)
                alert(e.altKey+':'+e.keyCode);
            */

            var before = true;

            // -------------------
            // Before move handler
            // -------------------

            if (typeof keyboard_alt_before === 'function')
                before = keyboard_alt_before(e.keyCode);

            if (before) {
                if (e.keyCode==38)                              // Alt-Up
                    exit = $ActiveSelector.up();
                else if (e.keyCode==40)                         // Alt-Down
                    exit = $ActiveSelector.down();
                else if ([33, 36].indexOf(e.keyCode) > -1)      // Alt-Home:Alt-PgUp
                    exit = $ActiveSelector.home();
                else if ([34, 35].indexOf(e.keyCode) > -1)      // Alt-End:Alt-PgDown
                    exit = $ActiveSelector.end();
            }
            else
                exit = true;

            // ------------------
            // After move handler
            // ------------------

            if (typeof keyboard_alt_after === 'function' && before)
                keyboard_alt_after(e.keyCode);
        }

        if (exit) {
            e.preventDefault();
            return false;
        }
    });
});

// ============
// WEB-SERVICES
// ============

function $web_semaphore(action) {
/***
 *  Sidebar Semaphore Control handler.
 */
    if (isWebServiceExecute || !$Semaphore.isEnabled())
        return;

    if (IsLog)
        console.log('web_semaphore:', action);

    $Semaphore.running();

    var args = {
        'action'   : action,
        'template' : $Semaphore.template,
        'lid'      : $Semaphore.lid,
    };

    //alert(args.lid);

    $.post($SCRIPT_ROOT + '/semaphore/loader', args, function(x) {
        var state = x['state'];

        $Semaphore.refresh(state);

    }, 'json')
    .fail(function() {

        $Semaphore.error();

    })
    .always(function() {

    });
}
