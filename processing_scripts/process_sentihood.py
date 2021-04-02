import json
import os


def process(file):
    with open(file) as o:
        data = json.load(o)
    #
    processed = []
    #
    for sent in data:
        new = {}
        new["idx"] = sent["id"]
        new["text"] = sent["text"]
        opinions = sent["opinions"]
        new["opinions"] = []
        # Keep only examples with opinion annotations
        if opinions != []:
            for op in opinions:
                new_op = {}
                new_op["holder"] = None
                target_entity = op["target_entity"]
                offset1 = new["text"].find(target_entity)
                offset2 = offset1 + len(target_entity)
                new_op["target"] = [target_entity, "{0}:{1}".format(offset1, offset2)]
                new_op["expression"] = None
                new_op["label"] = op["sentiment"].lower()
                new_op["intensity"] = "normal"
        #
                new["opinions"].append(new_op)
        #
            processed.append(new)
        else:
            pass
    #
    return processed

if __name__ == "__main__":

    sentihood_dir = "../sentihood/data/sentihood"

    files = ["sentihood-train.json",
             "sentihood-dev.json",
             "sentihood-test.json"]

    for file in files:
        p = process(os.path.join(sentihood_dir, file))
        os.makedirs(os.path.join("../processed", "sentihood"), exist_ok=True)
        with open(os.path.join("../processed", "sentihood", file), "w") as out:
            json.dump(p, out)
