
const $ = id => document.getElementById(id);
const board = $("board"), art = $("boardArt");
const socket = io();

let mode = "local", game = null, busy = false;
let onlineRoom = null, myPlayerIndex = -1;

const snakes = {27:5,40:18,43:22,54:34,76:58,89:68,99:41};
const ladders = {4:25,13:46,33:49,42:63,50:69,62:81,74:92};
const dice = ["⚀","⚁","⚂","⚃","⚄","⚅"];
const colors = ["#e47b75","#76a78d","#9c83be","#e4a44e","#6e9bb9","#d47c9e","#83a86b"];

const messages = {
    snake:"Oh no! You slid down a snake! 🐍",
    ladder:"Amazing! You climbed a ladder! 🪜",
    overshoot:"You need an exact roll to reach 100!",
    three_sixes:"Three consecutive sixes! Back to START! 😵",
    winner:"Congratulations! You won! 🎉"
};

// ==================================
// BOARD
// ==================================

function point(n) {
    const r=Math.floor((n-1)/10);
    const c=r%2?9-(n-1)%10:(n-1)%10;
    return {x:(c+.5)*100,y:(9-r+.5)*100};
}

function svg(tag,attrs) {
    const el=document.createElementNS("http://www.w3.org/2000/svg",tag);
    Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));
    art.appendChild(el);
}

function drawSnake(a,b,color) {
    a=point(a); b=point(b);
    const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy)||1;
    const px=-dy/len*Math.min(65,len*.16),py=dx/len*Math.min(65,len*.16);
    const d=`M${a.x} ${a.y} C${a.x+px} ${a.y+dy*.28},${b.x-px} ${b.y-dy*.28},${b.x} ${b.y}`;

    svg("path",{d,fill:"none",stroke:"#543c54","stroke-width":20,opacity:.18});
    svg("path",{d,fill:"none",stroke:color,"stroke-width":15,"stroke-linecap":"round",class:"snake-body"});
    svg("path",{d,fill:"none",stroke:"#ffe4a9","stroke-width":4,"stroke-dasharray":"5 13",class:"snake-belly"});
    svg("circle",{cx:a.x,cy:a.y,r:14,fill:color,stroke:"#fff1d9","stroke-width":2,class:"snake-head"});

    [-5,5].forEach(x=>svg("circle",{cx:a.x+x,cy:a.y-4,r:3,fill:"white"}));
}

function drawLadder(start,end) {
    const a=point(start),b=point(end);
    const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy)||1;
    const px=-dy/len*9,py=dx/len*9;

    [-1,1].forEach(s=>{
        const attrs={x1:a.x+px*s,y1:a.y+py*s,x2:b.x+px*s,y2:b.y+py*s,"stroke-linecap":"round"};
        svg("line",{...attrs,stroke:"#80512f","stroke-width":8});
        svg("line",{...attrs,stroke:"#e9b75d","stroke-width":5,class:"ladder-rail"});
    });

    for(let i=1;i<=7;i++){
        const t=i/8,x=a.x+dx*t,y=a.y+dy*t;
        svg("line",{x1:x+px,y1:y+py,x2:x-px,y2:y-py,stroke:"#fff0b6","stroke-width":5,class:"ladder-step"});
    }
}

function createBoard() {
    board.querySelectorAll(".cell,.token").forEach(el=>el.remove());

    for(let n=100;n>=1;n--){
        const p=point(n),cell=document.createElement("div");
        cell.className="cell"+(n===1?" start-cell":n===100?" end-cell":"");
        cell.textContent=n;
        cell.style.gridRow=Math.floor(p.y/100)+1;
        cell.style.gridColumn=Math.floor(p.x/100)+1;
        board.appendChild(cell);
    }

    art.innerHTML="";
    Object.entries(ladders).forEach(([a,b])=>drawLadder(+a,+b));
    Object.entries(snakes).forEach(([a,b],i)=>drawSnake(+a,+b,colors[i]));

    for(let i=0;i<2;i++){
        const token=document.createElement("div");
        token.id=`token${i}`;
        token.className=`token ${i?"two":"one"}`;
        board.appendChild(token);
    }
}

// ==================================
// PLAYER DISPLAY
// ==================================

function moveToken(i,pos) {
    const p=point(pos),token=$(`token${i}`);
    token.style.left=`${p.x/10}%`;
    token.style.top=`${p.y/10}%`;
    token.style.transform=`translate(calc(-50% + ${i?8:-8}px),-50%)`;
}

function updateScreen(status) {
    game=status;

    status.players.forEach((p,i)=>{
        $(`name${i}`).textContent=p.name;
        $(`position${i}`).textContent=p.position;
        $(`playerCard${i}`).classList.toggle("active",i===status.current_player&&!status.winner);
        $(`turn${i}`).textContent=status.winner
            ?status.winner===p.name?"WINNER 🏆":"FINISHED"
            :i===status.current_player?"YOUR TURN":"WAITING";
        moveToken(i,p.position);
    });

    $("turnMessage").textContent=status.winner
        ?`${status.winner} wins! 🏆`
        :`${status.current_player_name}, roll the dice!`;

    $("rollBtn").disabled=!!status.winner;
}

function showResult(r) {
    $("diceDisplay").textContent=dice[r.dice-1];
    $("gameMessage").textContent=
        `${r.player} rolled ${r.dice}. ${messages[r.event]||r.message||"Nice roll!"}`;

    if(r.event==="winner") document.body.classList.add("winner-mode");
}

