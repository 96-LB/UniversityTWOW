function setup_form()
{
    //changing any input initiates the unsaved changes dialog
    query('input, select, textarea').forEach(elem => {
        on(elem, 'change', () => {
            query('#form_save').forEach(elem => {
                elem.disabled = false;
            })
            window.onbeforeunload = event => {
                event.preventDefault()
                return event.returnValue = "Are you sure you want to exit?";
            };
        });
    });

    //submitting the form removes it
    query('form').forEach(elem => {
        on(elem, 'submit', () => {
            window.onbeforeunload = null;
        });
    });
}

load(setup_form);