import random
import copy

class Game2048:
    def __init__(self, size=4):
        self.size = size
        self.grid = self.empty_grid()
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.last_state = None
        self.best = 0  

    def empty_grid(self):
        """Tạo lưới rỗng kích thước size x size."""
        return [[0] * self.size for _ in range(self.size)]

    def random_empty_cell(self):
        """Tìm ô trống ngẫu nhiên."""
        empties = [(r, c) for r in range(self.size) for c in range(self.size) if self.grid[r][c] == 0]
        return random.choice(empties) if empties else None

    def add_random_tile(self):
        """Thêm ô mới (2 hoặc 4) vào vị trí ngẫu nhiên."""
        cell = self.random_empty_cell()
        if not cell:
            return None
        r, c = cell
        self.grid[r][c] = 2 if random.random() < 0.9 else 4
        return {"r": r, "c": c}

    def setup(self):
        """Khởi tạo trò chơi mới."""
        self.grid = self.empty_grid()
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.last_state = None
  
        new_tiles = [self.add_random_tile(), self.add_random_tile()]
        new_tiles = [tile for tile in new_tiles if tile]
        return {"grid": self.grid, "score": self.score, "moves": self.moves, "new_tiles": new_tiles}

    def compress(self, row):
        """Nén hàng, loại bỏ các số 0 và đẩy các số khác về một phía."""
        arr = [v for v in row if v != 0]
        return arr + [0] * (self.size - len(arr))

    def merge(self, row):
        """Gộp các ô giống nhau trong hàng."""
        merged_cells = []
        new_row = row[:]
        for i in range(self.size - 1):
            if new_row[i] != 0 and new_row[i] == new_row[i + 1]:
                new_row[i] *= 2
                self.score += new_row[i]
                new_row[i + 1] = 0
                merged_cells.append(i)
        return {"new_row": new_row, "merged_indices": merged_cells}

    def transpose(self, grid):
        """Chuyển vị ma trận."""
        return [[grid[r][c] for r in range(self.size)] for c in range(self.size)]

    def reverse_rows(self, grid):
        """Đảo ngược các hàng."""
        return [row[::-1] for row in grid]

    def operate(self, row):
        """Thực hiện nén và gộp hàng."""
        compressed = self.compress(row)
        merged = self.merge(compressed)
        final_row = self.compress(merged["new_row"])
        return {"result": final_row, "merged": merged["merged_indices"]}

    def move(self, direction):
        """Xử lý di chuyển theo hướng (up, down, left, right)."""
        if self.game_over:
            return {"changed": False}

    
        self.last_state = {
            "grid": copy.deepcopy(self.grid),
            "score": self.score,
            "moves": self.moves
        }

        temp_grid = copy.deepcopy(self.grid)
        changed = False
        merged_cells = []

        if direction in ("up", "down"):
            temp_grid = self.transpose(temp_grid)
        if direction in ("right", "down"):
            temp_grid = self.reverse_rows(temp_grid)

        for r in range(self.size):
            original_row = temp_grid[r][:]
            result = self.operate(temp_grid[r])
            temp_grid[r] = result["result"]
            if original_row != result["result"]:
                changed = True
            for c in result["merged"]:
                actual_col = self.size - 1 - c if direction in ("right", "down") else c
                actual_row = r
                if direction in ("up", "down"):
                    merged_cells.append({"r": actual_col, "c": actual_row})
                else:
                    merged_cells.append({"r": actual_row, "c": actual_col})

      
        if direction in ("right", "down"):
            temp_grid = self.reverse_rows(temp_grid)
        if direction in ("up", "down"):
            temp_grid = self.transpose(temp_grid)

        if not changed:
            self.last_state = None
            return {"grid": self.grid, "score": self.score, "moves": self.moves, "changed": False, "merged_cells": []}

        self.grid = temp_grid
        self.moves += 1
        new_tile = self.add_random_tile()

        return {
            "grid": self.grid,
            "score": self.score,
            "moves": self.moves,
            "changed": True,
            "new_tile": [new_tile] if new_tile else [],
            "merged_cells": merged_cells
        }

    def any_moves_left(self):
        """Kiểm tra xem còn nước đi nào không."""
      
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 0:
                    return True
  
        for r in range(self.size):
            for c in range(self.size - 1):
                if self.grid[r][c] == self.grid[r][c + 1]:
                    return True
        for c in range(self.size):
            for r in range(self.size - 1):
                if self.grid[r][c] == self.grid[r + 1][c]:
                    return True
        return False

    def max_tile(self):
        """Tìm ô có giá trị lớn nhất."""
        return max(max(row) for row in self.grid)

    def undo(self):
        """Hoàn tác nước đi trước."""
        if not self.last_state:
            return {"grid": self.grid, "score": self.score, "moves": self.moves}
        self.grid = copy.deepcopy(self.last_state["grid"])
        self.score = self.last_state["score"]
        self.moves = self.last_state["moves"]
        self.game_over = False
        self.last_state = None
        return {"grid": self.grid, "score": self.score, "moves": self.moves}

    def check_game_over(self):
        """Kiểm tra trạng thái game over."""
        if not self.any_moves_left():
            self.game_over = True
            return {"score": self.score, "max_tile": self.max_tile(), "moves": self.moves}
        return None

    def get_hint(self):
        """Gợi ý nước đi tốt nhất (premium feature)"""
        for direction in ["left", "right", "up", "down"]:
            test_grid = copy.deepcopy(self.grid)
            test_score = self.score
            
            # Simulate move
            temp_grid = copy.deepcopy(test_grid)
            changed = False
            
            if direction in ("up", "down"):
                temp_grid = self.transpose(temp_grid)
            if direction in ("right", "down"):
                temp_grid = self.reverse_rows(temp_grid)
            
            for r in range(self.size):
                original_row = temp_grid[r][:]
                result = self.operate(temp_grid[r])
                temp_grid[r] = result["result"]
                if original_row != result["result"]:
                    changed = True
            
            if direction in ("right", "down"):
                temp_grid = self.reverse_rows(temp_grid)
            if direction in ("up", "down"):
                temp_grid = self.transpose(temp_grid)
            
            if changed:
                return {"direction": direction}
        
        return None

    def shuffle(self):
        """Xáo trộn các ô trên bàn cờ (premium feature)"""
        all_tiles = []
        
        # Thu thập tất cả giá trị khác 0
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != 0:
                    all_tiles.append(self.grid[r][c])
        
        # Xáo trộn danh sách
        random.shuffle(all_tiles)
        
        # Đặt lại vào grid
        idx = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != 0:
                    self.grid[r][c] = all_tiles[idx]
                    idx += 1
        
        return {"grid": self.grid}

    def swap_two_tiles(self, row1, col1, row2, col2):
        """Hoán đổi vị trí 2 ô (premium feature)"""
        # Kiểm tra tính hợp lệ của vị trí
        if not (0 <= row1 < self.size and 0 <= col1 < self.size and
                0 <= row2 < self.size and 0 <= col2 < self.size):
            return {"ok": False, "message": "Vị trí không hợp lệ"}
        
        # Không thể đổi chỗ 2 ô giống nhau
        if row1 == row2 and col1 == col2:
            return {"ok": False, "message": "Không thể đổi chỗ ô với chính nó"}
        
        # Không thể đổi chỗ ô trống
        if self.grid[row1][col1] == 0 or self.grid[row2][col2] == 0:
            return {"ok": False, "message": "Không thể đổi chỗ ô trống"}
        
        # Thực hiện đổi chỗ
        temp = self.grid[row1][col1]
        self.grid[row1][col1] = self.grid[row2][col2]
        self.grid[row2][col2] = temp
        
        return {
            "ok": True,
            "grid": self.grid,
            "tile1": {"row": row1, "col": col1, "value": self.grid[row1][col1]},
            "tile2": {"row": row2, "col": col2, "value": self.grid[row2][col2]}
        } 