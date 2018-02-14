var searchString = "";

$(document).ready(function() {
    lastId = $('.addRow').last()[0].id;
    console.log(lastId);
    counter = Number(lastId.replace('add-row-', ''))

    /*
    $(".ordlistelement").each(function(i, element) {
        $(element).parent().hide();
    });
    */

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
        removeButtonId = '#remove-row-' + counter;
        $(removeButtonId).click(function(ev) { ev.preventDefault(); console.log('Trying to remove ' + ev.currentTarget.id); $(ev.currentTarget).parent().remove() });
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

    $('#spara').click(submitOrder);

    $('#sok-artikel').on('keyup', function(event) {
	newSearchString = $(event.currentTarget)[0].value;
	console.log(newSearchString);
        if (newSearchString != searchString) searchArticles(newSearchString);
        searchString = newSearchString;
    });

    function searchArticles(string) {
        console.log("Got search string: " + string);
        $(".ordlistelement").each(function(i, childElement) {
            element = $(childElement).parent();
        });
    }
});
