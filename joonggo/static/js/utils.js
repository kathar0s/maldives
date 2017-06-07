function setComma(value) {
	value = value.toString();
	value = parseFloat(value.replace(/\,/g,""));
	var reg = /(^[+-]?\d+)(\d{3})/;
	var n = (value + '');
	while (reg.test(n)) n = n.replace(reg,'$1' + ',' + '$2');

	return n;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
