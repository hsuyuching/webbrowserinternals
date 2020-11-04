try {
    console = { log: function(x) { call_python("log", x); } }
    document = { querySelectorAll: function(s) {
        return call_python("querySelectorAll", s);
    }}
    console.log("haha")
    console.log(document.querySelectorAll("p").length)
} catch(e) {
    console.log(e.stack);
    throw e;
}
