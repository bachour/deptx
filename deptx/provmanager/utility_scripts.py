import json
import random
import string

from deptx.settings import MEDIA_ROOT

RANDOM_FILES_PATH = MEDIA_ROOT + "GRINDING/"

# takes a json for a graph with randomizable content, randomizes all values in the graph, randomly chooses one set
# of critical values and makes at least one of them different from the others. adds question mark before all these values
# returns the resulting graph as a json object
def get_random_graph(graph):
    identifiers = {}
    duplicate_count = 0
    triplicate_count = 0
    
    #first collect all identifiers and assign random values to them from their respective source files
    for c in graph: #node class
        if c == 'prefix':
            continue
        for e in graph[c]: #individual elements
            for a in graph[c][e]:
                if graph[c][e][a][0] == '$':
                    values = graph[c][e][a].split()
                    file = values[0][1:]
                    id = values[1]
                    if not identifiers.has_key(id):
                        identifiers[id] = []
                        identifiers[id].append(get_random_from_file(RANDOM_FILES_PATH + file + ".txt", identifiers[id]))
                    elif len(identifiers[id]) == 1:
                        identifiers[id].append(get_random_from_file(RANDOM_FILES_PATH + file + ".txt", identifiers[id]))
                        duplicate_count += 1
                    else:
                        identifiers[id].append(identifiers[id][random.randint(0,1)])
                        triplicate_count += 1
                        
    #make duplicate_count a random number between 0 and duplicate_count
    duplicate_count = duplicate_count - random.randint(1,duplicate_count)
                 
    #choose duplicate_countTH duplicated identifier, and add ?'s to it's value           
    for i in identifiers:
        if len(identifiers[i]) >= 2:
            if (duplicate_count == 0):
                #print 'selected ',i, ': ', identifiers[i]
                for j in range(len(identifiers[i])):
                    identifiers[i][j] = '?' + identifiers[i][j]
            else:
                #choose one of the values and place it everywhere
                selected = identifiers[i][random.randint(1, len(identifiers[i]))]
                for j in range(len(identifiers[i])):
                    identifiers[i][j] = selected
            duplicate_count -= 1
    
    #replace every element in the graph with an element from the randomly generated list
    for c in graph: #node class
        if c == 'prefix':
            continue
        for e in graph[c]: #individual elements
            for a in graph[c][e]:
                if graph[c][e][a][0] == '$':
                    values = graph[c][e][a].split()
                    id = values[1]
                    graph[c][e][a] = identifiers[id].pop(0)
        
    return graph


# searches the graph for ? attribute, creates 2 lists of node, attribute pairs corresponding to the sets of attribtue values that should
# be consistent but arent. then returns the two lists, as well as the modified graph (without the question marks) as a json object
def get_inconsistencies(graph):
    
    criticals = {}
    
    for c in graph: #node class
        if c == 'prefix':
            continue
        for e in graph[c]: #individual elements
            for a in graph[c][e]:
                if graph[c][e][a][0] == '?':
                    if not criticals.has_key(graph[c][e][a]):
                        criticals[graph[c][e][a]] = []
                    criticals[graph[c][e][a]].append({"node":e,"attribute":a})
                    graph[c][e][a] = graph[c][e][a][1:]
                    
    lists = []
    for a in criticals:
        lists.append(criticals[a])
        
    return lists, graph

# internal use function:
# returns a random line from file that is not found in the list not_in
# returns None if no such line exists
def get_random_from_file(file, not_in):
    afile = open(file, 'U')
    lines = []
    
    line = None
    
    for line in afile.readlines():
        line = filter(lambda x: x in string.printable, line).strip()
        if line in not_in or len(line) < 1:
            continue
        lines.append(line)
        
        
    return lines[random.randint(0, len(lines)-1)].strip()
