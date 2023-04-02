﻿// *******************************
// APPLICATION PAGE CONTROLS MANAGER
// -------------------------------
// Version: 1.80
// Date: 21-12-2019

// =================================
// Common Page Controls declarations
// =================================

var $SidebarDialog = null;

var $Semaphore = {
    container    : null,

    IsTrace : 0, IsLog : 0,

    settings     : {
        'colors' : ['#0000ff', '#ff00ff', '#ffff00', '#ffa800', '#00ffff', '#00ff00', '#ff0000'],
        'background_color' : 'rgba(180, 180, 200, 0.1)',
        'default_class' : 'semaphore-default-item',
        'max_duration' : 10000,
    },

    template     : '',          // Kind of Semaphore Handle
    lid          : '',          // Handle LogID[OrderID:BatchID] to check state
    count        : 0,           // Number of indicators
    timeout      : 0,           // Timeout to windeow.setInterval
    action       : '',          // Handle action code
    speed        : [200, 600],  // Speed to animate indicators (on/off)
    items        : null,        // Semaphore indicator items (item objects list, this.item)

    index        : null,        // Index of interrupt mode

    is_active    : false,       // Initilized & ready to start, timeout is valid
    is_enabled   : false,       // Semaphore is active and Sidebar control is active & shown on the screen
    is_running   : false,       // Handle Web Servive is running
    is_focused   : true,        // Window is focused or not

    init: function(state) {
        if (state.length == 0) 
            return;

        this.updateState(state);

        if (this.IsLog)
            console.log('$Semaphore.init');
    },

    initState: function(template) {
        this.template = template;
    },

    reset: function(force) {
        this.items = new Array();

        for (i=0; i < this.count; i++) {
            if (force)
                this.items.push(this.item());

            var item = $("#semaphore-"+i.toString());
            if (!is_null(item)) {
                if (force)
                    item.removeClass(this.settings.default_class);
                else
                    item.addClass(this.settings.default_class);
            }
        }
    },

    updateState: function(state) {
        var x = state.split('::');
        var self = this;

        this.template = x[0];

        if (x.length > 1)
            this.lid = x[1] || '0:0';
        if (x.length > 2)
            this.count = parseInt(x[2]) || this.count || 7;
        if (x.length > 3)
            this.timeout = parseInt(x[3]) || this.timeout || 1000;
        if (x.length > 4)
            this.action = x[4] || this.action || '901';

        if (x.length > 5)
            x[5].split(':').forEach(function(s,i) { self.speed[i] = parseInt(s); });

        this.is_active = this.timeout > 0 ? true : false;

        if (this.IsTrace)
            alert(this.template+':'+this.lid+':'+this.count+':'+this.timeout+':'+this.action+':'+this.speed);
    },

    item: function() {
        return {'value':0, 'duration':0};
    },

    repr_item: function(i) {
        return this.items[i].value + ':' + this.items[i].duration;
    },

    dump: function() {
        var s = [];
        var self = this;

        if (is_null(this.items))
            return '';

        this.items.forEach(function(x, i) { s.push(self.repr_item(i)); });
        return s.join(',');
    },

    isEnabled: function() {
        this.is_enabled = $SidebarControl.isEnabled();
        return this.is_active & this.is_enabled & !this.is_running & this.is_focused;
    },

    toggleState: function() {
        if (this.isEnabled())
            this.start();
        else
            this.stop();
    },

    start: function(focused) {
        if (this.IsLog)
            console.log('$Semaphore.start:'+this.index);

        // ---------------
        // Start semaphore
        // ---------------

        if (focused === true)
            this.is_focused = true;

        this.reset(1);

        interrupt(true, 9, $Semaphore.timeout, null, this.index, 1);
    },

    run: function(index) {
        this.index = index;
        
        if (!this.isEnabled()) {
            if (!this.is_running)
                this.stop();
            return;
        }

        if (this.IsLog)
            console.log('$Semaphore.run:'+this.index);

        $web_semaphore(this.action);
    },

    stop: function(focused) {
        if (this.IsLog)
            console.log('$Semaphore.stop:'+this.index, 'running:'+this.is_running, 'focused:'+this.is_focused);

        // --------------
        // Stop semaphore
        // --------------

        if (focused === false)
            this.is_focused = false;

        this.reset(0);

        interrupt(false, 0, 0, null, this.index, 1);
    },

    error: function() {
        this.stop();
        this.is_running = false;
    },

    running: function() {
        this.is_running = true;
    },

    refresh: function(ob) {
        this.is_running = false;

        if(is_null(ob))
            return;

        var state = ob['state'];
        var items = ob['items'];

        this.updateState(state);

        for (i=0; i < this.count; i++) {
            if (items.length == i)
                break;
            this.items[i] = items[i];
        }

        if (this.IsTrace)
            alert(this.dump());

        if (this.IsLog)
            console.log('$Semaphore.refresh:'+this.dump());

        this.show();
    },

    show: function() {
        var self = this;
        var is_exist;

        do {
            is_exist = false;
            for (i=0; i < this.count; i++) {
                if (this.items[i].value > 0) {
                    var item = $("#semaphore-"+i.toString());

                    if (is_null(item))
                        continue;

                    var activate = this.speed[0];
                    var deactivate = this.items[i].duration || this.speed[1];

                    if (deactivate > 0 && deactivate < this.settings.max_duration) 
                        item.animate({backgroundColor:self.settings.colors[i]}, activate, function(){})
                            .animate({backgroundColor:self.settings.background_color}, deactivate);
                    else
                        item.animate({backgroundColor:self.settings.colors[i]}, activate);

                    this.items[i].value -= 1;
                    is_exist = true;
                }
            }
        } while(is_exist);
    }
};

