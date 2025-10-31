const boardEl = document.getElementById("board");
const scoreEl = document.getElementById("score");
const movesEl = document.getElementById("moves");
const bestEl  = document.getElementById("best");
const btnNew  = document.getElementById("btn-new");
const btnUndo = document.getElementById("btn-undo");
const btnHint = document.getElementById("btn-hint");
const btnShuffle = document.getElementById("btn-shuffle");
const toastContainer = document.getElementById("toast-container");

let inputLocked = false;   
const ANIM_MS = 140;       
const MERGE_DELAY_MS = 40;

// Toast notification function
function showToast(message, type = 'info', duration = 3000) {
  if (!toastContainer) {
    console.warn("Toast container not found");
    return;
  }
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  // Icon based on type
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  };
  
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
    <span class="toast-content">${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">×</button>
  `;
  
  toastContainer.appendChild(toast);
  
  // Auto remove after duration
  let timeoutId = setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, duration);
  
  // Store timeout ID to clear if manually closed
  toast.dataset.timeoutId = timeoutId;
  
  return toast;
} 


function render({ grid, score, moves, new_tiles = [], merged_cells = [] }) {
  if (!boardEl || !scoreEl || !movesEl || !bestEl) {
    console.error("Required DOM elements not found");
    return;
  }
  
  // Save current grid to window for swap functionality
  window.currentGrid = grid;

  boardEl.innerHTML = "";
  for (let i = 0; i < 16; i++) {
    const div = document.createElement("div");
    div.className = "tile empty";
    boardEl.appendChild(div);
  }


  grid.forEach((row, r) => {
    row.forEach((v, c) => {
      if (!v) return;
      const div = document.createElement("div");
      div.className = "tile";
      div.dataset.val = v;
      div.dataset.row = r;
      div.dataset.col = c;
      div.textContent = v;
      div.style.gridRowStart = r + 1;
      div.style.gridColumnStart = c + 1;

      
      if (new_tiles.some(cell => cell && cell.r === r && cell.c === c)) {
        div.classList.add("spawn");
      }
    
      if (merged_cells.some(cell => cell && cell.r === r && cell.c === c)) {
        setTimeout(() => div.classList.add("merge"), MERGE_DELAY_MS);
      }
      boardEl.appendChild(div);
    });
  });

  
  scoreEl.textContent = score;
  movesEl.textContent = moves;

 
  const best = parseInt(localStorage.getItem("best") || "0", 10);
  if (score > best) {
    localStorage.setItem("best", score);
    bestEl.textContent = score;
  } else {
    bestEl.textContent = best;
  }
}

function updateUndoButton(canUndo) {
  if (!btnUndo) return;
  btnUndo.disabled = !canUndo;
  btnUndo.classList.toggle("disabled", !canUndo);
}

function showGameOverOverlay({ score, max_tile, moves }) {
  if (!boardEl) {
    console.error("Board element not found");
    return;
  }
  
  removeGameOverOverlay();
  const overlay = document.createElement("div");
  overlay.className = "overlay";
  overlay.innerHTML = `
    <div class="overlay-content">
      <h2>Game Over</h2>
      <p>Score: ${score} &bull; Max Tile: ${max_tile} &bull; Moves: ${moves}</p>
      <button id="btn-restart-overlay">Chơi lại</button>
    </div>
  `;
  boardEl.appendChild(overlay);
  requestAnimationFrame(() => overlay.classList.add("show"));
  const restartBtn = document.getElementById("btn-restart-overlay");
  if (restartBtn) {
    restartBtn.addEventListener("click", startGame);
  }
}

function removeGameOverOverlay() {
  const overlay = boardEl.querySelector(".overlay");
  if (overlay) overlay.remove();
}


async function startGame() {
  try {
    inputLocked = true;
    const res = await fetch("/api/start_game", { method: "POST" });
    const data = await res.json();
    if (!data.ok) {
      console.error("Start game error:", data.message);
      return;
    }
    render(data);
    updateUndoButton(data.can_undo ?? false);
    removeGameOverOverlay();
  } catch (e) {
    console.error("startGame fetch error:", e);
  } finally {
   
    setTimeout(() => (inputLocked = false), ANIM_MS);
  }
}

async function handleMove(direction) {
  if (inputLocked) return;
  inputLocked = true;

  try {
    const res = await fetch("/api/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ direction })
    });
    const data = await res.json();


    if (!data.ok) {
      console.warn("Move not ok:", data.message);
      return;
    }

   
    render(data);
    updateUndoButton(!!data.can_undo);

    if (data.game_over) {
      
      setTimeout(() => showGameOverOverlay(data.game_over), ANIM_MS + 80);
    }
  } catch (e) {
    console.error("handleMove fetch error:", e);
  } finally {
    setTimeout(() => (inputLocked = false), ANIM_MS);
  }
}

async function undo() {
  if (inputLocked) return;
  inputLocked = true;

  try {
    const res = await fetch("/api/undo", { method: "POST" });
    const data = await res.json();
    if (!data.ok) {
      console.warn("Undo error:", data.message);
      return;
    }
    render(data);
    updateUndoButton(!!data.can_undo);
    removeGameOverOverlay();
  } catch (e) {
    console.error("undo fetch error:", e);
  } finally {
    setTimeout(() => (inputLocked = false), ANIM_MS / 2);
  }
}


window.addEventListener("keydown", (e) => {
  const map = { ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down" };
  if (map[e.key]) {
    e.preventDefault();
    handleMove(map[e.key]);
  }
});

let touchStartX = 0, touchStartY = 0;
let touchMoved = false;
let touchStartedOnBoard = false;
const MIN_SWIPE_DISTANCE = 25; // Giảm khoảng cách để nhạy hơn

// Touch events - Cố định bàn cờ khi vuốt, không cho scroll trang
boardEl.addEventListener("touchstart", e => {
  // Nếu đang ở swap mode, không xử lý swipe (để handler riêng của swap xử lý)
  if (swapMode) {
    return;
  }
  
  // Chỉ block nếu bắt đầu trên board (tránh block toàn trang)
  if (e.target === boardEl || boardEl.contains(e.target)) {
    touchStartedOnBoard = true;
    const t = e.touches && e.touches[0];
    if (!t || inputLocked) {
      touchStartedOnBoard = false;
      return;
    }
    touchStartX = t.clientX;
    touchStartY = t.clientY;
    touchMoved = false;
    // Prevent default ngay từ đầu để ngăn scroll
    e.preventDefault();
  } else {
    touchStartedOnBoard = false;
  }
}, { passive: false }); // Không passive để có thể preventDefault

// Touchmove để theo dõi quá trình vuốt và ngăn scroll
let lastTouchTime = 0;
boardEl.addEventListener("touchmove", e => {
  // Nếu đang ở swap mode, không xử lý swipe
  if (swapMode) {
    return; // Để handler riêng của swap xử lý
  }
  
  if (!touchStartedOnBoard || inputLocked) return;
  
  // Prevent default để ngăn scroll trang khi vuốt trên board
  e.preventDefault();
  
  const now = performance.now();
  // Throttle để tránh quá nhiều event (60fps max)
  if (now - lastTouchTime < 16) return;
  lastTouchTime = now;
  
  const t = e.touches && e.touches[0];
  if (!t) return;
  
  const dx = t.clientX - touchStartX;
  const dy = t.clientY - touchStartY;
  const absx = Math.abs(dx), absy = Math.abs(dy);
  
  // Nếu đã di chuyển đủ xa, đánh dấu là đã vuốt
  if (Math.max(absx, absy) > 8) {
    touchMoved = true;
  }
}, { passive: false }); // Không passive để có thể preventDefault

boardEl.addEventListener("touchend", e => {
  // Nếu đang ở swap mode, không xử lý swipe
  if (swapMode) {
    return; // Để handler riêng của swap xử lý
  }
  
  if (!touchStartedOnBoard || inputLocked) {
    touchStartedOnBoard = false;
    touchMoved = false;
    return;
  }
  
  const t = e.changedTouches && e.changedTouches[0];
  if (!t) {
    touchStartedOnBoard = false;
    touchMoved = false;
    return;
  }
  
  const dx = t.clientX - touchStartX;
  const dy = t.clientY - touchStartY;
  const absx = Math.abs(dx), absy = Math.abs(dy);
  
  // Chỉ xử lý nếu đã vuốt đủ xa
  if (Math.max(absx, absy) >= MIN_SWIPE_DISTANCE && touchMoved) {
    // Chỉ preventDefault khi cần (đã vuốt đủ xa)
    e.preventDefault();
    
    // Sử dụng requestAnimationFrame để đảm bảo mượt mà
    requestAnimationFrame(() => {
      if (inputLocked) return; // Kiểm tra lại trước khi xử lý
      
      if (absx > absy) {
        handleMove(dx > 0 ? "right" : "left");
      } else {
        handleMove(dy > 0 ? "down" : "up");
      }
    });
  }
  
  // Reset state
  touchStartedOnBoard = false;
  touchMoved = false;
  touchStartX = 0;
  touchStartY = 0;
}, { passive: false });

// Touchcancel để reset trạng thái nếu vuốt bị hủy
boardEl.addEventListener("touchcancel", () => {
  touchStartedOnBoard = false;
  touchMoved = false;
}, { passive: true });

btnNew?.addEventListener("click", startGame);
btnUndo?.addEventListener("click", undo);

// Premium features
btnHint?.addEventListener("click", async () => {
  if (!window.IS_PREMIUM) {
    showToast("Tính năng này chỉ dành cho Premium! Vui lòng nâng cấp tài khoản.", 'warning', 4000);
    return;
  }
  
  if (inputLocked) return;
  inputLocked = true;
  
  try {
    const res = await fetch("/api/premium/hint", { method: "POST" });
    const data = await res.json();
    
    if (data.ok && data.direction) {
      const directionText = data.direction === 'up' ? 'LÊN' : data.direction === 'down' ? 'XUỐNG' : data.direction === 'left' ? 'TRÁI' : 'PHẢI';
      showToast(`Gợi ý: Di chuyển sang ${directionText}!`, 'info', 2500);
    } else {
      showToast(data.message || "Không có gợi ý", 'warning');
    }
  } catch (e) {
    console.error("Hint error:", e);
    showToast("Có lỗi xảy ra khi lấy gợi ý", 'error');
  } finally {
    inputLocked = false;
  }
});

btnShuffle?.addEventListener("click", async () => {
  if (!window.IS_PREMIUM) {
    showToast("Tính năng này chỉ dành cho Premium! Vui lòng nâng cấp tài khoản.", 'warning', 4000);
    return;
  }
  
  if (!confirm("Bạn có chắc muốn xáo trộn bàn cờ? Bạn sẽ mất nước đi hiện tại.")) {
    return;
  }
  
  if (inputLocked) return;
  inputLocked = true;
  
  try {
    // Animate shuffle effect before API call
    const tiles = document.querySelectorAll('.tile:not(.empty)');
    tiles.forEach((tile, index) => {
      tile.style.transition = "all 0.6s cubic-bezier(0.4, 0, 0.2, 1)";
      tile.style.transform = "scale(0.3) rotate(720deg)";
      tile.style.opacity = "0";
    });
    
    const res = await fetch("/api/premium/shuffle", { method: "POST" });
    const data = await res.json();
    
    if (data.ok && data.grid) {
      setTimeout(() => {
        render({ grid: data.grid, score: scoreEl.textContent, moves: movesEl.textContent, new_tiles: [], merged_cells: [] });
        
        // Animate new tiles in
        const newTiles = document.querySelectorAll('.tile:not(.empty)');
        newTiles.forEach((tile, index) => {
          tile.style.transform = "scale(0) rotate(-720deg)";
          tile.style.opacity = "0";
          setTimeout(() => {
            tile.style.transition = "all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)";
            tile.style.transform = "scale(1) rotate(0deg)";
            tile.style.opacity = "1";
          }, index * 20);
        });
        
        showToast("Đã xáo trộn bàn cờ thành công!", 'success');
      }, 600);
    } else {
      showToast(data.message || "Không thể xáo trộn", 'warning');
    }
  } catch (e) {
    console.error("Shuffle error:", e);
    showToast("Có lỗi xảy ra khi xáo trộn", 'error');
  } finally {
    inputLocked = false;
  }
});

// Swap two tiles button
const btnSwap = document.getElementById("btn-swap");
let swapMode = false;
let firstTile = null;

btnSwap?.addEventListener("click", () => {
  if (!window.IS_PREMIUM) {
    showToast("Tính năng này chỉ dành cho Premium! Vui lòng nâng cấp tài khoản.", 'warning', 4000);
    return;
  }
  
  if (!swapMode) {
    swapMode = true;
    btnSwap.classList.add("active");
    btnSwap.textContent = "✓ Chọn 2 ô";
    showToast("Chế độ Đổi chỗ: Click vào 2 ô bất kỳ để đổi chỗ.", 'info', 3500);
  } else {
    swapMode = false;
    btnSwap.classList.remove("active");
    btnSwap.textContent = "🔄 Đổi chỗ 2 ô";
    firstTile = null;
  }
});

// Function to handle tile selection for swap (dùng chung cho cả click và touch)
function handleTileSelection(e, touchEvent = false) {
  if (!swapMode) return;
  
  // Nếu là touch event trong swap mode, prevent default để tránh conflict với swipe
  if (touchEvent) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  // Tìm tile element từ target hoặc parent
  let cell = e.target;
  while (cell && cell !== document.body) {
    if (cell.classList && cell.classList.contains('tile')) {
      break;
    }
    cell = cell.parentElement;
  }
  
  // Kiểm tra nếu không phải tile hoặc là tile trống
  if (!cell || cell.classList.contains('empty') || !cell.dataset.row) {
    return;
  }
  
  const row = parseInt(cell.dataset.row);
  const col = parseInt(cell.dataset.col);
  
  if (isNaN(row) || isNaN(col)) {
    console.log("Invalid row/col:", row, col);
    return;
  }
  
  const board = window.currentGrid;
  if (!board) {
    console.log("No board found - currentGrid:", window.currentGrid);
    return;
  }
  
  const value = board[row]?.[col];
  
  if (value === 0 || value === undefined) {
    showToast("Ô trống không thể đổi chỗ!", 'warning');
    return;
  }
  
  console.log("Selected tile:", { row, col, value });
  
  if (firstTile === null) {
    firstTile = { row, col, value };
    cell.style.border = "3px solid #fbbf24";
    showToast("Đã chọn ô đầu tiên. Chọn ô thứ hai để đổi chỗ.", 'info', 2000);
  } else {
    if (firstTile.row === row && firstTile.col === col) {
      showToast("Đã chọn ô này rồi! Chọn ô khác.", 'warning');
      return;
    }
    
    // Reset border of first tile
    const firstCell = document.querySelector(`.tile[data-row="${firstTile.row}"][data-col="${firstTile.col}"]`);
    if (firstCell) firstCell.style.border = "";
    
    performSwap(firstTile.row, firstTile.col, row, col);
    
    // Reset
    swapMode = false;
    btnSwap.classList.remove("active");
    btnSwap.textContent = "🔄 Đổi chỗ 2 ô";
    firstTile = null;
  }
}

// Handle tile click for swap mode (PC)
document.addEventListener("click", function(e) {
  handleTileSelection(e, false);
});

// Handle tile touch for swap mode (Mobile)
// Track touch for swap mode separately
let swapTouchStart = { x: 0, y: 0, time: 0 };
let swapTouchMoved = false;

boardEl.addEventListener("touchstart", function(e) {
  if (!swapMode) return; // Chỉ xử lý trong swap mode
  
  const t = e.touches && e.touches[0];
  if (!t) return;
  
  swapTouchStart.x = t.clientX;
  swapTouchStart.y = t.clientY;
  swapTouchStart.time = Date.now();
  swapTouchMoved = false;
}, { passive: false });

boardEl.addEventListener("touchmove", function(e) {
  if (!swapMode) return;
  
  const t = e.touches && e.touches[0];
  if (!t) return;
  
  const dx = Math.abs(t.clientX - swapTouchStart.x);
  const dy = Math.abs(t.clientY - swapTouchStart.y);
  
  // Nếu di chuyển quá nhiều (>10px), coi như là swipe, không phải tap
  if (dx > 10 || dy > 10) {
    swapTouchMoved = true;
  }
}, { passive: false });

boardEl.addEventListener("touchend", function(e) {
  if (!swapMode) return;
  
  // Chỉ xử lý nếu không phải swipe (tap)
  if (!swapTouchMoved) {
    const t = e.changedTouches && e.changedTouches[0];
    if (t) {
      const touchTime = Date.now() - swapTouchStart.time;
      // Chỉ xử lý tap nếu thời gian < 300ms (tap nhanh)
      if (touchTime < 300) {
        handleTileSelection(e, true);
      }
    }
  }
  
  // Reset
  swapTouchMoved = false;
  swapTouchStart = { x: 0, y: 0, time: 0 };
}, { passive: false });

// Handle ESC to cancel swap mode
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && swapMode) {
    swapMode = false;
    btnSwap.classList.remove("active");
    btnSwap.textContent = "🔄 Đổi chỗ 2 ô";
    firstTile = null;
    showToast("Đã hủy chế độ đổi chỗ.", 'info');
  }
});

async function performSwap(row1, col1, row2, col2) {
  if (inputLocked) return;
  inputLocked = true;
  
  try {
    const res = await fetch("/api/premium/swap", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ row1, col1, row2, col2 })
    });
    
    const data = await res.json();
    
    if (data.ok && data.grid) {
      // Animate swap - hoán đổi vị trí
      const tile1 = document.querySelector(`.tile[data-row="${row1}"][data-col="${col1}"]`);
      const tile2 = document.querySelector(`.tile[data-row="${row2}"][data-col="${col2}"]`);
      
      if (tile1 && tile2) {
        // Get current positions
        const rect1 = tile1.getBoundingClientRect();
        const rect2 = tile2.getBoundingClientRect();
        
        // Calculate movement
        const dx = rect2.left - rect1.left;
        const dy = rect2.top - rect1.top;
        
        // Set initial state
        tile1.style.position = "absolute";
        tile2.style.position = "absolute";
        tile1.style.zIndex = "10";
        tile2.style.zIndex = "10";
        
        // Add animation
        tile1.style.transition = "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)";
        tile2.style.transition = "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)";
        
        // Animate to swap positions
        tile1.style.transform = `translate(${dx}px, ${dy}px) scale(1.1)`;
        tile2.style.transform = `translate(${-dx}px, ${-dy}px) scale(1.1)`;
        
        setTimeout(() => {
          render({ 
            grid: data.grid, 
            score: scoreEl.textContent, 
            moves: movesEl.textContent, 
            new_tiles: [], 
            merged_cells: [] 
          });
          showToast("Đã đổi chỗ thành công!", 'success');
        }, 500);
      } else {
        render({ 
          grid: data.grid, 
          score: scoreEl.textContent, 
          moves: movesEl.textContent, 
          new_tiles: [], 
          merged_cells: [] 
        });
        showToast("Đã đổi chỗ thành công!", 'success');
      }
    } else {
      showToast(data.message || "Không thể đổi chỗ", 'error');
    }
  } catch (e) {
    console.error("Swap error:", e);
    showToast("Có lỗi xảy ra khi đổi chỗ", 'error');
  } finally {
    inputLocked = false;
  }
}

// ================================
// Hamburger Menu đã được xử lý trong mobile_menu.html
// Không cần setup ở đây nữa
// ================================

document.addEventListener("DOMContentLoaded", startGame);
