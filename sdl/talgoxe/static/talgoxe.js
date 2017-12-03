$(document).ready(function() {
    names = {
    }

    function addRow(event) {
        console.log(event.currentTarget.id);
        dpos = event.currentTarget.id.replace('button-', '');
        if (!names[dpos]) { names[dpos] = 0 }
        newRowId = dpos + '.' + names[dpos]
        names[dpos]++
        console.log("Adding a row after d.pos " + dpos + " ...");
        $('#data-' + dpos).after('<li id="data-' + newRowId + '"><input type="text" size="3" name="type-' + newRowId + '"> <input type="text" size="16" name="value-' + newRowId + '"> <button class="addRow" id="button-' + newRowId + '"><strong>+</strong></button></li>');
        console.log("Registering the event");
        $('#button-' + newRowId).click(function(event) { event.preventDefault(); addRow(event); });
    }

    $('.addRow').click(function(event) {
        event.preventDefault();
        addRow(event);
    });
});
