'use strict';

function setup_secret_page()
{
    //changing any input initiates the unsaved changes dialog
    query('input, select, textarea').forEach(elem => {
        on(elem, 'change', () => {
            update();
        });
    });
    update();
}

function get_inputs(elem)
{
    //if this element is an input, return its value
    if(elem.nodeName == 'INPUT' && elem.type != 'submit' && elem.type != 'hidden')
    {
        return elem.value && ((elem.type != 'checkbox' && elem.type != 'radio') || elem.checked) ? [elem.value] : [];
    }
    else
    {
        //recursively check its children for inputs 
        let out = []
        if(elem.children)
        {
            for(let child of Array.from(elem.children))
            {
                out = out.concat(get_inputs(child));
            }
        }
        return out;
    }
}

function update()
{
    //reads the input values
    let answer_elem = query('#secret_answer', true);
    let values = get_inputs(answer_elem.form);

    //combines the values based on the data type - default is to use the first
    answer_elem.value = values.length > 0 ? values[0] : ''
    switch(answer_elem.dataset.type)
    {
        case 'sorted':
            values.sort()
            //intentional fallthrough to case concat
        case 'concat':
            answer_elem.value = values.join('-')
            break;
    }
}

load(setup_secret_page);
