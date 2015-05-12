
var expanders = {};

function expand(name) {
	var expanded;
	if (name in expanders) {
		expanded = expanders[name];
	} else {
		expanded = false;
	}

	expanded = !expanded;

	var inner = document.getElementById("inner-" + name);
	var control = document.getElementById("control-" + name);

	if (expanded) {
		inner.style.display = "block";
		control.innerHTML = "&#x25bc;";
	} else {
		inner.style.display = "none";
		control.innerHTML = "&#x25ba;";
	}

	expanders[name] = expanded;
}
