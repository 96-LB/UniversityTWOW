function setup_voting()
{
    //update the character info
    update();
    log('LOAD', '', '');

    query('button').forEach(elem => {
        on(elem, 'click', () => {
            let parent = elem.parentElement;
            if(elem.innerText == '↑' && parent.previousElementSibling)
            {
                parent.parentElement.insertBefore(parent, parent.previousElementSibling);
                log('MOVE', elem.dataset.letter, '↑')
            }
            else if(elem.innerText == '↓' && parent.nextElementSibling)
            {
                parent.parentElement.insertBefore(parent, parent.nextElementSibling.nextSibling);
            }
            unsave();
            log('MOVE', elem.dataset.letter, elem.innerText);
        });
    });

    //log all changes
    query('input[type=text]').forEach(elem => {
        on(elem, 'input', () => {
            update();
        });
        on(elem, 'change', () => {
            log('NAME', elem.dataset.letter, elem.value);
        })
    });

    //log submissions
    query('form').forEach(elem => {
        on(elem, 'submit', () => {
            log('SAVE', '', '');
        });
    });
}

function update()
{
    characters_elem = query('#voting_characters', true);
    characters_elem.innerText = characters_elem.dataset.max - query('input[type=text]')
        .map(elem => elem.value.length)
        .reduce((a, b) => a + b);
}

function log(action, response, info)
{
    fetch('/voting/logs', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            action: action,
            response: response,
            info: info
        })
    });
}

load(setup_voting);