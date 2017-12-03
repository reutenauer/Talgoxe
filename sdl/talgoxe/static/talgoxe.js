$(document).ready(function() {
function addRow(data) {
    console.log("Adding a row ...");
    console.log($);
    console.log($.id);
    console.log($.attr('id'));
    /* console.log($.id()); */
    console.log(data);
}

$('.addRow').click(function(data) {
    console.log('foo');
    addRow(data);
});

$('button').click(function() {
    console.log("Hello, World!");
});

$('submit').click(function() {
  console.log('Submit was clicked.');
});
});