var $SidebarControl = {
    container     : {'sidebar' : null, 'data' : null, 'panel' : null, 'navigator' : null, 'semaphore' : null, 'pointer' : null, 'mobile_pointer' : null},
    height        : {'sidebar' : 0, 'scroller' : 0},

    IsDebug : 0, IsTrace : 0, IsLog : 0,

    timeout       : 600,
    timer         : null,

    mobile_pointer_active : 1,
    
    default_position : {  // Should be the same as in common.html styles
        'margin_left' : ["50px", "422px"], 'height_offset' : 10, 'min_offset' : 28, 'filter_width' : 398
    },
    default_count : 4,

    state         : 0,    // Sidebar state: 0/1 - collapsed/expanded
    data_margin   : 0,
    speed         : 600,
    is_active     : false,
    is_shown      : false,
    is_out        : false,
    is_run        : false,
    is_mobile     : false,
    animated      : 0,

    callback      : null,
    filter        : [],

    done_action   : null,

    pointer_timer : null,
    pointer_show  : -2,

    init: function(callback, filter, with_pointer) {
        this.callback = callback;
        this.filter = filter;

        this.container.sidebar = $("#sidebarFrame");
        this.container.data = $("#dataFrame");
        this.container.panel = $("#sidebar-content");
        this.container.navigator = $("#sidebar-navigator");
        this.container.semaphore = $("#semaphore");
        this.container.pointer = $("#sidebarPointer");
        this.container.mobile_pointer = $("#sidebarMobilePointer");

        this.state = parseInt($("#sidebar").val() || 0); // XXX 

        if (IsDeepDebug){
            alert('$SidebarControl.state:'+this.state);
        }

        this.is_mobile = $_mobile();

        this.pointer_show = with_pointer ? -1 : -2;

        this.initState();

        this.onBeforeStart();
    },

    initState: function() {
        var mode = 'available'; // this.is_mobile ? 'screen-max' : 'screen-min';
        var width_offset = (this.is_mobile ? 10 : this.default_position.min_offset);
        var sidebar_height = $_height(mode);

        this.height.sidebar = sidebar_height;

        if (is_null(this.container.sidebar))
            return;

        if (this.IsDebug)
            alert('H:'+joinToPrint(
                [$_height('screen-max'), $_height('screen-min'), $_height('max'), $_height('min'), $_height('available')]));

        this.showPointer(0);

        if (this.state == 1 || this.is_shown) {
            this.container.sidebar.css("min-height", $_get_css_size(sidebar_height));

            var scroller = $("#sidebar-filter-scroller");

            if (is_exist(scroller)) {
                var height_offset = scroller.position().top;
                var height = $("#filter-form").height() + 20;

                var kw = this.is_mobile ? Math.max(
                        Math.ceil(($_width('max') / design_settings.dialog.body_default_width) * 10) / 10, 
                        //design_settings.dialog.window_ratio, 
                        //1.4, 
                        1
                    ) : 1;

                //alert(kw);

                var scroller_height = int((sidebar_height - height_offset - this.default_position.height_offset) * kw);
                /*
                if (this.IsDebug)
                    alert(joinToPrint([$("#html-container").width(), $_width('max'), kw, design_settings.dialog.window_ratio, scroller_height]));

                if (this.IsLog)
                    console.log('$SidebarControl.initState:', 
                        this.height.sidebar, this.container.sidebar.height(), $_height('available'), height, scroller_height);

                if (this.IsDebug)
                    alert(joinToPrint([this.height.sidebar, $_height('available'), height, scroller_height]));
                */
                scroller.css("height", $_get_css_size(scroller_height));

                var padding_right = scroller_height < height ? width_offset : 0;
                var w = this.default_position.filter_width - padding_right;

                if (this.IsLog)
                    console.log('$SidebarControl.width:', this.height.sidebar, this.container.sidebar.height(), height, scroller_height);

                this.filter.forEach(function(id) {
                    var ob = $("#"+id);
                    if (is_exist(ob)) {
                        var x = $_get_css_size(w);
                        ob.css({"width" : x, "max-width" : x});
                    }
                });

                // XXX
                //scroller.css({"width" : $_get_css_size(w), "padding-right" : $_get_css_size(padding_right)}); 
                scroller.css({"padding-right" : $_get_css_size(padding_right)}); 
            }
        }

        var selection = $("#selected-batches");
        var parent = $("#line-table");
        var button = $("#CARDS_ACTIVATION");
        var box = $("#cards-selection-box");

        if (!is_exist(selection) || !is_exist(parent) || !is_exist(button) || !is_exist(box))
            return;

        box.css("width", button.width()+34);
        selection.css("height", parent.height()-38).css("width", button.width()+34); // height()-43
    },

    get_state: function() {
        return this.state.toString();
    },

    getMargin: function() {
        return this.default_position.margin_left[this.state];
    },

    checkShown: function() {
        this.is_shown = this.state == 1 ? true : false;

        // --------------------
        // Parent page callback
        // --------------------

        if (typeof this.callback === 'function')
            this.callback();

        // -------------------------
        // Toggle state of semaphore
        // -------------------------

        $Semaphore.toggleState();
    },

    isEnabled: function() {
        return this.is_active & this.is_shown & this.state;
    },

    isShown: function() {
        return (this.state == 1 || this.is_shown) ? true : false;
    },

    isDueAnimated: function() {
        return (this.animated > 0 && this.animated < this.default_count) ? true : false;
    },

    showPointer: function(mode) {
        /****
         *  Show Sidebar Pointer, mode:
         *     -2 - pointer is not used
         *     -1 - free and ready
         *      0 - init
         *      1 - animation started
         *      2 - animation finished
         *      3 - animation may be broken
         ****/
        if (!is_exist(this.container.pointer) || this.pointer_show == -2)
            return;

        var timeout = 100;

        if (mode == 3) {
            if (this.pointer_show != -1)
                this.pointer_show = this.state == 1 || this.is_shown ? 0 : 1;
            return;
        }
        
        if (mode == 0) {
            var top = this.height.sidebar - 84;
            this.container.pointer.css({"top" : $_get_css_size(top)});
            if (this.mobile_pointer_active) {
                var height = int((top - this.container.mobile_pointer.position().top - 4) / 2);
                this.container.mobile_pointer.css({"height" : $_get_css_size(height)});
            }
            this.pointer_show = this.state == 1 || this.is_shown ? 0 : 1;
        }
        else if (mode == 1) {
            this.pointer_show = 0;
            timeout = 10;
        }
        else if (this.state == 1 || this.is_shown)
            this.pointer_show = 0;
        else
            this.pointer_show = 1;

        if (!is_null(this.pointer_timer))
            return;

        if (this.IsLog)
            console.log('$SidebarControl.showPointer:, mode:', mode, this.pointer_show, this.state, this.is_shown);

        var self = $SidebarControl;

        this.pointer_timer = setTimeout(function() { 
            clearTimeout(self.pointer_timer);

            if (self.pointer_show)
                self.container.pointer.show(400); 
            else
                self.container.pointer.hide();

            if (self.mobile_pointer_active) {
                if (self.pointer_show)
                    self.container.mobile_pointer.show();
                else
                    self.container.mobile_pointer.hide();
            }

            self.pointer_timer = null;
            self.pointer_show = -1;
        }, timeout);
    },

    begin: function() {
        if (this.is_shown) {
            this.container.sidebar.addClass("sidebar-shadow");
        }
    },

    done: function() {
        var is_finished = this.isDueAnimated() ? false : true;

        if (is_finished) {
            if (!this.is_shown)
                this.container.sidebar.removeClass("sidebar-shadow");
            else
                this.initState();

            this.showPointer(2);
        }

        if (!is_null(this.done_action)) {
            if (this.IsDebug)
                alert('$SidebarControl.done:'+this.done_action['ob']+'::'+joinToPrint([this.state, this.is_shown, this.animated, this.default_count]));

            if (this.done_action['force'] || is_finished) {
                this.done_action['callback'](this.done_action['ob']);
                //$SidebarDialog.done(this.done_action['ob']);
                this.done_action = null;
            }
        }
    },

    toggleFrame: function(force) {
        if (this.IsLog)
            console.log('$SidebarControl.toggleFrame, state:', this.state);

        if (this.isDueAnimated() || is_null(this.container.semaphore))
            return;

        if (!is_null(this.timer)) {
            clearTimeout(this.timer);
            this.timer = null;
        }

        var self = $SidebarControl;

        this.animated = 1;

        if (!force || (this.state == 1 && !this.is_shown) || (this.state == 0 && this.is_shown)) {
            this.container.semaphore
                .animate({ width:'toggle' }, this.speed, function() {}).promise().done(function() {
                    ++self.animated;
                    self.done();
                });

            this.container.panel
                .animate({ width:'toggle' }, this.speed, function() {}).promise().done(function() {
                    ++self.animated;
                    self.done();
                });

            this.container.navigator.toggleClass("sidebar-rotate");
        } else
            this.animated += 2;

        if (force)
            this.container.data
                .animate({ marginLeft:this.getMargin() }, this.speed, function() {}).promise().done(function() {
                    self.initState();
                    ++self.animated;
                    self.done();
                });
        else
            this.animated += 1;

        if (this.IsLog)
            console.log('$SidebarControl.toggleFrame, shown:', this.animated, this.state, !this.is_shown);

        this.onToggle();
    },

    setBodyEnable: function(mode) {
        if (this.is_mobile || !IsActiveScroller)
            return;

        if (mode == 0)
            $("html, body").css({ overflow:"" });
        else if (mode == 1)
            $("html, body").css({ overflow:"hidden" });
    },

    onActivatePointer: function(ob) {
        if (!is_null($SidebarDialog) && !this.isShown()) {
            alert('$SidebarControl.onActivatePointer.1');
            $SidebarDialog.activate(ob);
        } else if (!is_null(this.done_action)) {
            alert('$SidebarControl.onActivatePointer.2');
            this.done_action.callback(this.done_action.force, {'callback':$SidebarControl.onActivatePointer, 'ob':ob});
        }
    },

    onRefreshPointer: function(ob) {
        if (!is_null($SidebarDialog))
            $SidebarDialog.update();
    },

    onBeforeStart: function() {
        setTimeout(function() { $SidebarControl.show(); }, 200);
    },

    onBeforeSubmit: function() {
        var state = this.state;
        $("input[name='sidebar']").each(function() { $(this).val(state.toString()); });

        if (this.is_shown && this.state == 0) {
            this.speed = 400;
            this.onFrameMouseOut();
        }

        if (typeof sidebar_submit === 'function')
            sidebar_submit();
    },

    onFrameMouseOver: function(focused) {
        if (this.IsLog)
            console.log('$SidebarControl.onFrameMouseOver, state:', this.state, this.is_shown, this.animated);

        this.is_out = false;

        // Don't hide pointer before sidebar will be activated
        //this.showPointer(1);

        this.setBodyEnable(1);

        if (!this.is_active || this.is_shown || this.state == 1 || this.isDueAnimated())
            return;

        if (!is_null(this.timer))
            return;

        var self = $SidebarControl;

        this.timer = setTimeout(function() {
            clearTimeout(self.timer);
            self.timer = null;

            if (self.is_out)
                return;

            // Hide pointer here after sidebar has been activated
            self.showPointer(1);

            self.toggleFrame(0);

            self.is_shown = true;

            self.begin();

            if (!is_null(focused))
                focused.focus();

        }, this.timeout);
    },

    onFrameMouseOut: function() {
        if (this.IsLog)
            console.log('$SidebarControl.onFrameMouseOut, state:', this.state, this.is_shown, this.animated);

        this.is_out = true;

        this.showPointer(3);

        this.setBodyEnable(0);

        if (!this.is_active || !this.is_shown || this.state == 1 || this.isDueAnimated())
            return;

        if (!is_null(this.timer))
            return;

        var self = $SidebarControl;

        this.timer = setTimeout(function() {
            clearTimeout(self.timer);
            self.timer = null;

            if (!self.is_out)
                return;

            self.toggleFrame(0);

            self.is_shown = false;

        }, this.timeout);
    },

    onToggle: function() {
        if (typeof sidebar_toggle === 'function')
            sidebar_toggle();
    },

    onNavigatorClick: function(force, done_action) {
        if (!IsSidebarEnabled) {
            return;
        }

        this.done_action = done_action;

        if (this.is_run || this.isDueAnimated() || is_null(this.container.sidebar))
            return;

        if (force) {
            if (this.state == 0)
                this.container.navigator.toggleClass("sidebar-rotate");
            return;
        }

        this.is_run = true;

        this.state ^= 1;

        if (this.state)
            this.showPointer(1);
        else
            this.setBodyEnable(0);

        this.toggleFrame(1);

        this.container.sidebar.removeClass("sidebar-shadow");

        this.checkShown();

        this.is_run = false;
    },

    submit: function(frm) {
        this.onBeforeSubmit();
        frm.submit();
    },

    resize: function() {
        this.initState();

        if (this.state == 1 || this.is_shown)
            return;

        if (!is_null($SidebarDialog))
            $SidebarDialog.resize();
    },

    hide: function() {
        if (this.state == 1)
            this.onNavigatorClick(false);
    },

    show: function() {
        this.is_active = true;
        this.checkShown();
    }
};

