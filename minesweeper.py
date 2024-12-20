from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random
import platform
from datetime import datetime
from tkinter import simpledialog


STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"
def keyin():
    while True:
        x = int(simpledialog.askstring("輸入", "輸入長度:"))
        if x>2 and x<31:
            break
        else:
            tkMessageBox.showwarning("錯誤", "請輸入大於2小於31的數值")
    

    while True:
        y = int(simpledialog.askstring("輸入", "輸入寬度:"))
        if y>2 and y<31:
            break
        else:
            tkMessageBox.showwarning("錯誤", "請輸入大於2小於31的數值")
    while True:
        z = int(simpledialog.askstring("輸入", "輸入地雷數量:"))
        if z>0 and z<x*y/2:
            break
        else:
            tkMessageBox.showwarning("錯誤", "地雷太多或是必須大於0")
    return x,y,z

class Minesweeper:
    stop = False
    def __init__(self, tk, size_x, size_y, num_mines):
        if size_x <= 0 or size_y <= 0 or size_x > 100 or size_y > 100:
            raise ValueError("Board size must be between 1x1 and 100x100.")
        if num_mines <= 0 or num_mines >= size_x * size_y:
            raise ValueError("Number of mines must be between 1 and the total number of tiles - 1.")

        self.size_x = size_x
        self.size_y = size_y
        self.num_mines = num_mines

        # import images
        self.images = {
            "plain": PhotoImage(file="images/tile_plain.gif"),
            "clicked": PhotoImage(file="images/tile_clicked.gif"),
            "mine": PhotoImage(file="images/tile_mine.gif"),
            "flag": PhotoImage(file="images/tile_flag.gif"),
            "wrong": PhotoImage(file="images/tile_wrong.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            self.images["numbers"].append(PhotoImage(file=f"images/tile_{i}.gif"))

        # set up frame
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        # set up labels/UI
        self.labels = {
            "time": Label(self.frame, text="00:00:00"),
            "mines": Label(self.frame, text=f"炸彈數量: {self.num_mines}"),
            "flags": Label(self.frame, text="標誌數量: 0")
        }
        self.labels["time"].grid(row=0, column=0, columnspan=self.size_y)  # top full width
        self.labels["mines"].grid(row=self.size_x + 1, column=0, columnspan=int(self.size_y / 2))  # bottom left
        self.labels["flags"].grid(row=self.size_x + 1, column=int(self.size_y / 2) - 1, columnspan=int(self.size_y / 2))  # bottom right

        self.restart()  # start game
        self.updateTimer()  # init timer

    def setup(self):
        # create flag and clicked tile variables
        self.flagCount = 0
        self.correctFlagCount = 0
        self.clickedCount = 0
        self.startTime = None

        # create buttons
        self.tiles = {}
        self.mines = 0
        mine_positions = set(random.sample(range(self.size_x * self.size_y), self.num_mines))

        for x in range(self.size_x):
            self.tiles[x] = {}
            for y in range(self.size_y):
                id = str(x) + "_" + str(y)
                isMine = (x * self.size_y + y) in mine_positions

                gfx = self.images["plain"]

                tile = {
                    "id": id,
                    "isMine": isMine,
                    "state": STATE_DEFAULT,
                    "coords": {"x": x, "y": y},
                    "button": Button(self.frame, image=gfx),
                    "mines": 0  # calculated after grid is built
                }

                tile["button"].bind(BTN_CLICK, self.onClickWrapper(x, y))
                tile["button"].bind(BTN_FLAG, self.onRightClickWrapper(x, y))
                tile["button"].grid(row=x + 1, column=y)  # offset by 1 row for timer

                self.tiles[x][y] = tile

        # loop again to find nearby mines and display number on tile
        for x in range(self.size_x):
            for y in range(self.size_y):
                mc = 0
                for n in self.getNeighbors(x, y):
                    mc += 1 if n["isMine"] else 0
                self.tiles[x][y]["mines"] = mc

   
    def refreshLabels(self):
        self.labels["flags"].config(text=f"標記數量: {self.flagCount}")
        self.labels["mines"].config(text=f"炸彈數量: {self.num_mines}")

    def gameOver(self, won):
      for x in range(self.size_x):
        for y in range(self.size_y):
            if self.tiles[x][y]["isMine"] == False and self.tiles[x][y]["state"] == STATE_FLAGGED:
                self.tiles[x][y]["button"].config(image=self.images["wrong"])
            if self.tiles[x][y]["isMine"] == True and self.tiles[x][y]["state"] != STATE_FLAGGED:
                self.tiles[x][y]["button"].config(image=self.images["mine"])

      self.tk.update()
      self.stop = True
      print("stop")
      msg = "你贏了! 還玩不?" if won else "你輸了! 還玩不?"
      res = tkMessageBox.askyesno("Game Over", msg)
      self.tk.destroy()  # 關閉當前視窗
      
      if res:
        # 在此重新詢問用戶輸入遊戲參數
        size_x,size_y,num_mines = keyin()
        
        # 關閉當前視窗
        
        
        # 重新創建新的 Tk 視窗
        new_window = Tk()
        new_window.title("Minesweeper")
        
        # 重新創建 Minesweeper 實例
        minesweeper = Minesweeper(new_window, size_x, size_y, num_mines)
        self.stop = False
        new_window.mainloop()
      else:
        self.tk.destroy()
        self.tk.quit()

    def restart(self, size_x=None, size_y=None, num_mines=None):
    # 如果有新參數，使用新的遊戲設置
     if size_x and size_y and num_mines:
        self.size_x = size_x
        self.size_y = size_y
        self.num_mines = num_mines
     self.setup()  # 初始化遊戲
     self.refreshLabels()


    def updateTimer(self):
        ts = "00:00:00"
        if self.startTime:
            delta = datetime.now() - self.startTime
            ts = str(delta).split('.')[0]  # drop ms
            if delta.total_seconds() < 36000:
                ts = "0" + ts  # zero-pad
        self.labels["time"].config(text=ts)
        if self.stop==False:
            self.frame.after(100, self.updateTimer)

    def getNeighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x - 1, "y": y - 1},
            {"x": x - 1, "y": y},
            {"x": x - 1, "y": y + 1},
            {"x": x, "y": y - 1},
            {"x": x, "y": y + 1},
            {"x": x + 1, "y": y - 1},
            {"x": x + 1, "y": y},
            {"x": x + 1, "y": y + 1},
        ]
        for n in coords:
            try:
                neighbors.append(self.tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbors

    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])

    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])

    def onClick(self, tile):
        if self.startTime is None:
            self.startTime = datetime.now()

        if tile["isMine"]:
            self.gameOver(False)
            return

        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            self.clearSurroundingTiles(tile["id"])
        else:
            tile["button"].config(image=self.images["numbers"][tile["mines"] - 1])

        if tile["state"] != STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            self.clickedCount += 1
        if self.clickedCount == (self.size_x * self.size_y) - self.num_mines:
            self.gameOver(True)

    def onRightClick(self, tile):
        if self.startTime is None:
            self.startTime = datetime.now()

        if tile["state"] == STATE_DEFAULT:
            tile["button"].config(image=self.images["flag"])
            tile["state"] = STATE_FLAGGED
            tile["button"].unbind(BTN_CLICK)
            if tile["isMine"]:
                self.correctFlagCount += 1
            self.flagCount += 1
            self.refreshLabels()
        elif tile["state"] == STATE_FLAGGED:
            tile["button"].config(image=self.images["plain"])
            tile["state"] = STATE_DEFAULT
            tile["button"].bind(BTN_CLICK, self.onClickWrapper(tile["coords"]["x"], tile["coords"]["y"]))
            if tile["isMine"]:
                self.correctFlagCount -= 1
            self.flagCount -= 1
            self.refreshLabels()

    def clearSurroundingTiles(self, id):
        queue = deque([id])

        while queue:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.getNeighbors(x, y):
                self.clearTile(tile, queue)

    def clearTile(self, tile, queue):
        if tile["state"] != STATE_DEFAULT:
            return

        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            queue.append(tile["id"])
        else:
            tile["button"].config(image=self.images["numbers"][tile["mines"] - 1])

        tile["state"] = STATE_CLICKED
        self.clickedCount += 1

### END OF CLASSES ###

def main():
    size_x,size_y,num_mines = keyin()

    window = Tk()
    window.title("Minesweeper")
    try:
        minesweeper = Minesweeper(window, size_x, size_y, num_mines)
        window.mainloop()
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()