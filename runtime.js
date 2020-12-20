try {
    console = { 
        log: function(x) { call_python("log", x); 
        }
    }
    document = { querySelectorAll: function(s) {
        var handles = call_python("querySelectorAll", s)
        return handles.map(function(h) { return new Node(h) });
        }
    }
    scripts = document.querySelectorAll("script");
    for (var i = 0; i < scripts.length; i++) {
        console.log(call_python("getAttribute", scripts[i].handle, "src"));
    };
    LISTENERS = {}

    function Node(handle) { this.handle = handle; }

    function __runHandlers(handle, type) {
        var list = (LISTENERS[handle] && LISTENERS[handle][type]) || [];
        var evt = new Event(type);
        for (var i = 0; i < list.length; i++) {
            list[i].call(new Node(handle), evt);
        }
        return evt.do_default;
    }
    function Event(type) {
        this.type = type
        this.do_default = true;
    }
    
    Event.prototype.preventDefault = function() {
        this.do_default = false;
    }
    Node.prototype.getAttribute = function(attr) {
        return call_python("getAttribute", this.handle, attr);
    }

    Node.prototype.addEventListener = function(type, handler) {
        if (!LISTENERS[this.handle]) LISTENERS[this.handle] = {};
        var dict = LISTENERS[this.handle]
        if (!dict[type]) dict[type] = [];
        var list = dict[type];
        list.push(handler);
    }

    Object.defineProperty(Node.prototype, 'innerHTML', {
        set: function(s) {
            call_python("innerHTML", this.handle, "" + s);
        }
    });
    


} catch(e) {
    console.log(e.stack);
    throw e;
}
