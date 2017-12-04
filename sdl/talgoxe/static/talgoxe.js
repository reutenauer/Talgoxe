$(document).ready(function() {
    lastId = $('.addRow').last().id
    console.log(lastId);
    counter = Number(lastId.replace('button-', ''))
    console.log(lastId);
    console.log(counter);

    function addRow(event) {
        console.log(event.currentTarget.id);
        dpos = event.currentTarget.id.replace('button-', '');
        counter++
        newRowId = counter
        console.log("Adding a row after d.pos " + dpos + " ...");
        $('#data-' + dpos).after('<li id="data-' + newRowId + '"><input type="text" size="3" name="type-' + newRowId + '"> <input type="text" size="16" name="value-' + newRowId + '"> <button class="addRow" id="button-' + newRowId + '"><strong>+</strong></button></li>');
        buttonId = '#button-' + newRowId;
        console.log("Registering the event on id " + buttonId);
        $(buttonId).click(function(ev) { ev.preventDefault(); addRow(ev); });
    }

    function submitOrder() {
        $('.addRow').each(function(event, data) {
            console.log(data.id);
        });
    }

    $('.addRow').click(function(event) {
        event.preventDefault();
        addRow(event);
    });

    $('.nosubmit').on('keydown', function(event) {
        if (event.originalEvent.key == 'Enter') event.preventDefault();
        /* TODO Något med piltangenter? */
    });

    $('#spara').click(submitOrder);
});
