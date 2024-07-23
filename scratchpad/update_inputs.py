import csv

with open("data/inputs.csv", "r") as input_file:
    with open("data/inputs_new.csv", "w") as output_file:
        r = csv.reader(input_file)
        w = csv.writer(output_file)
        all = []
        row0 = next(r)
        row0.append("Ticks")
        all.append(row0)
        for item in r:
            item.append(500)
            all.append(item)
        w.writerows(all)