var $BaseDialog = {
    container : null,
    id        : null,
    opened    : false,
    focused   : false,

    init: function(id, container) {
        this.id = id;
        this.container = container || $("#"+this.id+"-confirm-container");
    },

    callback: function() {
        return this.container;
    },

    is_focused: function() {
        return (this.focused && !is_null(this.callback())) ? true : false;
    },

    submit: function() {
        $onParentFormSubmit(this.id+"-form");
    },

    activate: function() {
        this.container.dialog("open");
        this.focused = true;
    },

    open: function(id, container) {
        this.init(id, container);

        this.opened = true;

        this.container.dialog("option", "position", {my:"center center", at:"center center", of:window, collision:"none"});

        this.activate();
    },

    onClose: function() {
        this.opened = false;
        this.focused = false;
    },

    confirmed: function() {
        this.close();
        this.submit();
    },

    cancel: function() {
        this.close();
    },

    deactivate: function() {
        this.container.dialog("close");
        this.focused = false;
    },

    close: function() {
        this.deactivate();
        this.onClose();
    },

    run: function(id) {
        this.init(id);
        this.onClose();
        
        this.submit();
    }
};

var $BaseScreenDialog = {
    parent       : null,

    container    : null,
    box          : null,
    form         : null,
    ob           : null,
    cache        : null,

    // =================
    // Base Screen Class
    // =================

    IsDebug : 0, IsTrace : 0, IsLog : 0,

    // Timeout to open a window
    timeout      : 300,
    timer        : null,
    
    id           : null,
    cacheid      : '',
    activated    : false,

    // Screen size params
    ssp          : null,
    // Screen available offset
    offset       : {'H' : [0, 0, 0], 'W' : [0, 0, 0], 'init' : [0, 0]},
    // Flag: this is mobile frame
    is_mobile    : null,
    // Windows scroll top before lock_scroll
    scroll_top   : 0,

    init: function(ob, id, parent) {
        this.ob = ob;
        this.id = id;
        this.parent = parent;

        this.container = this.parent.container || $("#"+this.id+"-confirm-container");
        this.box = this.parent.box || $("#"+this.id+"-box");
        this.form = this.parent.form || $("#"+this.id+"-form");

        this.initState();
    },

    initState: function() {
        this.is_mobile = $_mobile();

        active_dialog = this.container;

        this.ssp = {'H' : {'available':0, 'container':0, 'content':0, 'box':0}, 'W' : {'available':0, 'container':0, 'content':0, 'box':0}};

        this.cache = $("#dialog-cache");
        this.cacheid = ['__', this.id, '-view-content'].join('');

        //this.IsTrace = this.is_mobile ? 1 : 0;

        this.timer = null;
    },

    term: function() {
        this.parent.unlock_scroll();

        $InProgress(null);

        active_dialog = null;

        this.container = null;
        this.box = null;
        this.form = null;
        this.ob = null;
        this.cache = null;

        this.activated = false;

        this.id = '';
        this.scroll_top = 0;
    },

    lock_scroll: function() {
        this.scroll_top = $(window).scrollTop();
        $("html, body").css({ overflow:"hidden" });
    },

    unlock_scroll: function() {
        $("html, body").css({ overflow:"" });
        $(window).scrollTop(this.scroll_top);
    },

    check_screen: function() {
        if (this.IsDebug) {
            var ss = '<h3>Screen:'
                + 'H:'+[
            verge.viewportH(), 
            window.screen.height, 
            window.screen.availHeight, 
            document.body.clientHeight, 
            document.documentElement.clientHeight
                ].join(':') + ' *** '
                + 'W:'+[
            verge.viewportW(),
            window.screen.width, 
            window.screen.availWidth, 
            document.body.clientWidth, 
            document.documentElement.clientWidth
                ].join(':') + 
                '</h3>';

            var hs = '<div class="p50"><h3>setDefaultSize:'
                + 'H:'+[$_height('screen-max'), $_height('screen-min'), $_height('max'), $_height('min'), $_height('available'), $_height('client')].join(':') + '</h3>'
                + '<table class="param-screen">'
                + '<tr><td>container: </td><td>' + this.ssp['H']['container'] + '</td></tr>'
                + '<tr><td>content:   </td><td>' + this.ssp['H']['content']   + '</td></tr>'
                + '<tr><td>box: </td><td>' + this.ssp['H']['box'] + '</td></tr>'
                + '<tr><td>init offset: </td><td>' + this.offset['init'][0] + '</td></tr>'
                + '<tr><td>available: </td><td>' + this.ssp['H']['available'] + '</td></tr>'
                + (is_exist(this.parent.container) ? '<tr><td>parent: </td><td>' + this.parent.container.parent().outerHeight() + '</td></tr>' : '')
                + '</table></div>';

            var ws = '<div class="p50"><h3>setDefaultSize:'
                + 'W:'+[$_width('screen-max'), $_width('screen-min'), $_width('max'), $_width('min'), $_width('available'), $_width('client')].join(':') + '</h3>'
                + '<table class="param-screen">'
                + '<tr><td>container: </td><td>' + this.ssp['W']['container'] + '</td></tr>'
                + '<tr><td>content:   </td><td>' + this.ssp['W']['content']   + '</td></tr>'
                + '<tr><td>box: </td><td>' + this.ssp['W']['box'] + '</td></tr>'
                + '<tr><td>init offset: </td><td>' + this.offset['init'][1] + '</td></tr>'
                + '<tr><td>available: </td><td>' + this.ssp['W']['available'] + '</td></tr>'
                + (is_exist(this.parent.container) ? '<tr><td>parent: </td><td>' + this.parent.container.parent().outerWidth() + '</td></tr>' : '')
                + '</table></div>';

            this.box.html('<div class="check-screen"><h2>mode:'+this.parent.mode+'(is'+(this.is_mobile ? ' ':' not ')+'mobile'+') '
                + 'window orientation:'+$_window_orientation() + '</h2>'
                + 'screen params:<br><div>' + ss + '</div><div class="inline">' + hs + ws + '</div></div>');
        }
    },

    reset: function(with_cache) {
        clearTimeout(this.timer);

        if (with_cache)
            this.box.html(this.cache.html().replace(/__/g, ''));

        this.cache.html('');
    },

    progress: function() {
        $InProgress(this.ob, 1);
    },

    load: function(html) {
        this.cache.html(html);
    },

    setDefaultSize: function(offset) {
        /****
         *  `offset` Object params:
         *      'H' -- Array: 
         *          0 - смещение по высоте (заголовок+подвал), 
         *          1 - доп.смещение (?), 
         *          2 - расчетная высота диалога
         *      'W' -- Array:
         *          0 - смещение по ширине (отсупы слева+справа), 
         *          1 - доп.смещение (?), 
         *          2 - расчетная ширина диалога
         *      'init' -- Array:
         *          0 - начальное приращение доступной части экрана по высоте
         *          1 - начальное приращение доступной части экрана по ширине
         ****/
        //alert('setDefaultSize');
        /*
        if (this.activated)
            return;
        */
        this.offset = offset;

        if (this.is_mobile) {
            this.offset['H'][0] += design_settings.dialog.offset_height;
            this.offset['H'][1] += design_settings.dialog.offset_height;
        }

        var content = $("#"+this.cacheid);
        var box = this.cache;

        if (this.IsLog)
            console.log('$BaseScreenDialog.setDefaultSize:', is_exist(box), box.attr('id'), 
                ['W', box.width(), box.outerWidth(), 'H', box.height(), box.outerHeight()].join(':'),
                ['W', content.width(), 'H', content.height()].join(':')
                );

        this.ssp['H']['content'] = box.height();
        this.ssp['W']['content'] = int(Math.max(content.width(), 800));

        this.parent.reset();

        var mode = this.parent.mode;

        this.ssp['H']['available'] = $_height(mode) + this.offset['init'][0];
        this.ssp['W']['available'] = $_width(mode) + this.offset['init'][1];

        var x = [];

        x.push(this.ssp['H']['available']);
        x.push(Math.max(this.offset['H'][2], this.ssp['H']['content'] + this.offset['H'].slice(0,1).sum()));

        if (this.is_mobile && $_window_portrait() && is_exist(this.parent.form) && this.parent.check_limit_height)
            x.push(design_settings.dialog.container_limit_height);

        this.ssp['H']['container'] = int(x.min());
        this.ssp['H']['box'] = this.ssp['H']['container'] - this.offset['H'][0];

        var height = $_get_css_size(this.ssp['H']['box']);

        this.box.css({"height" : height, "max-height" : height});

        if (this.IsLog)
            console.log('$BaseScreenDialog.setDefaultSize:', 'H:', this.box.outerHeight());
        
        var x = [];

        x.push(this.ssp['W']['available']);
        x.push(Math.max(this.offset['W'][2], this.ssp['W']['content'] + this.offset['W'].slice(0,1).sum()));

        this.ssp['W']['container'] = int(x.min());
        this.ssp['W']['box'] = this.ssp['W']['container'] - this.offset['W'][0];

        if (this.IsLog)
            console.log('$BaseScreenDialog.setDefaultSize:', 'W:', this.box.outerWidth());

        this.check_screen();

        this.container.dialog("option", "height", this.ssp['H']['container']);
        this.container.dialog("option", "width", this.ssp['W']['container']);

        this.parent.lock_scroll();

        if (this.IsTrace)
            alert('$BaseScreenDialog.setDefaultSize');

        this.activated = true;
    },

    width: function(mode){
        return this.ssp['W'][mode || 'container'];
    },

    height: function(mode){
        return this.ssp['H'][mode || 'container'];
    },

    handle: function(f) {
        this.timer = setTimeout(f, self.timeout);
    },

    onOpen: function() {
        if (is_null(this.parent))
            return;

        var mode = this.parent.mode;
        var parent = this.container.parent();

        if (this.IsLog)
            console.log('$BaseScreenDialog.onOpen parent:', parent);

        if (this.parent.is_active)
            return;

        var width = parent.outerWidth();
        var height = parent.outerHeight();
        var left = int(($_width(mode) - width) / 2);
        var top = 0;

        if (this.is_mobile && $_window_portrait() && is_exist(this.parent.form))
            top = design_settings.dialog.top;
        else
            top = int(($_height(mode) - height) / 2);

        parent.css({position: 'fixed', left: left, top: top});
    }
};

