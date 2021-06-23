function setup_page()
{
    //changing any input initiates the unsaved changes dialog
    query('input, select').forEach(elem => {
        on(elem, 'change', () => {
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

load(setup_page);