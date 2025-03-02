const isMobile = window.innerWidth <= 768;
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext('2d');

// Set canvas size
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const stars = [];
const particles = [];
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
        connections: 0,
        hovered: false
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

    // Draw particles
    particles.forEach((particle, index) => {
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius, 0, 2 * Math.PI);
        ctx.fill();
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.radius *= 0.95;
        if (particle.radius < 0.1) {
            particles.splice(index, 1);
        }
    });

    // Draw stars with hover effect
    stars.forEach(star => {
        const targetRadius = star.hovered ? STAR_RADIUS * 1.5 : STAR_RADIUS;
        star.radius += (targetRadius - star.radius) * 0.1;
        ctx.fillStyle = star.color;
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, 2 * Math.PI);
        ctx.fill();
        star.connections = 0; // Reset connections count for next frame
    });

    // Draw connections with optimized logic
    ctx.lineWidth = 0.25;
    ctx.strokeStyle = 'black';
    ctx.beginPath();

    const MAX_CONNECTIONS = 8;
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

    allConnections.sort((a, b) => a.distance - b.distance);

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

function popStar(clickedStar) {
    for (let i = 0; i < 20; i++) {
        const angle = Math.random() * 2 * Math.PI;
        const speed = Math.random() * 0.5 + 0.5;
        particles.push({
            x: clickedStar.x,
            y: clickedStar.y,
            radius: Math.random() * 2 + 1,
            color: clickedStar.color,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed
        });
    }

    const index = stars.indexOf(clickedStar);
    if (index > -1) {
        stars.splice(index, 1);
    }
}

// Add logging to click handler
canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const mouseX = (e.clientX - rect.left) * scaleX;
    const mouseY = (e.clientY - rect.top) * scaleY;

    stars.forEach(star => {
        const dist = distance({ x: mouseX, y: mouseY }, star);
        if (dist < STAR_RADIUS) {
            popStar(star);
        }
    });
});

// Update mousemove to be simpler for testing
canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const mouseX = (e.clientX - rect.left) * scaleX;
    const mouseY = (e.clientY - rect.top) * scaleY;

    stars.forEach(star => {
        const dist = distance({ x: mouseX, y: mouseY }, star);
        star.hovered = dist < STAR_RADIUS;
    });
});

let resizeTimeout;
let lastResizeTime = Date.now();

window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    
    const now = Date.now();
    if (now - lastResizeTime < 500) {
        return;
    }
    
    resizeTimeout = setTimeout(() => {
        const container = document.documentElement;
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
        
        stars.length = 0;
        for (let i = 0; i < (window.innerWidth <= 768 ? 70 : 200); i++) {
            stars.push(createStar());
        }
        
        lastResizeTime = now;
    }, 250);
});

function tick() {
    draw();
    requestAnimationFrame(tick);
}

tick();