// ==================================
// API HELPER
// ==================================

async function api(url,body) {
    const res=await fetch(url,{
        method:"POST",
        ...(body?{
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify(body)
        }:{})
    });
    const data=await res.json();
    if(!res.ok) throw Error(data.error||"Something went wrong!");
    return data;
}

// ==================================
// GAME MODE
// ==================================

document.querySelectorAll(".mode-btn").forEach(btn=>{
    btn.onclick=()=>{
        document.querySelectorAll(".mode-btn").forEach(b=>b.classList.remove("active"));
        btn.classList.add("active");
        mode=btn.dataset.mode;

        $("player2").style.display=["computer","online"].includes(mode)?"none":"block";
        $("onlineControls").classList.toggle("hidden",mode!=="online");
        $("startBtn").style.display=mode==="online"?"none":"inline-block";
        $("setupMessage").textContent="";
    };
});

// ==================================
// START GAME
// ==================================

$("startBtn").onclick=async()=>{
    $("startBtn").disabled=true;
    try{
        const data=await api("/api/start",{
            mode,
            player1:$("player1").value.trim()||"Player 1",
            player2:mode==="computer"?"Sunset Bot":$("player2").value.trim()||"Player 2"
        });

        document.body.classList.remove("winner-mode");
        createBoard();
        updateScreen(data.status);
        $("setupPanel").classList.add("hidden");
        $("gameArea").classList.remove("hidden");
        $("diceDisplay").textContent="🎲";
        $("gameMessage").textContent="Let the sunset adventure begin! 🌅";
    }catch(e){
        $("setupMessage").textContent=e.message;
    }finally{
        $("startBtn").disabled=false;
    }
};

// ==================================
// ONLINE MULTIPLAYER
// ==================================

$("createRoomBtn").onclick=()=>{
    socket.emit("create_room",{name:$("player1").value.trim()||"Player 1"});
    $("onlineMessage").textContent="Creating room...";
};

$("joinRoomBtn").onclick=()=>{
    const room=$("roomCode").value.trim().toUpperCase();
    if(!room){$("onlineMessage").textContent="Enter a room code!";return;}
    socket.emit("join_room",{room,name:$("player1").value.trim()||"Player 2"});
    $("onlineMessage").textContent="Joining room...";
};

socket.on("room_created",data=>{
    onlineRoom=data.room;
    $("onlineMessage").innerHTML=`Share this room code: <strong>${data.room}</strong><br>Waiting for your friend...`;
});

socket.on("game_started",data=>{
    mode="online";
    onlineRoom=data.room;
    myPlayerIndex=data.player_index;
    busy=false;

    document.body.classList.remove("winner-mode");
    createBoard();
    updateScreen(data.status);

    $("setupPanel").classList.add("hidden");
    $("gameArea").classList.remove("hidden");
    $("diceDisplay").textContent="🎲";
    $("gameMessage").textContent="Both players connected! 🌅";
    $("rollBtn").disabled=myPlayerIndex!==data.status.current_player;
});

socket.on("online_update",data=>{
    showResult(data.result);
    updateScreen(data.status);
    busy=false;
    $("rollBtn").disabled=!!data.status.winner||data.status.current_player!==myPlayerIndex;
});

socket.on("room_error",data=>{
    busy=false;
    $("onlineMessage").textContent=data.message;
    $("gameMessage").textContent=data.message;
    if(game&&!game.winner&&game.current_player===myPlayerIndex)
        $("rollBtn").disabled=false;
});

// ==================================
// DICE ROLLING
// ==================================

const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));

async function animateDice() {
    $("diceDisplay").classList.add("rolling");
    await delay(550);
    $("diceDisplay").classList.remove("rolling");
}

async function rollOnlineDice() {
    if(busy||!onlineRoom||!game||game.winner||game.current_player!==myPlayerIndex)return;

    busy=true;
    $("rollBtn").disabled=true;
    await animateDice();
    socket.emit("online_roll",{room:onlineRoom});
}

async function rollDice() {
    if(busy||!game||game.winner)return;

    busy=true;
    $("rollBtn").disabled=true;
    await animateDice();

    try{
        const data=await api("/api/roll");
        showResult(data.result);
        updateScreen(data.status);
    }catch(e){
        $("gameMessage").textContent=e.message;
    }

    busy=false;

    if(game.winner)return;

    if(mode==="computer"&&game.current_player_name==="Sunset Bot"){
        $("rollBtn").disabled=true;
        $("turnMessage").textContent="Sunset Bot is rolling... 🤖";
        setTimeout(rollDice,1200);
    }else{
        $("rollBtn").disabled=false;
    }
}

$("rollBtn").onclick=()=>{
    if(mode==="online")rollOnlineDice();
    else rollDice();
};

// ==================================
// RESTART
// ==================================

$("restartBtn").onclick=()=>{
    $("gameArea").classList.add("hidden");
    $("setupPanel").classList.remove("hidden");
    $("setupMessage").textContent="";
    $("onlineMessage").textContent="";
    $("diceDisplay").textContent="🎲";
    $("rollBtn").disabled=false;

    document.body.classList.remove("winner-mode");

    game=null;
    busy=false;
    onlineRoom=null;
    myPlayerIndex=-1;
};

createBoard();
