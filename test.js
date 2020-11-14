inputs = document.querySelectorAll('input')
for (var i = 0; i < inputs.length; i++) {
    var name = inputs[i].getAttribute("name");
    var value = inputs[i].getAttribute("value");
    console.log(name + ": "+ value);
    if (value.length > 100) {
        console.log("Input " + name + " has too much text.")
    }
}
