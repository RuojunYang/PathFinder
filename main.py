import os.path
import tkinter as tk
import time
import random
from tkinter import ttk
import numpy as np


def GUI(name, height, width):
    window = tk.Tk()
    window.title('sudoku')
    # window.geometry('1400x800')
    window.configure(bg='white')

    canvas = tk.Canvas(
        window,
        height=900,
        width=1200,
        bg="#fff"
    )
    canvas.pack()

    start_i = 100
    start_j = 100
    w = 50
    text_lists = []
    rec_lists = []

    for i in range(height):
        rec_list = []
        text_list = []
        for j in range(width):
            rec = canvas.create_rectangle(start_j + j * w, start_i + i * w, start_j + j * w + w, start_i + i * w + w, )
            t = canvas.create_text(start_j + j * w + w / 2, start_i + i * w + w / 2, text='', font=25)
            rec_list.append(rec)
            text_list.append(t)
        text_lists.append(text_list)
        rec_lists.append(rec_list)

    # create maze
    rerun = True
    map_ = np.zeros_like(rec_lists)
    maze_height = int((height + 1) / 2)
    maze_width = int((width + 1) / 2)
    maze_start = (int(maze_height / 2), int(maze_width / 4))
    maze_end = (int(maze_height / 2), int(maze_width / 4 * 3))
    while rerun:

        maze = np.zeros((maze_height, maze_width))

        stack = [maze_start]
        map_[map_ == 0] = 4

        while len(stack) > 0:
            temp = stack[-1]
            maze[temp[0]][temp[1]] = 1

            # print(maze)
            map_[temp[0] * 2][temp[1] * 2] = 0

            temp_list = []
            for each in (
                    (temp[0] + 1, temp[1]), (temp[0] - 1, temp[1]), (temp[0], temp[1] + 1), (temp[0], temp[1] - 1)):
                i = each[0]
                j = each[1]
                if i < 0 or j < 0 or i >= len(maze) or j >= len(maze[0]):
                    continue
                elif maze[i][j] == 0:
                    temp_list.append(each)

            if len(temp_list) == 0:
                stack.remove(temp)
                continue
            # random select
            select = random.randint(0, len(temp_list) - 1)

            if temp[0] == temp_list[select][0]:
                map_[temp[0] * 2][min(temp[1], temp_list[select][1]) * 2 + 1] = 0
            elif temp[1] == temp_list[select][1]:
                map_[min(temp[0], temp_list[select][0]) * 2 + 1][temp[1] * 2] = 0

            stack.append(temp_list[select])

        wall_list = []
        for i in range(len(map_)):
            for j in range(len(map_[0])):
                if map_[i][j] == 4:
                    wall_list.append((i, j))

        for i in range(int(np.sqrt(height * width))):
            temp = random.randint(0, len(wall_list) - 1)
            map_[wall_list[temp][0]][wall_list[temp][1]] = 0
            wall_list.remove(wall_list[temp])

        # no 2*2 space or 2*2 wall
        rerun = False
        for i in range(len(map_) - 1):
            for j in range(len(map_[0]) - 1):
                if map_[i][j] + map_[i + 1][j] + map_[i][j + 1] + map_[i + 1][j + 1] == 0 \
                        or map_[i][j] + map_[i + 1][j] + map_[i][j + 1] + map_[i + 1][j + 1] == 4 * 4:
                    # print(i, j)
                    rerun = True

    for i in range(len(map_)):
        for j in range(len(map_[0])):
            if map_[i][j] == 4:
                canvas.itemconfig(rec_lists[i][j], fill='black')

    start = (maze_start[0] * 2, maze_start[1] * 2)
    end = (maze_end[0] * 2, maze_end[1] * 2)

    map_[start[0]][start[1]] = 1
    map_[end[0]][end[1]] = 2

    canvas.itemconfig(rec_lists[start[0]][start[1]], fill='red')

    canvas.itemconfig(rec_lists[end[0]][end[1]], fill='blue')

    path_method = ['Dijkstra', 'A*']
    path_method = ['Dijkstra']
    box = ttk.Combobox(window, height=3, values=path_method)
    box.set(path_method[0])
    box.place(x=200, y=10)

    button = ttk.Button(window, text='Find Path', command=lambda: click())

    global keep
    keep = None

    def Dijkstra(map, path_list):
        arrive = False

        record = [path_list]
        while len(path_list) > 0:
            path_list_next = []
            for point in path_list:
                for each in [(point[0] - 1, point[1]), (point[0] + 1, point[1]), (point[0], point[1] - 1),
                             (point[0], point[1] + 1)]:
                    i = each[0]
                    j = each[1]

                    if i < 0 or j < 0 or i >= len(map) or j >= len(map[0]):
                        continue

                    if map[i][j] == 0:
                        path_list_next.append((i, j))
                        for rec in record:
                            if rec[-1] == point:
                                temp = rec
                                record.append(temp + [(i, j)])

                        map[i][j] = 3
                    if map[i][j] == 2:
                        for rec in record:
                            if rec[-1] == point:
                                temp = rec
                                record = temp + [(i, j)]
                        arrive = True
                        break
                if arrive:
                    break
                for rec in record:
                    if rec[-1] == point:
                        record.remove(rec)

            path_list = path_list_next
            if arrive:
                break
        return record

    def paint_path(record, i):
        global keep
        if i < len(record) - 1:
            canvas.itemconfig(rec_lists[record[i][0]][record[i][1]], fill='green', stipple='hourglass')
            keep = window.after(300, lambda: paint_path(record, i + 1))
        if i >= len(record) - 1:
            window.after_cancel(keep)

    def update_Dijkstra(map, path_list, map_copy):

        global keep
        arrive = False
        path_list_next = []
        for point in path_list:
            for each in [(point[0] - 1, point[1]), (point[0] + 1, point[1]), (point[0], point[1] - 1),
                         (point[0], point[1] + 1)]:
                i = each[0]
                j = each[1]
                if i < 0 or j < 0 or i >= len(map) or j >= len(map[0]):
                    continue
                if map[i][j] == 0:
                    path_list_next.append((i, j))
                    map[i][j] = 3
                if map[i][j] == 2:
                    arrive = True

        path_list = path_list_next

        for i in range(len(map_)):
            for j in range(len(map_[0])):
                if map_[i][j] == 3:
                    canvas.itemconfig(rec_lists[i][j], fill='orange')

        for each in path_list_next:
            canvas.itemconfig(rec_lists[each[0]][each[1]], fill='yellow')

        if arrive or len(path_list) == 0:
            # print(canvas.itemconfig(rec_lists[0][0]))
            window.after_cancel(keep)
            record = Dijkstra(map_copy, [start])
            paint_path(record, 1)
            return
        keep = window.after(300, lambda: update_Dijkstra(map, path_list, map_copy))

    def get_weighted_map(map):
        map_copy = map.copy()
        weight_map = map.copy()

        for i1 in range(len(map_copy)):
            for j1 in range(len(map_copy[0])):
                if map[i1][j1] == 4:
                    weight_map[i1][j1] = -1
                else:
                    weight_map[i1][j1] = 0

        map_copy = map.copy()

        for i1 in range(len(map_copy)):
            for j1 in range(len(map_copy[0])):

                if weight_map[i1][j1] != 0:
                    continue

                path_list = [(i1, j1)]

                arrive = False
                record = [path_list]
                map = map_copy.copy()
                while len(path_list) > 0:
                    path_list_next = []
                    for point in path_list:
                        for each in [(point[0] - 1, point[1]), (point[0] + 1, point[1]), (point[0], point[1] - 1),
                                     (point[0], point[1] + 1)]:
                            i = each[0]
                            j = each[1]

                            if i < 0 or j < 0 or i >= len(map) or j >= len(map[0]):
                                continue

                            if map[i][j] == 0 or map[i][j] == 2:
                                path_list_next.append((i, j))
                                for rec in record:
                                    if rec[-1] == point:
                                        temp = rec
                                        record.append(temp + [(i, j)])

                                map[i][j] = 3
                            if map[i][j] == 1:
                                for rec in record:
                                    if rec[-1] == point:
                                        temp = rec
                                        record = temp + [(i, j)]
                                arrive = True
                                break
                        if arrive:
                            break
                        for rec in record:
                            if rec[-1] == point:
                                record.remove(rec)

                    path_list = path_list_next
                    if arrive:
                        break
                del map
                for k in range(len(record)):
                    weight_map[record[k][0]][record[k][1]] = len(record) - k - 1

        return weight_map

    def update_A_star(map, dis_dict, map_copy, weighted_map):

        global keep
        vision = 4
        arrive = False
        print(end)
        while len(dis_dict) > 0:
            cur = sorted(dis_dict.items(), key=lambda x: x[1][0] + x[1][1])[0][0]

            temp_dict = {}
            for each in dis_dict.keys():
                if dis_dict[cur][0] + dis_dict[cur][1] == dis_dict[each][0] + dis_dict[each][1]:
                    temp_dict[each] = dis_dict[each]

            cur = sorted(temp_dict.items(), key=lambda x: x[1][0], reverse=True)[0][0]

            for i in range(len(map)):
                for j in range(len(map[0])):
                    if weighted_map[i][j] < dis_dict[cur][0] + vision and weighted_map[i][j] >= 0:
                        if map[i][j] == 0:
                            dis_dict[(i, j)] = [weighted_map[i][j], abs(i - end[0]) + abs(j - end[1])]
                            map[i][j] = 3
                        if map[i][j] == 2:
                            arrive = True
                            break
                    if arrive:
                        break
                if arrive:
                    break
            if arrive:
                break

            print(cur)
            print(sorted(dis_dict.items(), key=lambda x: x[1][0] + x[1][1]))
            print(sorted(temp_dict.items(), key=lambda x: x[1][0], reverse=True))
            print()
            dis_dict.pop(cur)

            canvas.itemconfig(rec_lists[cur[0]][cur[1]], fill='yellow')


        print(dis_dict)

    ## 0 = empty, 1 = start, 2 = end, 3 = walked, 4 = wall
    def click():
        if keep:
            window.after_cancel(keep)
        for i in range(len(map_)):
            for j in range(len(map_[0])):
                if map_[i][j] == 3:
                    canvas.itemconfig(rec_lists[i][j], fill='')
                    map_[i][j] = 0
                if map_[i][j] == 4:
                    canvas.itemconfig(rec_lists[i][j], fill='black')
        # window.after_cancel(None)
        print(path_method[box.current()])
        if path_method[box.current()] == 'Dijkstra':
            update_Dijkstra(map_, [start], map_.copy())
        # elif path_method[box.current()] == 'A*':
        #     path_dic = {}
        #     path_dic[start] = [0, abs(start[0] - end[0]) + abs(start[1] - end[1])]
        #
        #     weighted_map = get_weighted_map(map_.copy())
        #     print(weighted_map)
        #     print(path_dic)
        #     update_A_star(map_, path_dic, map_.copy(), weighted_map)
        else:
            update_Dijkstra(map_, [start], map_.copy())

    button.place(x=700, y=10)

    window.resizable(False, False)

    window.mainloop()


if __name__ == '__main__':
    # (num+1) / 2 has to be odd
    # for map and maze mapping
    # (13+1) % 2 == 1, (21+1) % 2 == 1
    height, width = 13, 21

    GUI('PyCharm', height, width)
