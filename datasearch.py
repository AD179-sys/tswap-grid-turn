import os
import sys
import random
import matplotlib.pyplot as plt
import numpy as np

def get_initial_goal_positions(mname):
    with open("./map/" + mname, 'r') as f:
        lines = f.readlines()
    
    height = -1
    width = -1
    for line in lines:
        if 'height' in line:
            height = int(line.split()[1])
        if 'width' in line:
            width = int(line.split()[1])
        if height != -1 and width != -1:
            break
    
    map_start = lines.index("map\n") + 1
    
    igp = []
    for y in range(height):
        line = lines[map_start + y].strip()
        for x in range(width):
            if line[x] == '.':
                igp.append((x, y, random.randint(0, 1)))
    
    return igp, height, width

if len(sys.argv) != 6:
    raise ValueError("invalid number of arguments")

mname, beg, end, step, cnt_runs = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])

if end == "inf":
    end = 10**100
else:
    end = int(end)

is_valid = False
valid_names = ["arena.map", "100x100.map", "lak503d.map", "den520d.map", "random512-20-0.map"]
for s in valid_names:
    if mname == s:
        is_valid = True

names = [mname]
if mname == 'all':
    is_valid = True
    names = valid_names

if not is_valid:
    raise ValueError("invalid name of map")

if beg >= end:
    raise ValueError("invalid bounds(end more then begin)")

if step <= 0 or beg <= 0:
    raise ValueError("step and begin should be a possitive number")

for mname in names:
    table = []
    success = 0
    cnt = 0


    x_cnt_agents = np.arange(beg, end, step)
    y_makespan = np.zeros((end - beg - 1) // step + 1)
    y_flowtime = np.zeros((end - beg - 1) // step + 1)
    y_comptime = np.zeros((end - beg - 1) // step + 1)
    cnt_success = np.zeros((end - beg - 1) // step + 1)



    for num_run in range(cnt_runs):
        pos, height, width = get_initial_goal_positions(mname)
        random.shuffle(pos)

        ind_agnts = -1

        for cnt_agents in range(beg, end, step):
            ind_agnts += 1

            if 2 * cnt_agents > len(pos):
                print("overflow place. Break earlier")
                break

            # this version is not optimal
            with open("cur_map.txt", "w") as f:
                f.write("map_file="+mname+"\n")
                f.write("agents="+str(cnt_agents)+"\n")
                f.write("seed=1\n")
                f.write("random_problem=0\n")
                f.write("max_timestep=1000\n")
                f.write("max_comp_time=5000\n")

                for j in range(cnt_agents):
                    f.write(str(pos[j][0]) + "," + str(pos[j][1]) + "," + str(pos[j][2]) + ",")
                    f.write(str(pos[len(pos) - 1 - j][0]) + "," + str(pos[len(pos) - 1 - j][1]) + "," +
                            str(pos[len(pos) - 1 - j][2]) + "\n")
            
            result_of_work = os.system("./build/app -i cur_map.txt -s TSWAPTurns -o ./build/result.txt -v")

            assert(result_of_work == 0)

            print()
            print()
            print()

            positions = [[-1, 0] for _ in range(cnt_agents)]
            makespan_item = -1
            flowtime_item = -1

            is_solved = 0
            comp_time = 0
            with open("./build/result.txt", "r") as f:
                for line in f:
                    if 'solved=' in line:
                        is_solved = int(line[-2:-1])
                    if 'comp_time=' in line:
                        comp_time = int(line[10:-1])
                    
                    if ":" in line:
                        makespan_item += 1

                        state = 0
                        not_parse_str = ""
                        ind = 0
                        for c in line:
                            if c == '(':
                                state = 1
                                not_parse_str = ""
                            elif c == ')':
                                x, y, t = not_parse_str.split(',')
                                state = 0
                                if positions[ind][0] == (x + y * width) * 2 + t:
                                    positions[ind][1] += 1
                                else:
                                    positions[ind] = [(x + y * width) * 2 + t, 1]
                                ind += 1
                            elif state == 1:
                                not_parse_str += c
                    
            
            flowtime_item = cnt_agents * makespan_item

            for _, eq in positions:
                flowtime_item -= (eq - 1)

            if is_solved:
                y_makespan[ind_agnts] += makespan_item
                y_flowtime[ind_agnts] += flowtime_item
                y_comptime[ind_agnts] += comp_time
                cnt_success[ind_agnts] += 1
                success += 1
            cnt += 1

    plt.plot(x_cnt_agents, y_makespan / cnt_success)
    plt.title(f'Makespan for {mname} map for N agents(with success rate {success / cnt:.0%})')
    plt.xlabel("cnt_agents")
    plt.ylabel("makespan")
    plt.savefig(f"./build/makespan_{mname[:-4]}.png") #[:-4]need for deleting .map

    plt.clf()

    plt.plot(x_cnt_agents, y_flowtime / cnt_success)
    plt.title(f'Flowtime for {mname} map for N agents(with success rate {success / cnt:.0%})')
    plt.xlabel("cnt_agents")
    plt.ylabel("flowtime")
    plt.savefig(f"./build/flowtime_{mname[:-4]}.png") #[:-4]need for deleting .map

    plt.clf()

    plt.plot(x_cnt_agents, y_comptime / cnt_success)
    plt.title(f'Comptime for {mname} map for N agents(with success rate {success / cnt:.0%})')
    plt.xlabel("cnt_agents")
    plt.ylabel("comptime(ms)")
    plt.savefig(f"./build/comptime_{mname[:-4]}.png") #[:-4]need for deleting .map

    plt.clf()
    '''
    with open("./build/test_data.txt", "w") as f:
        f.write("[")
        for x, y in table:
            f.write("[" + str(x) + ", " + str(y) +" ],\n")
        f.write("]")
    '''