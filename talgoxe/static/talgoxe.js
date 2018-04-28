var searchString = "";

$(document).ready(function() {
    if ($('.addRow').length > 0) {
        lastId = $('.addRow').last()[0].id;
        console.log(lastId);
        counter = Number(lastId.replace('add-row-', ''))
    } else {
        counter = 0;
    }

    function addRow(event) {
        console.log(event.currentTarget.id);
        dpos = event.currentTarget.id.replace('add-row-', '');
        counter++
        newRowId = counter
        console.log("Adding a row after d.pos " + dpos + " with counter " + counter + " ...");
        $('#data-' + dpos).after('<li id="data-' + counter + '"><input type="text" size="3" name="type-' + counter + '" id="type-' + counter + '" class="d-type"> <textarea rows="1" style="width: 55%" name="value-' + counter + '" id="value-' + counter + '" class="d-value" /> <button class="addRow" id="add-row-' + counter + '" tabindex="-1"><strong>+</strong></button> <button class="removeRow" id="remove-row-' + counter + '" tabindex="-1"><strong>-</strong></button><button class="moveRowUp" id="row-up-' + counter + '" tabindex="-1"><strong>↑</strong></button><button class="moveRowDown" id="row-down-' + counter + '" tabindex="-1"><strong>↓</strong></button></li>');
        buttonId = '#add-row-' + counter;
        console.log("Registering the event on id " + buttonId);
        $(buttonId).click(function(ev) { ev.preventDefault(); addRow(ev); });
        removeButtonId = '#remove-row-' + counter;
        $(removeButtonId).click(function(ev) { ev.preventDefault(); removeRow(ev); });
        $('.d-type').change(function(event) { checkType(event); });
        $('.d-value').change(function(event) { checkValue(event); });
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
        event.preventDefault();
        removeRow(event);
    });

    function removeRow(event) {
        console.log("Trying to remove a row ...");
        if (confirm("Är du säker?")) {
            $(event.currentTarget).parent().remove();
        }
    }

    $('.moveRowUp').click(function(event) {
        console.log("Hej, här är jag.");
        event.preventDefault();
        moveUp($(event.currentTarget).parent());
    });

    $('.moveRowDown').click(function(event) {
        event.preventDefault();
        moveDown($(event.currentTarget).parent());
    });

    function moveUp(element) {
        prev = element.prev();
        prev.first().before(element.first());
    }

    function moveDown(element) {
        // id = element[0].id.replace('data-', '');
        next = element.next();
        next.first().after(element.first());
    }

    $('.d-type').change(function(event) { checkType(event); });

    /* TODO Hämsta listor (typer och landskap) från någon ändepunkt på servern */
    types = [
        'srt', 'sov', 'fo', 'vk', 'vb', 'ssv', 'vr', 'ok', 'ust', 'm1',
        'm2', 'g', 'gp', 'be', 'rbe', 'us', 'sp', 'ssg', 'hr', 'foa',
        'm3', 'm0', 'vh', 'hh', 'okt', 'pcp', 'öv', 'hv', 'övp', 'ref',
        'int', 'obj', 'ip', 'ko', 'kl', 'nyr', 'ti', 'dsp', 'vs', 'gt',
        'gtp', 'bea', 'äv', 'ävk', 'fot', 'tip', 'tik', 'flv', 'lhv', 'gö',
        'göp'
    ];

    function checkType(event) {
        type = $(event.currentTarget)[0].value.trim().toLowerCase();
        if ($.inArray(type, types) >= 0) {
            $(event.currentTarget).removeClass("red");
        } else {
            $(event.currentTarget).addClass("red");
        }
    }

    $('.d-value').change(function(event) { checkValue(event); }); // TODO Klura ut varför .focusout har precis samma effekt (avfyras inte om ingen ändring)

    landskap = {
        'sk' : 'skåne', 'bl' : 'blek', 'öl' : 'öland', 'sm' : 'smål', 'ha' : 'hall',
        'vg' : 'västg', 'bo' : 'boh', 'dsl' : 'dalsl', 'gl' : 'gotl', 'ög' : 'östg',
        'götal' : 'götal', 'sdm' : 'sörml', 'nk' : 'närke', 'vrm' : 'värml', 'ul' : 'uppl',
        'vstm' : 'västm', 'dal' : 'dal', 'sveal' : 'sveal', 'gst' : 'gästr', 'hsl' : 'häls',
        'hrj' : 'härj' , 'mp' : 'med', 'jl' : 'jämtl', 'åm' : 'ång', 'vb' : 'västb',
        'lpl' : 'lappl', 'nb' : 'norrb', 'norrl' : 'norrl'
    };
    longLandskap = [];
    for (key in landskap) { longLandskap.push(landskap[key]); }

    function checkValue(event) {
        value = $(event.currentTarget);
        valueValue = value[0].value.trim().toLowerCase();
        row = value.parent();
        type = row.children()[0].value.trim().toLowerCase();
        if (type == 'g') {
            if (valueValue in landskap) {
                value[0].value = landskap[valueValue];
                value.removeClass("red");
            } else if ($.inArray(valueValue, longLandskap) >= 0) {
            /* if (['häls', 'västb'].includes(valueValue)) { */
                value.removeClass("red");
            } else {
                value.addClass("red");
            }
        }
    }

    $('#spara').click(submitOrder);

    $('#sok-artikel').on('keyup', function(event) {
        newSearchString = $(event.currentTarget)[0].value;
        console.log(newSearchString);
        if (newSearchString != searchString) {
            searchingFeedback = $('#searching-feedback');
            searchingFeedback.show();
            searchingFeedback.html('Letar efter ' + newSearchString + '...');
            searchArticles(newSearchString);
            searchingFeedback.html('');
            searchingFeedback.hide();
        }
        searchString = newSearchString;
    });

    $('#sok-artikel-button').click(function() {
        searchArticles($("#sok-artikel")[0].value);
    });

    function searchArticles(string) {
        console.log("Got search string: " + string);
        if (string == "") {
            hideEverything();
            return;
        }

        regexp = new RegExp('^' + string);
        $(".ordlistelement").each(function(i, childElement) {
            element = $(childElement).parent();
            if ($(childElement).html().match(regexp)) element.show();
            else element.hide();
        });
    }

    function hideEverything() {
        $(".ordlistelement").each(function(i, childElement) {
            $(childElement).parent().hide();
        });
    }

    $('.träff .träffelement').click(function(event) { showArticle($(event.currentTarget).parent()) });
    $('.virgin').click(function(event) { fetchArticle(event.currentTarget); });

    function showArticle(element) {
        console.log(element);
        var artId = element[0].id.replace(/^lemma-/, 'artikel-');
        article = $('#' + artId);
        if (article.hasClass("hidden")) {
            article.removeClass("hidden");
            element.children().first().html('▾');
            $(element.children()[1]).hide();
            article.show();
            element.children().last().show();
        } else {
            article.addClass("hidden");
            element.children().first().html('▸');
            $(element.children()[1]).show();
            article.hide();
            element.children().last().hide();
        }
    }

    function fetchArticle(element) {
        var artId = element.id.replace(/^lemma-/, '');
        var artUrl = window.location.href.replace(/\/search.*$/, '/artikel/');
        $.get(artUrl + artId).done(function(data) {
            $('#artikel-' + artId).html(data);
            $(element).off("click");
            $(element).removeClass("virgin");
        });
    }

    $('#skapa-pdf').click(function(event) { createPDF(event.currentTarget); });

    function createPDF(element) {
        articles = [];
        $('input').each(function(i, article) {
            articles.push(article.value.replace(/^article-/, ''));
        });
        console.log("Article IDs:");
        console.log(articles);
        $.get(window.location.href + '/pdf?ids=' + new String(articles)).done(function(data) {
            console.log("GET completed!  Data:");
            console.log(data);
        });
    }
});
