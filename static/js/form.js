'use strict';

function setup_form()
{
    //changing any input initiates the unsaved changes dialog
    query('input, select, textarea').forEach(elem => {
        on(elem, 'change', () => {
            unsave();
        });
    });

    //submitting the form removes it
    query('form').forEach(elem => {
        on(elem, 'submit', () => {
            window.onbeforeunload = null;
        });
    });
}

function unsave()
{
    let save_elem = query('#form_save', true);
    if(save_elem)
    {
        save_elem.disabled = false;
    }
    window.onbeforeunload = event => {
        event.preventDefault()
        return event.returnValue = "Are you sure you want to exit?";
    };
}

load(setup_form);