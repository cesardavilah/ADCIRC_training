from itertools import islice

def read_elevations(filename):
    with open(filename, 'r') as file:
        elevations = []
        for line in islice(file, 1, 2):
            _, numberofnodes = line.split()
        for line in islice(file, 0, int(numberofnodes)):
            id, _,_, elev = line.split()
            elevations.append([id, elev])
        return elevations, numberofnodes

def read_levels(filename):
    input = []
    with open(filename, 'r') as file:
        for line in file:
            if (len(line.split()) != 2):
                continue
            # print(line.split())
            elev, mann = line.split()
            input.append([elev, mann])
    return input

def elevation_helper(elevation, input):
    for k in range(len(input)):
        if k == 0:
            if float(elevation) <= float(input[k][0]):
                return input[k][1]
        else:
            if float(input[k][0]) >= float(elevation) > float(input[k - 1][0]):
                return input[k][1]

def assign_mann(elev, input):
    out = []
    for node, elevation in elev:
        if (elevation_helper(elevation, input)) == None:
            continue
        else:
            out.append([node, elevation_helper(elevation, input)])
    return out

def write_fort13(out, numberofnodes):
    with open('fort.13', 'w') as file:
        file.write('Spatial attributes description\n')
        file.write(str(numberofnodes)+'\n')
        file.write('1\n')
        file.write('mannings_n_at_sea_floor\n')
        file.write(' m\n 1\n 0.0200000\n')
        file.write('mannings_n_at_sea_floor\n')
        file.write(' '+str(len(out))+'\n')
        towrite = ''
        for node, mann in out:
            mann = float("{:0.7f}".format(float(mann)))
            towrite += ' '+node+' '+"%.7f" % mann+'\n'
        file.write(towrite)


elev, numberofnodes = read_elevations('fort.14')

input = read_levels('levels')

out = assign_mann(elev, input)

write_fort13(out, numberofnodes)

