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
        // console.log(scripts[i].handle)
    };
    Node.prototype.getAttribute = function(attr) {
        return call_python("getAttribute", this.handle, attr);
    }
    function Node(handle) { this.handle = handle; }


} catch(e) {
    console.log(e.stack);
    throw e;
}
