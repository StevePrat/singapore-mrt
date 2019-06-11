import json
import time

with open("mrt_graph.json") as f:
    graph = json.load(f)

def get_node(graph,name=None,code=None):
    if name:
        for node in graph:
            if node['name'] == name:
                return node
        return None
    
    if code:
        for node in graph:
            if code in node['codes']:
                return node
        return None

def get_line(graph,code):
    return [node for node in graph if code in node['lines']]

def find_fewest_stations_path(graph,start_code='',end_code='',start_name='',end_name='',path=[]):
    if start_code:
        start_node = get_node(graph,code=start_code)
    if end_code:
        end_node = get_node(graph,code=end_code)
    if start_name:
        start_node = get_node(graph,name=start_name)
    if end_name:
        end_node = get_node(graph,name=end_name)

    if start_node and end_node:
        pass
    else:
        return None

    path = path + [start_node]
    
    if start_node == end_node:
        return path
    
    shortest = None
    neighbours = [get_node(graph,code=neighbour_code) for neighbour_code in start_node['neighbours']]
    for node in neighbours:
        if node in graph:
            if node not in path:
                new_path = find_fewest_stations_path(graph,start_name=node['name'],end_name=end_name,path=path)
                if new_path:
                    if not shortest or len(new_path) < len(shortest):
                        shortest = new_path
    
    return shortest

def get_interchanges(graph,include_lines=[],exclude_lines=[]):
    interchanges = [node for node in graph if len(node['lines'])>1]
    if not (include_lines or exclude_lines):
        return interchanges
    
    if include_lines and exclude_lines:
        selector = set(include_lines) - set(exclude_lines)
    elif include_lines:
        selector = include_lines
    elif exclude_lines:
        all_line_codes = {line for node in graph for line in node['lines']}
        selector = all_line_codes - set(exclude_lines)
    
    return [node for node in interchanges if set(node['lines']) & selector]

def find_fewest_transfers_path(graph,start_code='',end_code='',start_name='',end_name='',path=[],exclude_lines=[]):
    if start_code:
        start_node = get_node(graph,code=start_code)
    if end_code:
        end_node = get_node(graph,code=end_code)
    if start_name:
        start_node = get_node(graph,name=start_name)
    if end_name:
        end_node = get_node(graph,name=end_name)

    print('Starting station:', start_name)
    print('Destination station:', end_name)
    print('Excluded lines:',exclude_lines)

    start_line_codes = set(start_node['lines']) - set(exclude_lines)
    target_line_codes = set(end_node['lines']) - set(exclude_lines)

    common_line = set(start_line_codes) & set(target_line_codes)
    if common_line:
        print('Common line between',start_name,'and',end_name,':',common_line)
        shortest = []
        for line_code in common_line:
            line = get_line(graph,line_code)
            new_path = find_fewest_stations_path(line,start_name=start_node['name'],end_name=end_node['name'],path=path)
            if not shortest or len(new_path)<len(shortest):
                shortest = new_path

        return shortest
    
    else:
        fewest = []
        for start_line_code in start_line_codes:
            if start_line_code:
                start_line = get_line(graph,start_line_code)
                start_line_interchanges = get_interchanges(start_line,exclude_lines=exclude_lines)
                for node in start_line_interchanges:
                    print('Current node:',node['name'])
                    partial_path = find_fewest_stations_path(start_line,start_name=start_node['name'],end_name=node['name'],path=path)
                    if partial_path:
                        print('Partial path:',path_to_string(partial_path))
                        new_path = find_fewest_transfers_path(graph,start_name=node['name'],end_name=end_node['name'],exclude_lines=exclude_lines+[start_line_code],path=partial_path[:-1])
                        print('New path:',path_to_string(new_path))
                        if not fewest or calc_transfers(new_path)<=calc_transfers(fewest):
                            if not fewest or len(new_path)<len(fewest):
                                fewest = new_path
                                print("Current fewest:",path_to_string(fewest))
        return fewest

def calc_transfers(path):
    if len(path) < 2:
        return 0

    current_line = set(path[0]['lines'])
    transfers = 0
    for node in path:
        current_line = current_line & set(node['lines'])
        if not current_line:
            current_line = set(node['lines'])
            transfers += 1
    
    return transfers

def path_to_string(path):
    return '-->'.join([node['name'] for node in path])