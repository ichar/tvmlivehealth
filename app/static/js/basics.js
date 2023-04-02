// ***************************
// BASICS HTML CONTROL CLASSES
// ---------------------------
// Version: 1.00
// Date: 06-04-2021

// ---------------
// Basics Controls
// ---------------

var $ListItemSideControl = {
    container           : null,
    id                  : null,

    // ==========================================================
    // List Item Side Control with Insert/Remove buttons:<accord>
    // ==========================================================

    IsDebug : 0, IsTrace : 0, IsLog : 0,

    check_all           : null,
    left_panel          : null,
    right_panel         : null,
    button_include      : null,
    button_exclude      : null,

    selected            : null,

    selected_left_item  : null,
    selected_right_item : null,

    items               : new Object(),
    left_side           : null,
    right_side          : null,

    init: function(id, container) {
        this.id = id;
        this.container = container || $("#"+this.id+"-control");

        if (this.IsTrace)
            alert('init');

        this.check_all = $("#"+this.id+"check-all", this.container);
        this.left_panel = $("#"+this.id+"-left", this.container);
        this.right_panel = $("#"+this.id+"-right", this.container);
        this.button_include = $("#"+this.id+"-include", this.container);
        this.button_exclude = $("#"+this.id+"-exclude", this.container);

        this.items = new Object();

        this.left_side = $("ul", this.left_panel);
        this.right_side = $("ul", this.right_panel);

        this.selected = this._get_selected(null);

        if (this.IsLog)
            console.log('$ListItemSideControl.init:'+this.selected, 'container:'+this.container);

        this.reset();
    },

    term: function() {
        this.items = null;
    },

    _get_selected: function(ob) {
        //
        // Set and returns `selected` item as Object
        //
        if (is_null(ob)) {
            var ob = $("li[class~='selected']", this.container);
            if (is_null(ob))
                ob = $("li", this.container).first();
        }

        if (!is_exist(ob))
            return;

        var child = ob.children().first();
        var id = child.attr('id');
        var cid = id.split('_')[0];
        var container = $("#"+cid);
        var selected = {'ob':ob, 'child':child, 'id':id, 'cid':cid, 'container':container};

        if (!is_null(this.selected)) {
            this.selected['ob'].removeClass('selected');
            //this.selected['container'].hide();
        }
        
        ob.addClass('selected');
        container.show();

        if (this.IsLog)
            console.log('$ListItemSideControl._get_selected:', objectKeyValues(selected), 'id:'+id);

        return selected;
    },

    _insert_before: function(item, container) {
        //
        // Check `insert_before` position for given item inside of a side container
        // Returns item before which given one should be inserted
        //
        var data = item.attr('data').toLowerCase();
        var ob = null;

        if (this.IsDebug)
            alert(data);

        if (is_null(data))
            return null;

        container.children().each(function(index) {
            if (!is_null(ob))
                return;
            else if ($(this).attr('data').toLowerCase() > data)
                ob = $(this);
        });

        if (this.IsTrace)
            alert('$ListItemSideControl._insert_before:'+(ob != null ? ob.attr('data') : '...'));

        return ob;
    },

    _get_item: function(id, container) {
        //
        // Returns item with given id from a side container
        //
        var item = null;

        container.children().each(function(index) {
            if (item != null)
                return;
            else if ($(this).attr('id').split(DEFAULT_HTML_SPLITTER)[1] == id) {
                item = $(this);
            }
        });

        return item;
    },

    reset: function() {
        //
        // Reset side containers: moves all items from right to left side
        // Attr this.items: list of items form right side (selected)
        //
        var self = this;

        if (this.IsTrace)
            alert('$ListItemSideControl.reset');

        this.right_side.children().each(function(index) {
            var item = $(this);
            var insert_before = self._insert_before(item, self.left_side);

            if (insert_before != null)
                item.insertBefore(insert_before);
            else
                self.left_side.append(item);
        });

        this.items = new Object();
    },

    click: function(ob) {
        var id = ob.attr('id');
        var parent = ob.parent();
        this.selected = this._get_selected(parent);
    },

    activate: function(checked) {
        if (this.IsTrace)
            alert('$ListItemSideControl.activate');

        if (checked) {
            this.left_panel.addClass('disabled');
            this.button_include.addClass('disabled');
            this.button_exclude.addClass('disabled');
            this.right_panel.addClass('disabled');
        } else {
            this.left_panel.removeClass('disabled');
            this.button_include.removeClass('disabled');
            this.button_exclude.removeClass('disabled');
            this.right_panel.removeClass('disabled');
        }

        this.check_all.prop('checked', checked);
    },

    update: function(data) {
        if (is_null(data))
            return;

        if (this.IsTrace)
            alert('$ListItemSideControl.update');

        var rows = data.split(DEFAULT_HTML_SPLITTER);

        if (this.IsLog)
            console.log('$ListItemSideControl.update:', rows);

        for (var i=0; i < rows.length; i++) {
            var id = rows[i];
            var item = this._get_item(id, this.left_side);
            
            if (is_null(item))
                continue;

            var insert_before = this._insert_before(item, this.right_side);

            if (insert_before != null)
                item.insertBefore(insert_before);
            else
                this.right_side.append(item);

            this.items[id] = 1;
        }

        this.check_all.prop('checked', rows.length > 0 ? 0 : 1);
        this.activate(rows.length > 0 ? false : true);
    },

    setLeft: function(ob, force) {
        if (!force && this.selected_left_item != null)
            this.selected_left_item.removeClass('selected');
       
        ob.addClass('selected');
        this.selected_left_item = ob;
    },

    setRight: function(ob, force) {
        if (!force && this.selected_right_item != null)
            this.selected_right_item.removeClass('selected');
        
        ob.addClass('selected');
        this.selected_right_item = ob;
    },

    getItems: function() {
        var ids = new Array();
        for (var id in this.items) {
            if (this.items[id] == 1)
                ids[ids.length] = id;
        }
        return ids;
    },

    onInsertItem: function(ob) {
        var item = this.selected_left_item;
        var container = this.right_side;

        if (this.IsTrace)
            alert(left.prop('tagName')+':'+right.prop('tagName'));

        var insert_before = this._insert_before(item, container);

        if (insert_before != null)
            item.insertBefore(insert_before);
        else
            container.append(item);

        item.removeClass('selected');

        var id = item.attr('id').split(DEFAULT_HTML_SPLITTER)[1];
        this.items[id] = 1;

        $setUserFormSubmit(0);

        this.selected_right_item = null;
        var ob = this._insert_before(item, this.left_side);
        if (ob == null)
            return;

        this.setLeft(ob, true);
    },

    onRemoveItem: function(ob) {
        var item = this.selected_right_item;
        var container = this.left_side;

        if (this.IsTrace)
            alert(left.prop('tagName')+':'+right.prop('tagName'));

        var insert_before = this._insert_before(item, container);

        if (insert_before != null)
            item.insertBefore(insert_before);
        else
            container.append(item);

        item.removeClass('selected');

        var id = item.attr('id').split(DEFAULT_HTML_SPLITTER)[1];
        this.items[id] = 0;

        $setUserFormSubmit(0);

        this.selected_left_item = null;
        var ob = this._insert_before(item, this.right_side);
        if (ob == null)
            return;

        this.setRight(ob, true);
    }
};
