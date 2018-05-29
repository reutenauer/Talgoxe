var lastLemma;

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
        $('#data-' + dpos).after('<li id="data-' + counter + '"><input type="text" size="3" name="type-' + counter + '" id="type-' + counter + '" class="d-type"><textarea rows="1" style="width: 55%" name="value-' + counter + '" id="value-' + counter + '" class="d-value" /><button class="addRow" id="add-row-' + counter + '" tabindex="-1"><strong>+</strong></button><button class="removeRow" id="remove-row-' + counter + '" tabindex="-1"><strong>-</strong></button><button class="moveRowUp" id="row-up-' + counter + '" tabindex="-1"><strong>↑</strong></button><button class="moveRowDown" id="row-down-' + counter + '" tabindex="-1"><strong>↓</strong></button><input type="submit" id="spara-och-ladda-om-' + counter + '" class="spara-och-ladda-om" value="💾" tabindex="-1" /></li>');
        buttonId = '#add-row-' + counter;
        console.log("Registering the event on id " + buttonId);
        $(buttonId).click(function(ev) { ev.preventDefault(); addRow(ev); });
        removeButtonId = '#remove-row-' + counter;
        $(removeButtonId).click(function(ev) { ev.preventDefault(); removeRow(ev); });
        $('#type-' + counter).change(function(event) { checkType(event); });
        $('#value-' + counter).change(function(event) { checkValue(event); });
        $('#spara-och-ladda-om-' + counter).click(function(event) { submitOrder(event); });
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
        var id = event.currentTarget.id.replace(/^remove-row-/, '')
        console.log("id is " + id);
        console.log($('#type-' + id)[0].value == '');
        console.log($('#value-' + id)[0].value == '');
        if ($('#type-' + id)[0].value.trim() == '' && $('#value-' + id)[0].value.trim() == '') $(event.currentTarget).parent().remove();
        else if (confirm("Är du säker?")) {
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

    $('.moveMomentUp').click(moveMomentUp);

    $('.moveMomentDown').click(moveMomentDown);

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

    /* TODO Check type before! Need to re-add textarea if changing from M1 or M2 to sth. else */
    function checkType(event) {
        type = $(event.currentTarget)[0].value.trim().toLowerCase();
        if (type == 'm1' || type == 'm2') {
          console.log("type = " + type);
          id2 = event.currentTarget.id.replace(/^type-/, '#value-');
          console.log("Looking for element with ID " + id2);
          element = $(id2);
          console.log("Target object:");
          console.log(element);
          element.hide();
          addAfter = $(event.currentTarget.id.replace(/^type-/, '#row-down-'));
          pos = event.currentTarget.id.replace(/^type-/, '');
          addAfter.after('<button class="moveMomentDown" id="moment-down-' + pos + '" tabindex="-1"><strong>⇓</strong></button>');
          addAfter.after('<button class="moveMomentUp" id="moment-up-' + pos + '" tabindex="-1"><strong>⇑</strong></button>');
        } else if ($.inArray(type, types) >= 0) {
            element = $(event.currentTarget.id.replace(/^type-/, '#moment-up-'));
            console.log("element?");
            if (element.attr("id")) {
              console.log("yes");
              console.log(element);
              console.log(element.attr("id"));
              element.remove();
              $(event.currentTarget.id.replace(/^type-/, '#moment-down-')).remove();
              $(event.currentTarget.id.replace(/^type-/, '#value-')).show();
              $('#moment-up-' + pos).click(moveMomentUp);
              $('#moment-down-' + pos).click(moveMomentDown);
            } else console.log("no");
            $(event.currentTarget).removeClass("red");
        } else {
            $(event.currentTarget).addClass("red");
        }
    }

    function moveMomentUp(event) {
        moveMoment(event, 'up');
    }

    function moveMomentDown(event) {
        moveMoment(event, 'down');
    }

    function moveMoment(event, dir) {
        event.preventDefault();
        element = $(event.currentTarget).parent();
        if (isM1(element)) {
            isRightMomentType = isM1;
        } else if (isM2(element)) {
            isRightMomentType = isM1OrM2;
        }
        /* TODO A separate function */
        moment = element.prev();
        ids = [];
        if (dir == 'up') {
            while (moment[0].id && !isRightMomentType(moment)) {
                // ids.push(moment[0].id);
                moment = moment.prev();
            }
            console.log(moment);
            console.log(moment.length);
            console.log(moment[0].id);
            console.log(ids);
            if (!moment[0].id) {
                alert("Cannot flytta momentet upp, det är det första i artikeln.");
                return;
            }
        }

        // ids.unshift(moment[0].id);
        nextMoment = element.next();
        var i = 1;
        while (nextMoment.length > 0 && nextMoment[0].id && !isRightMomentType(nextMoment)) {
            console.log(i);
            /*
            if (dir == 'up') ids.unshift(nextMoment[0].id);
            else ids.push(nextMoment[0].id);
            */
            ids.unshift(nextMoment[0].id);
            nextMoment = nextMoment.next();
            if (!nextMoment[0]) {
                if(dir == 'up') {
                    break;
                } else {
                    alert("Kan inte flytta momentet ner, det är det sista i artikeln.");
                    return;
                }
            }
            i++;
        }
        if (dir == 'down') {
            ids = []
            momentAfter = nextMoment.next();
            while (momentAfter.length > 0 && momentAfter[0].id && !isRightMomentType(momentAfter)) {
                ids.unshift(momentAfter[0].id);
                momentAfter = momentAfter.next();
                if (!momentAfter[0]) break;
            }
        }
        if (dir == 'up') ids.unshift(element[0].id);
        /* else ids.unshift(nextMoment[0].id); */
        // else ids.push(moment[0].id);
        /* else ids.push(element[0].id); */
        else {
            /* ids.unshift(element[0].id); */
            /* ids.push(momentAfter[0].id); */
            /* ids.push(moment.next()[0].id); */ // Samma som två rader högre!
            ids.push(element[0].id);
            ids.unshift(nextMoment[0].id);
        }
        console.log(nextMoment);
        console.log(ids);
        console.log("Moving stuff after:");
        console.log(moment);
        for (i in ids) {
            var id = ids[i];
            console.log(id);
            moment.after($('#' + id));
        }
    }

    function isM1(element) {
        return rowType(element) == 'M1';
    }

    function isM2(element) {
        return rowType(element) == 'M2';
    }

    function isM1OrM2(element) {
        return isM1(element) || isM2(element);
    }

    function rowType(row) {
        console.log(row);
        console.log(row.length);
        return $(row[0].id.replace(/^data-/, '#type-'))[0].value.trim();
    }

    /*
    function moveMomentDown(element) {
        console.log("Starting to move moment down.");
    }
    */

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
    $('.spara-och-ladda-om').click(submitOrder);

    $('#sok-artikel').on('keyup', searchArticles);

    function searchArticles() {
        string = this.value
        if (string == "") {
            hideEverything();
            return;
        }

        $('#sökstrang').html(string);
        regexp = new RegExp('^' + string);
        var nbhits = 0;
        $(".ordlistelement").each(function(i, childElement) {
            element = $(childElement).parent();
            if ($(childElement).html().replace(/.*<\/sup>\s*/, '').match(regexp)) { element.show(); nbhits++; }
            else element.hide();
        });
        if (nbhits == 0) $('#searching-feedback').show();
        else $('#searching-feedback').hide();
    }

    function hideEverything() {
        $(".ordlistelement").each(function(i, childElement) {
            $(childElement).parent().hide();
        });
    }

    $('.träff .träffelement').click(function(event) { toggleArticle($(event.currentTarget).parent()) });
    $('.virgin').click(function(event) { fetchArticle(event.currentTarget); });

    function showArticle(parent) {
        $(parent.children()[4]).removeClass("hidden");
        $(parent.children()[2]).html('▾');
        $(parent.children()[3]).hide();
        $(parent.children()[4]).show();
        parent.children().last().show();
    }

    function hideArticle(parent) {
        $(parent.children()[4]).addClass("hidden");
        $(parent.children()[2]).html('▸');
        $(parent.children()[3]).show();
        $(parent.children()[4]).hide();
        parent.children().last().hide();
    }

    function toggleArticle(element) {
        console.log(element);
        var artId = element[0].id.replace(/^lemma-/, 'artikel-');
        article = $('#' + artId);
        if (article.hasClass("hidden")) {
            showArticle(article.parent());
        } else {
            hideArticle(article.parent());
        }
    }

    function fetchArticle(element) {
        var artId = element.id.replace(/^lemma-/, '');
        var artUrl = window.location.href.replace(/\/talgoxe.*$/, '/talgoxe/artikel/');
        $.get(artUrl + artId).done(function(data) {
            $('#artikel-' + artId).html(data);
            $(element).off("click");
            $(element).removeClass("virgin");
        });
    }

    $('#visa-alla, #visa-alla-text').click(function() {
        if ($('#visa-alla-text').html() == "Visa alla") {

            $('.träff').each(function(i, lemma) {
                showArticle($(lemma));
            });

            $('.virgin').each(function(i, element) {
                fetchArticle(element);
            });

            $('#visa-alla').html('▾'); /* Inte ⚾! */
            $('#visa-alla-text').html('Dölja alla');
        } else {
            $('#visa-alla').html('▸');
            $('#visa-alla-text').html('Visa alla');

            $('.träff').each(function(i, lemma) {
                hideArticle($(lemma));
            });
        }
    });

    $('#skapa-pdf').click(function(event) { createPDF(event.currentTarget); });

    function createPDF(element) {
        console.log(element);
        $(element).html("Förbereder&nbsp;PDF...");
        articles = collectArticles();
        console.log("Article IDs:");
        console.log(articles);
        url = printableEndpoint('pdf', articles);
        console.log("Getting " + url);
        $.get(url).done(function(data) {
            console.log("GET completed!  Data:");
            console.log(data);
            $(element).off('click');
            $(element).attr("href", data.trim());
            $(element).html("Ladda&nbsp;ner&nbsp;PDF");
        });
    }

    function collectArticles() {
        articles = [];
        $('.träff').each(function(i, article) {
            articles.push(article.id.replace(/^lemma-/, ''));
        });

        console.log("Samlat in artiklar:");
        console.log(articles);
        return articles;
    }

    function printableEndpoint(format, articles) {
        return window.location.href.replace(/\/talgoxe.*/, '/talgoxe/print-on-demand') + '/' + format + '?ids=' + new String(articles);
    }

    $('#skapa-odf').click(function(event) { createODF(event.currentTarget); });

    function createODF(element) {
      $(element).html("Förbereder&nbsp;ODF...");
      articles = collectArticles();
      url = printableEndpoint('odf', articles);
      $.get(url).done(function(link) {
        $(element).off('click');
        $(element).attr("href", link.trim());
        $(element).html("Ladda&nbsp;ner&nbsp;ODF");
      });
    }

    $('.toselect').click(selectLemma);

    function selectLemma(event) {
        if (!lastLemma) lastLemma = $('#lemma-0');

        console.log(event.currentTarget);
        name = $(event.currentTarget).attr("name").replace(/^select/, 'selected');
        console.log(name);
        /* lemma = $('[name="' + name + '"]'); */
        /*
        lemma = $('#li-' + name);
        console.log(lemma);
        */
        var id = name.replace(/^selected-/, '');
        console.log(id);
        lemma = $($('[name="select-' + id + '"]').parent().children()[1]).html().trim();
        console.log(lemma);
        if ($(event.currentTarget).is(':checked')) {
            /* lemma.show(); */
            lastLemma.before('<li id="li-select-' + id + '" class="nobullet">' + lemma + ' <input type="checkbox" id="ta-bort-' + id + '" class="ta-bort" /> Ta bort <input type="hidden" name="selected-' + id + '" /></li>');
            tickBox = $('#ta-bort-' + id);
            tickBox.click(removeLemma);
            if (tickBox.is(':checked')) tickBox.click()
            /* lemma.after('<input type="hidden" name="selected-' + id + '" />'); */
        } else {
            $('#li-select-' + id).remove();
            /*
            lemma.hide();
            $('[name="selected-' + id + '"]').remove();
            */
        }
    }

    $(".ta-bort").click(removeLemma);

    function removeLemma(event) {
        console.log("Hej hej hej!");
        lemma = $(event.currentTarget).parent();
        var name = $(event.currentTarget).attr("name");
        if (name && name.match(/^selected-bokstav/)) {
            bokstav = name.replace(/^selected-bokstav-/, '');
            $('[name="selected-bokstav-' + bokstav + '"]').parent().remove();
            selector = '[name="bokstav-' + bokstav + '"]'
        } else  {
            var id = lemma.attr("id").replace(/^li-select-/, '');
            console.log(lemma);
            lemma.remove();
            $('[name="selected-' + id + '"]').remove();
            selector = '[name="select-' + id + '"]';
        }
        console.log(selector);
        lemmaLeft = $(selector);
        console.log(lemmaLeft);
        lemmaLeft.click();
    }

    $("#selectalla").click(selectAll);

    function selectAll(event) {
        event.preventDefault();
        $('[style="display: list-item;"]').each(function(i, element) {
            if (!element.id.match(/^li-selected-/)) {
                console.log($(element).children().first());
                var id = $(element).children().first().attr("name").replace(/^select-/, '')
                console.log(id);
                $('[name="select-' + id + '"]').each(function(i, element) {
                    if (!$(element).is(':checked')) $(element).click();
                });
                rightHandSide = $('#ta-bort-' + id);
                if (rightHandSide.is(':checked')) rightHandSide.click();
            }
        });
    }

    $('#ta-bort-alla').click(removeAll);

    function removeAll(event) {
        event.preventDefault();
        $('.ta-bort').each(function(i, element) {
            console.log(element);
            /* var id = $(element).attr("id").replace(/^ta-bort-/, ''); */
            $(element).click();
        });
    }

    $('.bokstav [type="checkbox"]').click(addBokstav);

    function addBokstav(event) {
        if (!lastLemma) lastLemma = $('#lemma-0');
        box = $(event.currentTarget);
        bokstav = box.attr("name").replace(/^bokstav-/, '');
        if (box.is(':checked')) {
            lastLemma.before('<li class="nobullet">' + bokstav + ' – hela bokstaven <input type="checkbox" name="selected-bokstav-' + bokstav + '" class="ta-bort" /> Ta bort</li>');
            removeBox = $('[name="selected-bokstav-' + bokstav + '"]');
            removeBox.click(removeLemma);
        } else {
            $('[name="selected-bokstav-' + bokstav + '"]').parent().remove();
        }
    }

    $('.bokstav .ta-bort').click(removeBokstav);

    function removeBokstav(event) {
        box = $(event.currentTarget);
        bokstav = box.attr("name").replace(/^selected-bokstav-/, '');
        $('[name="selected-bokstav-' + bokstav + '"]').parent().remove();
        $('[name="bokstav-' + bokstav + '"]').click();
    }

    $('#skapa-docx').click(createDOCX);

    function createDOCX(event) {
        element = $(event.currentTarget);
        element.html("Förbereder&nbsp;Word‑dokument...");
        articles = collectArticles();
        url = printableEndpoint('docx', articles);
        $.get(url).done(function(link) {
            element.off("click");
            element.attr("href", link.trim());
            element.html("Ladda&nbsp;ner&nbsp;Wordfilen");
        });
    }

    $('#omordna').click(omordna);

    function omordna() {
        console.log(this);
        if ($('.flytta-upp').hasClass("hidden")) {
            $('.flytta-upp, .flytta-ner, #spara-ordning').show();
            $('.flytta-upp, .flytta-ner, #spara-ordning').removeClass("hidden");
        } else {
            $('.flytta-upp, .flytta-ner, #spara-ordning').hide();
            $('.flytta-upp, .flytta-ner, #spara-ordning').addClass("hidden");
        }
    }

    $('.flytta-upp').click(flyttaUpp);

    function flyttaUpp(event) {
        event.preventDefault();
        rad = $(this).parent();
        upp = rad.prev();
        upp.before(rad);
    }

    $('.flytta-ner').click(flyttaNer);

    function flyttaNer(event) {
        event.preventDefault();
        rad = $(this).parent();
        ner = rad.next();
        ner.after(rad);
    }

    var radbytessymbol = '¶';

    $('.d-value').keydown(hanteraTangent);
    $('.d-value').keyup(hanteraTangentUp);

    function hanteraTangentUp(event) {
        if (event.keyCode == 17) {
            state = 'INITIAL';
        }
    }

    var speciellaTecken = {
        123 : radbytessymbol,
        222 : 'â'
    }

    function speciellTecken(element, tecken) {
        console.log("foo");
        console.log(element);
        var text = element.value;
        textF = text.substring(0, element.selectionStart);
        var cursor = element.selectionStart;
        textEfter = text.substring(cursor, text.length);
        element.value = textF + tecken + textEfter;
        element.selectionStart = element.selectionEnd = cursor + 1;
    }

    var state = 'INITIAL';
    function hanteraTangent(event) {
        console.log(state);
        console.log(event.keyCode);
        console.log(event.which);
        if (event.keyCode == 123 && state == 'INITIAL') { // 119 F8
            event.preventDefault();
            /*
            console.log(radbytessymbol);
            var sel = window.getSelection();
            console.log(sel);
            console.log(sel.toString());
            sel.text += radbytessymbol;
            */
            /*
            console.log(event.currentTarget.createTextRange);
            console.log(this.caretPos);
            console.log(this.value);
            this.value += radbytessymbol;
            console.log(this);
            */
            speciellTecken(this, radbytessymbol);
        } else if (event.keyCode == 17 && state == 'INITIAL') {
            state = 'CONTROL';
        } else if (event.keyCode == 222 && state == 'CONTROL') { // 85 u, 59 ö, 68 d, 76 l
            speciellTecken(this, 'â');
            state = 'INITIAL';
        }
    }
});
