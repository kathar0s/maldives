function setComma(value) {
	value = value.toString();
	value = parseFloat(value.replace(/\,/g,""));
	var reg = /(^[+-]?\d+)(\d{3})/;
	var n = (value + '');
	while (reg.test(n)) n = n.replace(reg,'$1' + ',' + '$2');

	return n;
}