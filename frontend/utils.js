

let formatCurrency = function(cents) {
    if (cents == 0) {
        return "$0";
    }
    var value = cents / 100;
    var num = '$' + value.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    return num.replace(/\.00$/,'');
}

let utils = {
    formatCurrency,
}


export default utils;