var $ConfirmDialog = {
    container : null,
    opened    : false,
    focused   : false,

    init: function() {
        this.container = $("#confirm-container");
    },

    is_focused: function() {
        return this.focused;
    },

    open: function(msg, width, height, title) {
        if (this.opened)
            return;

        this.init();

        this.opened = true;
        this.focused = true;

        this.setContent(msg);

        this.container.dialog("option", "title", !is_empty(title) ? title : keywords['Confirm notification form']);

        if (!is_empty(width))
            this.container.dialog("option", "width", width);
        if (!is_empty(height))
            this.container.dialog("option", "height", height);

        this.container.dialog("open");
    },

    onClose: function() {
        this.opened = false;
        this.focused = false;
    },

    setContent: function(msg) {
        var box = $("#confirm-info");
        var s = '<p>'+msg.replace(/{/g, '<').replace(/}/g, '>')+'</p>';

        isConfirmation = true;

        box.html(s);
    },

    cancel: function() {
        this.focused = false;
        this.close();
    },

    close: function() {
        isConfirmation = false;

        this.container.dialog("close");
        this.onClose();
    }
};

var $NotificationDialog = {
    container : null,

    opened    : false,
    focused   : false,

    init: function() {
        this.container = $("#notification-container");
    },

    is_focused: function() {
        return this.focused;
    },

    open: function(msg, width, height, title) {
        if (this.opened)
            return;

        this.init();

        this.opened = true;
        this.focused = true;

        this.setContent(msg);

        this.container.dialog("option", "title", !is_empty(title) ? title : keywords['Notification form']);

        if (!is_empty(width))
            this.container.dialog("option", "width", width);
        if (!is_empty(height))
            this.container.dialog("option", "height", height);

        this.container.dialog("open");
    },

    onClose: function() {
        this.opened = false;
        this.focused = false;
    },

    setContent: function(msg) {
        var box = $("#notification-info");
        var s = '<p>'+msg.replace(/{/g, '<').replace(/}/g, '>')+'</p>';

        isNotificationation = true;

        box.html(s);
    },

    cancel: function() {
        this.focused = false;
        this.close();
    },

    close: function() {
        isNotificationation = false;

        this.container.dialog("close");
        this.onClose();
    }
};

