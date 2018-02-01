$(document).ready(function() {
    lastId = $('.addRow').last()[0].id;
    console.log(lastId);
    counter = Number(lastId.replace('add-row-', ''))

    function addRow(event) {
        console.log(event.currentTarget.id);
        dpos = event.currentTarget.id.replace('add-row-', '');
        counter++
        newRowId = counter
        console.log("Adding a row after d.pos " + dpos + " with counter " + counter + " ...");
        $('#data-' + dpos).after('<li id="data-' + counter + '"><input type="text" size="3" name="type-' + counter + '" id="type-' + counter + '"> <textarea rows="1" cols="16" name="value-' + counter + '" id="value-' + counter + '" /> <button class="addRow" id="add-row-' + counter + '" tabindex="-1"><strong>+</strong></button> <button class="removeRow" id="remove-row-' + counter + '" tabindex="-1"><strong>-</strong></button></li>');
        buttonId = '#add-row-' + counter;
        console.log("Registering the event on id " + buttonId);
        $(buttonId).click(function(ev) { ev.preventDefault(); addRow(ev); });
        // Inte .keyDown!
        $('#type-' + counter).on('keydown', function(eve) { keyDown(eve); });
        removeButtonId = '#remove-row-' + counter;
        $(removeButtonId).click(function(ev) { ev.preventDefault(); console.log('Trying to remove ' + ev.currentTarget.id); $(ev.currentTarget).parent().remove() });
        $('#value-' + counter).on('keydown', function(event) { keyDown(event); });
    }

    function keyDown(event) {
        console.log("key pressed");
        console.log(event.originalEvent.key);
        console.log($(event.currentTarget).parent());
        if (event.originalEvent.key == 'Enter') event.preventDefault();
        /* TODO Något med piltangenter? */
        if (event.originalEvent.key == 'ArrowDown') {
            id = Number((event.currentTarget.id).replace(/(value|type)-/, ''));
            console.log(id);
            selector = '#value-' + String((id + 1));
            console.log("Selector is " + selector);
            $(selector).focus();
        }
    }

    function submitOrder(event) {
        ids = [];
        $('.addRow').each(function(event, data) {
            ids.push(data.id.replace('add-row-', ''));
            console.log(data.id.replace('add-row-', ''));
        });
        console.log(ids.join());
        $('#spara').after('<input type="hidden" name="order" value="' + ids.join() + '">');
    }

    $('.addRow').click(function(event) {
        event.preventDefault();
        addRow(event);
    });

    $('.removeRow').click(function(event) {
        console.log("Trying to remove a row ...");
        event.preventDefault();
        $(event.currentTarget).parent().remove();
    });

    $('.nosubmit').on('keydown', function(event) {
        keyDown(event);
    });

    $('#spara').click(submitOrder);

    $('#sok-artikel').on('keyup', function(event) {
	string = event.originalEvent.key
	console.log(string);
    });
});
