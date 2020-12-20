var allow_submit = true;
var p_error = document.querySelectorAll("#errors")[0];

function lengthCheck() {
    allow_submit = input.getAttribute("value").length < 5;
    if (!allow_submit) {
        p_error.innerHTML = "Comment too long!"
    } else {
        p_error.innerHTML = "Allow submit."
    }
}

var input = document.querySelectorAll("input")[0];
input.addEventListener("change", lengthCheck);

var form = document.querySelectorAll("form")[0];
form.addEventListener("submit", function(e) {
    if (!allow_submit) {
        e.preventDefault();
        p_error.innerHTML = "Failed to submit the fort: comment too long"
    }
});