var $HelpDialog = {
    container : null,
    box       : null,
    context   : null,

    opened    : false,

    // Flag: this is mobile frame
    is_mobile    : null,
    // Mode of screen available
    mode         : '',

    init: function() {
        this.container = $("#help-container");
        this.box = $("#help-box");
        
        this.context = $CurrentContext();

        this.is_mobile = $IS_FRAME == 0;

        this.mode = this.is_mobile ? 'available' : 'min';
    },

    open: function() {
        if (this.opened)
            return;

        this.init();

        this.opened = true;

        this.confirmed();

        //this.container.dialog("option", "position", {my:"center center", at:"center center", of:"#dataFrame"});

        this.container.dialog("open");
    },

    onClose: function() {
        this.opened = false;
    },

    confirmed: function() {
        var info = $("#help-info");
        var height_container = 0; // 22 for item

        var s = '<p class="group">'+'Общие команды интерфейса'+':</p>'+
                //'<div><dt class="keycode">Shift-F1</dt><dd class="spliter">:</dd><p class="text">'+'Данная справка'+'</p></div>'+
                '<div><dt class="keycode">Shift-O | C</dt><dd class="spliter">:</dd><p class="text">'+'Развернуть/свернуть панель меню'+'</p></div>'+
                '<div><dt class="keycode">F5</dt><dd class="spliter">:</dd><p class="text">'+'Команда "Обновить страницу"'+'</p></div>'+
                '<div><dt class="keycode">Ctrl-F5</dt><dd class="spliter">:</dd><p class="text">'+'Команда "Обновить интерфейс (перезагрузка)"'+'</p></div>'+
                '<div><dt class="keycode">Shift-R</dt><dd class="spliter">:</dd><p class="text">'+'Сбросить фильтр'+'</p></div>'+
                '<div><dt class="keycode">Shift-S</dt><dd class="spliter">:</dd><p class="text">'+'Контекстный поиск'+'</p></div>' +
                '<p class="group">'+'Журнал (события, сообщения)'+':</p>'+
                '<div><dt class="keycode">Ctrl | Shift-Up|Down</dt><dd class="spliter">:</dd><p class="text">'+'назад/вперед на одну строку'+'</p></div>'+
                //'<div><dt class="keycode">Ctrl/Shift-Down</dt><dd class="spliter">:</dd><p class="text">'+'вперед на одну строку'+'</p></div>'+
                '<div><dt class="keycode">Ctrl-Home | End</dt><dd class="spliter">:</dd><p class="text">'+'к первой/последней странице'+'</p></div>'+
                //'<div><dt class="keycode">Ctrl-End</dt><dd class="spliter">:</dd><p class="text">'+'к последней странице'+'</p></div>'+
                '<div><dt class="keycode">Shift-PgUp | PgDown</dt><dd class="spliter">:</dd><p class="text">'+'к предыдущей/следующей странице'+'</p></div>'+
                //'<div><dt class="keycode">Shift-PgDown</dt><dd class="spliter">:</dd><p class="text">'+'к следующей странице'+'</p></div>'+
                '<p class="group">'+'ИнфоМеню (вкладки)'+':</p>'+
                '<div><dt class="keycode">Shift-Tab</dt><dd class="spliter">:</dd><p class="text">'+'к следующей вкладке (в цикле)'+'</p></div>'+
                '<div><dt class="keycode">Ctrl-Left | Right</dt><dd class="spliter">:</dd><p class="text">'+'к предыдущей/следующей вкладке'+'</p></div>' +
                '';
            
            height_container = 0;

        if (['admin'].indexOf(this.context) > -1) {
            s += 
                '<p class="group">'+'Функциональные команды'+':</p>'+
                '<div><dt class="keycode">Shift-M</dt><dd class="spliter">:</dd><p class="text">'+'Информационное письмо'+'</p></div>'+
                '';

            height_container = Math.min(560, $_height(this.mode) - 10);
        }

        info.html(s);

        if (height_container > 0) {
            this.box.css({ 'height' : $_get_css_size(height_container-162) });
            this.container.dialog("option", "height", height_container);
        }
    },

    cancel: function() {
        this.close();
    },

    close: function() {
        this.container.dialog("close");
        this.onClose();
    }
};

