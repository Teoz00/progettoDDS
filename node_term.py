import sys

def parse_neighbors(args):
    neighbors = []
    current_dict = {}
    key = None
    
    for arg in args:
        if arg.endswith(":"):
            if key is not None and current_dict:
                neighbors.append(current_dict)
                current_dict = {}
            key = arg[:-1]
        else:
            try:
                value = int(arg)
            except ValueError:
                value = arg

            if key:
                current_dict[key] = value
                key = None

    if current_dict:
        neighbors.append(current_dict)

    for elem in neighbors:
        print(elem)

    return neighbors

if __name__ == "__main__":
    if len(sys.argv) > 1:
        node_id = int(sys.argv[1])
        my_addr = sys.argv[2]
        
        neighbors_args = sys.argv[3:]
        
        # print("neighbors_args:", neighbors_args, "\n")
        
        # i = 0
        # for elem in sys.argv:
        #     print(f"sys.argv[{i}]: {elem}")
        #     i += 1
        
        neighbors = parse_neighbors(neighbors_args)
        
        print("\nneighbors_parsed:", neighbors)
        