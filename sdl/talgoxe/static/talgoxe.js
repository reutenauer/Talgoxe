$(document).ready(function() {
    function addRow(data) {
        console.log("Adding a row ...");
        console.log($);
        console.log($.id);
        console.log($.attr('id'));
        /* console.log($.id()); */
        console.log(data);
        console.log(this.id);
        console.log(this);
    }

    $('.addRow').click(function(data) {
        addRow(data);
    });
});