var $Images = {
    default_images : ['static/img/sky-dark.jpg', 'static/img/sky-light.jpg'],

    IsTrace : 0, IsLog : 0,

    init: function() {
        $onImagesPreload();
    },

    _get_src: function(item, i) {
        return root+item+('?i='+i)+(IsForcedRefresh ? "?"+new Date().getTime() : ''); // isIE
    },

    _on_load_images: function() {
        if ($Images.IsTrace)
            alert('$Images.on_load_images');

        $Images.init();
    },

    preload: function() {
        var items = [];

        for(var i=0; i < this.default_images.length; i++) {
            items.push(this._get_src(this.default_images[i], i));
        }

        if (IsShowLoader == 1)
            items.push(this._get_src('static/img/loader.gif'), 0);

        if (items.length > 0) {
            preloadImages(items, this._on_load_images);
            return;
        }

        this.init();
    }
};

// =======
// Dialogs
// =======

jQuery(function($) 
{
    // ---------------
    // Help form: <F1>
    // ---------------

    $("#help-container").dialog({
        autoOpen: false,
        width:560,
        height:600, /* 720 = 25 for one line */
        //position:0,
        buttons: [
            {text: keywords['OK'], click: function() { $HelpDialog.cancel(); }}
        ],
        modal: true,
        draggable: true,
        resizable: false,
        position: {my: "center center", at: "center center", of: window, collision: "none"},
        create: function (event, ui) {
            $(event.target).parent().css("position", "fixed");
        },
        close: function() {
            $HelpDialog.onClose();
        }
    });

    // --------------------
    // Confirm form: Yes/No
    // --------------------

    $("#confirm-container").dialog({
        autoOpen: false,
        width:500,
        height:194,
        //position:0,
        buttons: [
            {text: keywords['Confirm'], click: function() { $Confirm(1, $(this)); }},
            {text: keywords['Reject'], click: function() { $Confirm(0, $(this)); }}
        ],
        modal: true,
        draggable: true,
        resizable: false,
        position: {my: "center center", at: "center center", of: window, collision: "none"},
        create: function (event, ui) {
            $(event.target).parent().css("position", "fixed");
        },
        close: function() {
            $ConfirmDialog.onClose();
        }
    });

    // ----------------------
    // Notification form: Yes
    // ----------------------

    $("#notification-container").dialog({
        autoOpen: false,
        width:400,
        //height:600,
        //position:0,
        buttons: [
            {text: keywords['OK'], click: function() { $Notification(1, $(this)); }},
        ],
        modal: true,
        draggable: true,
        resizable: false,
        position: {my: "center center", at: "center center", of: window, collision: "none"},
        create: function (event, ui) {
            $(event.target).parent().css("position", "fixed");
        },
        close: function() {
            $NotificationDialog.onClose();
        }
    });

    $("li.dropdown").click(function(e) {
        cls ='open';
        var ob = $(this);
        if (!ob.hasClass(cls))
            ob.addClass(cls);
        else
            ob.removeClass(cls);
    });
});

