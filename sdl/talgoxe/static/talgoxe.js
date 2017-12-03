$(document).ready(function() {
    function addRow(event) {
        console.log(event.currentTarget.id);
        dpos = event.currentTarget.id.replace('button-', '');
        console.log("Adding a row after d.pos" + dpos + " ...");
    }

    $('.addRow').click(function(event) {
        event.preventDefault();
        addRow(event);
    });
});
