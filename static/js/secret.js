'use strict';

const CENTER = [480, 480];
const SIZE = 240;
const COLORS = [
    [192, 24, 0],
    [192, 192, 0],
    [0, 192, 24],
    [24, 0, 192],
    [128, 0, 128]
];

function setup_secret_page()
{
    //gather all of the data
    let canvas_elem = query('#secret_canvas', true); 
    let data = JSON.parse(atob(canvas_elem.dataset.branches));
    let ctx = canvas_elem.getContext('2d');
    let map = query('#secret_map', true);
    let background = query('#secret_bg', true);
    let opacity = 0;

    let pentagon = [];
    
    //build the triangle for each branch
    for(let i = 0; i < 5; i++)
    {
        //check whether the branch has been completed
        let completed = data[i]['completed'];
        if(completed)
        {
            opacity += opacity + 1 / 31;
            pentagon.push(pointOnCircle(i * 2 * Math.PI / 5));
        }

        //draw the triangle on the canvas
        let triangle = get_triangle(i * 2 * Math.PI / 5 - Math.PI / 2, completed);
        polygon(ctx, rgb(...COLORS[i], !completed), ...triangle);
        
        //add a clickable region to the link map
        let area = document.createElement('area');
        area.shape = 'polygon';
        area.coords = triangle.flat().join();
        area.href = data[i]['link'];
        map.appendChild(area);
    }
    
    if(pentagon.length == 5)
    {
        //add a clickable region to the link map
        let area = document.createElement('area');
        area.shape = 'polygon';
        area.coords = pentagon.flat().join();
        area.href = data[5]['link'];
        map.appendChild(area);
    }
    
    //vary the portal opacity by the number of branches completed
    background.style.opacity = opacity;
}

function rgb(r, g, b, dark=false)
{
    //converts rgb values to a css string
    if(dark)
    {
        r = Math.floor(r / 4);
        g = Math.floor(g / 4);
        b = Math.floor(b / 4);
    }
    return `rgb(${r}, ${g}, ${b})`;
}

function polygon(ctx, fillStyle, start, ...points)
{
    //draws a polygon with the specified points and fill style
    let old = ctx.fillStyle;
    ctx.fillStyle = fillStyle;
    ctx.beginPath();
    ctx.moveTo(start[0], start[1]);
    for(let point of points)
    {
        ctx.lineTo(point[0], point[1]);
    }
    ctx.fill();
    ctx.fillStyle = old;
}

function pointOnCircle(angle, factor=1)
{
    //gets a point on the center circle with the given angle
    return [CENTER[0] + factor * SIZE * Math.cos(angle), CENTER[1] + factor * SIZE * Math.sin(angle)];
}

function get_triangle(angle, completed)
{
    //calculates the angles for each point of the triangle
    let leftAngle = angle - Math.PI / 5;
    let rightAngle = angle + Math.PI / 5;
    
    //calculates each point of the triangle; the middle one should be farther away
    let leftPoint = pointOnCircle(leftAngle);
    let point = completed ? pointOnCircle(angle, 2 * Math.sin(3 * Math.PI / 10)) : CENTER;
    let rightPoint = pointOnCircle(rightAngle);
    return [leftPoint, point, rightPoint];
}

load(setup_secret_page);
