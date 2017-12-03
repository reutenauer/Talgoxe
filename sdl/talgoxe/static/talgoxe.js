$(document).ready(function() {
    function addRow(event) {
        console.log("Adding a row ...");
        console.log($);
        console.log($.id);
        console.log($.attr('id'));
        /* console.log($.id()); */
        console.log(event);
        console.log(this.id);
        console.log(this);
        console.log(event.currentTarget);
        console.log(event.currentTarget.id);
        console.log(event.currentTarget.id.replace('button-', ''));
    }

    $('.addRow').click(function(event) {
        event.preventDefault();
        addRow(event);
    });
});
