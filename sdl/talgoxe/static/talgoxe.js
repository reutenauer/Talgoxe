function addRow(data) {
    console.log("Adding a row ...");
    console.log($);
    console.log($.id);
    console.log($.attr('id'));
    /* console.log($.id()); */
    console.log(data);
}

$('#button-*').each(function(data) {
    addRow(data);
});
