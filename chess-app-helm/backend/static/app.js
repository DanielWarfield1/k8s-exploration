// ===============================
// Unicode chess pieces
// ===============================
const PIECES = {
  "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
  "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚"
};

// ===============================
// Game State
// ===============================
let board = [];
let selected = null;
let gameId = null;

// Track whose turn it is (true = white, false = black)
let turn = 'w'; // White starts

// Track move counters for FEN
let halfmoveClock = 0;
let fullmoveNumber = 1;

const overlay = document.getElementById("thinking-overlay");
const boardDiv = document.getElementById("board");

// ===============================
// Initialize board to startpos
// ===============================
function initBoardState() {
  board = [
    "rnbqkbnr".split(""),
    "pppppppp".split(""),
    Array(8).fill(null),
    Array(8).fill(null),
    Array(8).fill(null),
    Array(8).fill(null),
    "PPPPPPPP".split(""),
    "RNBQKBNR".split("")
  ];
  turn = 'w';
  halfmoveClock = 0;
  fullmoveNumber = 1;
}

// ===============================
// Convert board → FEN (mirroring python-chess)
// ===============================
function boardToFEN() {
  const rows = board.map(row => {
    let empty = 0;
    let s = "";
    for (let sq of row) {
      if (sq === null) {
        empty++;
      } else {
        if (empty > 0) {
          s += empty;
          empty = 0;
        }
        s += sq;
      }
    }
    if (empty > 0) s += empty;
    return s;
  });

  const placement = rows.join("/");
  
  // For now, use basic FEN without castling/en passant
  // You might need to track these if your engine uses them
  const fen = `${placement} ${turn} KQkq - ${halfmoveClock} ${fullmoveNumber}`;
  
  console.log("FEN sent to backend:", fen);
  return fen;
}

// ===============================
// Convert coordinates to UCI (e2e4, etc.)
// ===============================
function toUCI(sr, sc, tr, tc) {
  const files = "abcdefgh";
  const from = files[sc] + (8 - sr);
  const to = files[tc] + (8 - tr); // Fixed: should be tr not tc
  return from + to;
}

// ===============================
// Apply a UCI move to our board
// ===============================
function applyUCIMove(move) {
  const files = "abcdefgh";
  
  const fromFile = move[0];
  const fromRank = parseInt(move[1], 10);
  const toFile = move[2];
  const toRank = parseInt(move[3], 10);
  
  const sc = files.indexOf(fromFile);
  const sr = 8 - fromRank;
  
  const tc = files.indexOf(toFile);
  const tr = 8 - toRank;
  
  const piece = board[sr][sc];
  if (!piece) {
    console.warn("applyUCIMove: no piece at", move, "sr=", sr, "sc=", sc);
    return false;
  }
  
  // Update move counters
  if (piece.toLowerCase() === 'p' || board[tr][tc] !== null) {
    halfmoveClock = 0;
  } else {
    halfmoveClock++;
  }
  
  // Update fullmove number after black's move
  if (turn === 'b') {
    fullmoveNumber++;
  }
  
  // Move the piece
  board[sr][sc] = null;
  board[tr][tc] = piece;
  
  // Toggle turn
  turn = turn === 'w' ? 'b' : 'w';
  
  return true;
}

// ===============================
// Render the board
// ===============================
function renderBoard() {
  boardDiv.innerHTML = "";
  
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      const sq = document.createElement("div");
      sq.classList.add("square");
      sq.classList.add((r + c) % 2 === 0 ? "light" : "dark");
      sq.dataset.row = r;
      sq.dataset.col = c;
      
      const piece = board[r][c];
      if (piece) {
        sq.textContent = PIECES[piece];
      }
      
      sq.onclick = () => handleClick(r, c);
      
      if (selected && selected.r === r && selected.c === c) {
        sq.classList.add("selected");
      }
      
      boardDiv.appendChild(sq);
    }
  }
}

// ===============================
// Handle clicking on the board
// ===============================
function handleClick(r, c) {
  // Don't allow moves when it's not the player's turn
  if (turn === 'b') {
    console.log("Not your turn - engine is thinking");
    return;
  }
  
  // First click: select piece
  if (!selected) {
    const piece = board[r][c];
    if (piece && piece === piece.toUpperCase()) { // Only allow white pieces
      selected = { r, c };
      renderBoard();
    }
    return;
  }
  
  // Second click: make move
  const move = toUCI(selected.r, selected.c, r, c);
  console.log("Player move UCI:", move);
  
  // Apply the move locally
  if (applyUCIMove(move)) {
    // Clear selection
    selected = null;
    
    // Get FEN after player's move (just like Python client)
    const fenAfterMove = boardToFEN();
    console.log("Sending FEN to backend:", fenAfterMove);
    
    // Render the updated board
    renderBoard();
    
    // Send to backend
    sendMove(move, fenAfterMove);
  } else {
    // Invalid move
    selected = null;
    renderBoard();
    alert("Invalid move!");
  }
}

// ===============================
// Backend communication
// ===============================
async function startGame() {
  console.log("Starting new game via /start...");
  try {
    const res = await fetch("/start");
    const data = await res.json();
    console.log("Received game_id:", data.game_id);
    gameId = data.game_id;
  } catch (err) {
    console.error("Failed to start game:", err);
    alert("Failed to connect to backend");
  }
}

async function sendMove(move, fen) {
  showThinking(true);
  
  try {
    console.log("Sending to /move:", { game_id: gameId, move, fen });
    
    const res = await fetch("/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        game_id: gameId,
        move: move,
        fen: fen
      })
    });
    
    if (!res.ok) {
      throw new Error(`Backend error: ${res.statusText}`);
    }
    
    const data = await res.json();
    const engineMove = data.best_move;
    console.log("Engine plays:", engineMove);
    
    // Apply engine's move
    applyUCIMove(engineMove);
    
    // Render the updated board
    renderBoard();
    
    // Check if game is over (simple check for now)
    const pieces = board.flat().filter(p => p && p.toLowerCase() === 'k');
    if (pieces.length < 2) {
      alert("Game over!");
    }
    
  } catch (err) {
    console.error("Engine error:", err);
    alert("Error communicating with engine");
  }
  
  showThinking(false);
}

// ===============================
// Thinking overlay
// ===============================
function showThinking(show) {
  overlay.classList.toggle("show", show);
}

// ===============================
// Kick things off
// ===============================
initBoardState();
renderBoard();
startGame();