function on(elem, event, func)
{
    if(elem.addEventListener)
    {
        elem.addEventListener(event, func);
    }
    else if(elem.attachEvent)
    {
        elem.attachEvent('on' + event, func);
    }
    else
    {
        throw new Error(`Failed to add event to ${elem}`);
    }
}

function load(func)
{
    return on(window, 'load', func)
}

function query(selector)
{
    return [...document.querySelectorAll(selector)];
}