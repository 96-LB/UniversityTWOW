function on(elem, event, func)
{
    //attaches an event listener to the provided element
    if(elem.addEventListener)
        elem.addEventListener(event, func);
    else if(elem.attachEvent)
        elem.attachEvent('on' + event, func);
    else
        throw new Error(`Failed to add event to ${elem}`);
}

function load(func)
{
    //shorthand for adding to window.onload
    return on(window, 'load', func)
}

function query(selector, first=false)
{
    //selects elements that fit the css selector
    return first ?
        document.querySelector(selector) :
        [...document.querySelectorAll(selector)];
}