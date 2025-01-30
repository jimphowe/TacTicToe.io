const isMobile = window.innerWidth <= 768;
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const stars = [];
const numStars = isMobile ? 70 : 200;
const mouse = { x: 0, y: 0 };
const STAR_RADIUS = 8;
const LINE_DISTANCE = 150;

function isOverlapping(newStar) {
    return stars.some(star => {
        const dist = distance(newStar, star);
        return dist < (STAR_RADIUS * 2);
    });
}

function createStar() {
    const color = ['#FF0000', '#0000FF', '#000000'][Math.floor(Math.random() * 3)];
    let newStar = {
        originalX: Math.random() * canvas.width,
        originalY: Math.random() * canvas.height,
        x: 0,
        y: 0,
        radius: STAR_RADIUS,
        color: color,
        connections: 0
    };

    newStar.x = newStar.originalX + (Math.random() - 0.5) * 20;
    newStar.y = newStar.originalY + (Math.random() - 0.5) * 20;

    while (isOverlapping(newStar)) {
        newStar.originalX = Math.random() * canvas.width;
        newStar.originalY = Math.random() * canvas.height;
        newStar.x = newStar.originalX + (Math.random() - 0.5) * 20;
        newStar.y = newStar.originalY + (Math.random() - 0.5) * 20;
    }

    return newStar;
}

for (let i = 0; i < numStars; i++) {
    stars.push(createStar());
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.globalCompositeOperation = "lighter";

    stars.forEach(star => {
        ctx.fillStyle = star.color;
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, 2 * Math.PI);
        ctx.fill();
    });

    ctx.lineWidth = 0.25;
    ctx.strokeStyle = 'black';
    ctx.beginPath();

    const MAX_CONNECTIONS = 8;  // Maximum connections per star

    // Sort all possible connections by distance
    let allConnections = [];
    stars.forEach((star1, i) => {
        stars.slice(i + 1).forEach(star2 => {
            const dist = distance(star1, star2);
            if (dist < LINE_DISTANCE) {
                allConnections.push({
                    star1,
                    star2,
                    distance: dist
                });
            }
        });
    });

    // Sort connections by distance (shorter first)
    allConnections.sort((a, b) => a.distance - b.distance);

    // Draw connections, respecting max connections per star
    allConnections.forEach(conn => {
        if (conn.star1.connections < MAX_CONNECTIONS && 
            conn.star2.connections < MAX_CONNECTIONS) {
            ctx.moveTo(conn.star1.x, conn.star1.y);
            ctx.lineTo(conn.star2.x, conn.star2.y);
            conn.star1.connections++;
            conn.star2.connections++;
        }
    });

    ctx.stroke();
}

function distance(point1, point2) {
    const xs = point2.x - point1.x;
    const ys = point2.y - point1.y;
    return Math.sqrt(xs * xs + ys * ys);
}

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    stars.length = 0;  // Clear existing stars
    for (let i = 0; i < (window.innerWidth <= 768 ? 70 : 200); i++) {
        stars.push(createStar());
    }
    draw();
});

draw();