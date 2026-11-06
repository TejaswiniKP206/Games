const birdImage = new Image();
birdImage.src = "assets/bird.png";

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const startBtn = document.getElementById("start");

const W = canvas.width, H = canvas.height;
const bird = { x: 80, y: 280, v: 0, r: 13 };
const pipes = [];
const gravity = 0.4, jump = -7, gap = 155;

let score = 0, best = Number(localStorage.best) || 0;
let playing = false, started = false, frame = 0;

function reset() {
  bird.y = 280;
  bird.v = 0;
  pipes.length = 0;
  score = frame = 0;
  playing = false;
  started = false;
  startBtn.textContent = "Start Game";
  updateScore();
}

function updateScore() {
  scoreEl.textContent = `Score: ${score} | Best: ${best}`;
}

function flap() {
  if (!started) {
    started = true;
    playing = true;
    bird.v = jump;
    startBtn.textContent = "Restart";
  } else if (playing) {
    bird.v = jump;
  }
}


function drawBird() {
  if (!birdImage.complete || !birdImage.naturalWidth) return;

  ctx.save();
  ctx.translate(bird.x, bird.y);
  ctx.rotate(Math.max(-0.25, Math.min(0.45, bird.v * 0.04)));
  ctx.drawImage(birdImage, -25, -26, 50, 52);
  ctx.restore();
}


function draw() {
  ctx.fillStyle = "#70c5ce";
  ctx.fillRect(0, 0, W, H);

  // Clouds
  ctx.fillStyle = "#ffffffaa";
  for (let i = 0; i < 3; i++) {
    ctx.beginPath();
    ctx.arc((i * 150 + frame * -0.3 + W) % W, 100 + i * 65, 20, 0, 7);
    ctx.fill();
  }

  // Pipes
  pipes.forEach(p => {
    ctx.fillStyle = "#239b43";
    ctx.fillRect(p.x, 0, 55, p.top);
    ctx.fillRect(p.x - 5, p.top - 20, 65, 20);
    ctx.fillRect(p.x, p.bottom, 55, H - 35 - p.bottom);
    ctx.fillRect(p.x - 5, p.bottom, 65, 20);
  });

  // Ground
  ctx.fillStyle = "#83bd40";
  ctx.fillRect(0, H - 35, W, 35);
  drawBird();
}

function endGame() {
  playing = false;
  best = Math.max(score, best);
  localStorage.best = best;
  startBtn.textContent = "Play Again";
  updateScore();
}

function update() {
 if (!started) {
  bird.y = 280 + Math.sin(Date.now() / 250) * 8;
}

if (playing) {
  frame++;
  bird.v += gravity;
  bird.y += bird.v;

    if (frame % 95 === 0) {
      const top = 60 + Math.random() * 210;
      pipes.push({ x: W, top, bottom: top + gap, scored: false });
    }

    for (const p of pipes) {
      p.x -= 2.5;

      const hitX = bird.x + bird.r > p.x && bird.x - bird.r < p.x + 55;
      const hitY = bird.y - bird.r < p.top || bird.y + bird.r > p.bottom;

      if (hitX && hitY) endGame();

      if (!p.scored && p.x + 55 < bird.x) {
        p.scored = true;
        score++;
        updateScore();
      }
    }

    pipes.splice(0, pipes.findIndex(p => p.x + 55 > 0) < 0 ? pipes.length : pipes.findIndex(p => p.x + 55 > 0));

    if (bird.y - bird.r < 0 || bird.y + bird.r > H - 35) endGame();
  }

  draw();
  requestAnimationFrame(update);
}

startBtn.addEventListener("click", () => {
  if (started || !playing) reset();
  else flap();
});
canvas.addEventListener("pointerdown", flap);
document.addEventListener("keydown", e => {
  if (["Space", "ArrowUp"].includes(e.code)) {
    e.preventDefault();
    if (!e.repeat) flap();
  }
});

updateScore();
update();
