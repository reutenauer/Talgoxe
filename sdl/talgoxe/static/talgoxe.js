$(document).ready(function() {
    lastId = $('.addRow').last()[0].id;
    console.log(lastId);
    counter = Number(lastId.replace('button-', ''))

    function addRow(event) {
        console.log(event.currentTarget.id);
        dpos = event.currentTarget.id.replace('button-', '');
        counter++
        newRowId = counter
        console.log("Adding a row after d.pos " + dpos + " with counter " + counter + " ...");
        $('#data-' + dpos).after('<li id="data-' + counter + '"><input type="text" size="3" name="type-' + counter + '"> <input type="text" size="16" name="value-' + counter + '"> <button class="addRow" id="button-' + counter + '"><strong>+</strong></button></li>');
        buttonId = '#button-' + counter;
        console.log("Registering the event on id " + buttonId);
        $(buttonId).click(function(ev) { ev.preventDefault(); addRow(ev); });
    }

    function submitOrder() {
        $('.addRow').each(function(event, data) {
            event.preventDefault();
            $('form').add('<input type="hidden" name="order" value="foo foo foo">');
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
