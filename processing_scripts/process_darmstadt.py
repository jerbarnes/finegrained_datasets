from lxml import etree
from lxml.etree import fromstring
import os
import json

parser = etree.XMLParser(recover=True, encoding='utf8')

def expand_span(span):
    if "," in span:
        spans = span.split(",")
        new_span = []
        for sp in spans:
            if ".." in sp:
                off1, off2 = sp.split("..")
                off1 = int(off1.split("_")[-1])
                off2 = int(off2.split("_")[-1])
                r = list(range(off1, off2+1))
                new_span.extend(["word_" + str(i) for i in r])
            else:
                new_span.extend([sp])
        return new_span
    #
    elif ".." in span:
        off1, off2 = span.split("..")
        off1 = int(off1.split("_")[-1])
        off2 = int(off2.split("_")[-1])
        r = list(range(off1, off2+1))
        span = ["word_" + str(i) for i in r]
    else:
        span = [span]
    return span


def get_sents(sent_file):
    mark_xml = open(sent_file).read().encode('utf8')
    mark_root = fromstring(mark_xml, parser)
    #
    sents = []
    #
    for i in mark_root:
        sent_span = i.get("span")
        sent_span = expand_span(sent_span)
        sents.append(sent_span)
    return sents

# polarity_flip_dict = {"positive": "negative",
#                           "negative": "positive"}

# increase_strength_dict = {"average": "strong"}

# for i in mark_root:
#     if i.get("annotation_type") == "opinionexpression":
#         polarity = i.get("polarity")
#         modifier = i.get("opinionmodifier")
#         strength = i.get("strength")
#         span = i.get("span")
#         span = expand_span(span)
#         if modifier != "empty":
#             modifier = markups[modifier]
#             change = modifier.get("modifier")
#             mspan = modifier.get("span")
#             mspan = expand_span(mspan)
#             span.extend(mspan)
#             print(span)
#             toks = " ".join([tokens[i] for i in span])
#             print(toks)
#             if change == "negation":
#                 new_polarity = polarity_flip_dict[polarity]
#                 #print(change)
#                 print(new_polarity)
#                 print(strength)
#             elif change == "increase":
#                 new_strength = increase_strength_dict[strength]
#                 print(polarity)
#                 print(new_strength)
#             else:
#                 print(change)
#         else:
#             toks = " ".join([tokens[i] for i in span])
#             print(toks)
#             print(polarity)
#             print(strength)
#         print("---" * 10)
#     elif i.get("annotation_type") == "polar_target":
#         span = i.get("span")
#         span = expand_span(span)
#         toks = " ".join([tokens[i] for i in span])
#         label = i.get("polar_target_polarity")
#         print("POLAR TARGET")
#         print(toks)
#         print(label)
#         print("---" * 10)


def get_opinions(base_file, markable_file):

    polarity_flip_dict = {"positive": "negative",
                          "negative": "positive",
                          "neutral": "negative"}

    increase_strength_dict = {"average": "strong",
                              "weak": "average",
                              "strong": "strong"}

    decrease_strength_dict = {"average": "weak",
                              "weak": "weak",
                              "strong": "average"}

    new = {}
    new["idx"] = base_file.split("/")[-1][:-10]

    base_xml = open(base_file).read().encode('utf8')
    mark_xml = open(markable_file).read().encode('utf8')

    base_root = fromstring(base_xml, parser)
    mark_root = fromstring(mark_xml, parser)

    tokens = {}
    spans = {}
    markups = {}

    text = ""
    span_idx = 0

    for i in base_root:
        idx = i.get("id")
        token = i.text
        tokens[idx] = token
        text += token + " "
        begin_span = span_idx
        end_span = span_idx + len(token)
        spans[idx] = (begin_span, end_span)
        span_idx += len(token) + 1

    for i in mark_root:
        idx = i.get("id")
        markups[idx] = i

    opinions = []

    for m in markups.values():
        if m.get("annotation_type") == "opinionexpression":
            idx = m.get("id")
            #print(idx)
            hspan = m.get("opinionholder")
            exp_span = m.get("span")
            tspan = m.get("opiniontarget")
            label = m.get("polarity")
            modifier = m.get("opinionmodifier")
            intensity = m.get("strength")

            # Collect opion holder: text and spans
            if hspan == "empty":
                holder = None
            elif hspan is None:
                holder = None
            elif ";" in hspan:
                #print(hspan) # only one example of multiple holders
                hspan = hspan.split(";")[0]
                holder_span = markups[hspan].get("span")
                holder_span = expand_span(holder_span)
                holder_tokens = " ".join([tokens[i] for i in holder_span])
                hld_off1 = spans[holder_span[0]][0]
                hld_off2 = spans[holder_span[-1]][1]
                #hld_off1 = text.find(holder_tokens)
                #hld_off2 = hld_off1 + len(holder_tokens)
                holder = [holder_tokens, "{0}:{1}".format(hld_off1, hld_off2)]
            else:
                holder_span = markups[hspan].get("span")
                holder_span = expand_span(holder_span)
                holder_tokens = " ".join([tokens[i] for i in holder_span])
                hld_off1 = spans[holder_span[0]][0]
                hld_off2 = spans[holder_span[-1]][1]
                #hld_off1 = text.find(holder_tokens)
                #hld_off2 = hld_off1 + len(holder_tokens)
                holder = [holder_tokens, "{0}:{1}".format(hld_off1, hld_off2)]

            # deal with any modified expressions
            # these may change the polarity (negation), intensity (increase)
            # additionally, the offsets for the expressions will need to be updated
            if modifier != "empty" and modifier is not None:
                if ";" in modifier:
                    mod_tokens = ""
                    mod_offs = ""
                    modifiers = modifier.split(";")
                    for modifier in modifiers:
                        modifier = markups[modifier]
                        change = modifier.get("modifier")
                        modifier_span = modifier.get("span")
                        modifier_span = expand_span(modifier_span)
                        mod_toks = " ".join([tokens[i] for i in modifier_span])
                        mod_off1 = spans[modifier_span[0]][0]
                        mod_off2 = spans[modifier_span[-1]][1]
                        #mod_off1 = text.find(mod_tokens)
                        #mod_off2 = mod_off1 + len(mod_tokens)

                        mod_tokens += mod_toks + ";"
                        offs = "{0}:{1}".format(mod_off1, mod_off2)
                        mod_offs += offs + ";"

                        if change == "negation":
                            label = polarity_flip_dict[label]
                        elif change == "increase":
                            intensity = increase_strength_dict[intensity]
                        elif change == "decrease":
                            intensity = decrease_strength_dict[intensity]
                        else:
                            pass
                            #print(change)

                    # remove trailing semicolons
                    mod_offs = mod_offs[:-1]
                    mod_tokens = mod_tokens[:-1]

                else:
                    modifier = markups[modifier]
                    change = modifier.get("modifier")
                    modifier_span = modifier.get("span")
                    modifier_span = expand_span(modifier_span)
                    mod_tokens = " ".join([tokens[i] for i in modifier_span])
                    mod_off1 = spans[modifier_span[0]][0]
                    mod_off2 = spans[modifier_span[-1]][1]
                    #mod_off1 = text.find(mod_tokens)
                    #mod_off2 = mod_off1 + len(mod_tokens)
                    mod_offs = "{0}:{1}".format(mod_off1, mod_off2)

                    if change == "negation":
                        label = polarity_flip_dict[label]
                        #print(change)
                        #print(new_polarity)
                    elif change == "increase":
                        intensity = increase_strength_dict[intensity]
                        #print(new_strength)
                    elif change == "decrease":
                        intensity = decrease_strength_dict[intensity]
                    else:
                        pass
                        #print(change)

            # Collect opinion expression: text, span, polarity, and intensity
            exp_span = expand_span(exp_span)
            #print(exp_span)
            exp_tokens = " ".join([tokens[i] for i in exp_span])

            exp_off1 = spans[exp_span[0]][0]
            exp_off2 = spans[exp_span[-1]][1]
            #exp_off1 = text.find(exp_tokens)
            #exp_off2 = exp_off1 + len(exp_tokens)

            if modifier != "empty" and modifier is not None:
                expression = [exp_tokens + ";" + mod_tokens, "{0}:{1};{2}".format(exp_off1, exp_off2, mod_offs)]
            else:
                expression = [exp_tokens, "{0}:{1}".format(exp_off1, exp_off2)]
            #

            # Collect opinion target: text and spans
            if tspan == "empty":
                target = None
            elif tspan is None:
                target = None
            elif ";" in tspan:
                tspans = tspan.split(";")
                for tsp in tspans:
                    target_span = markups[tsp].get("span")
                    target_span = expand_span(target_span)
                    target_tokens = " ".join([tokens[i] for i in target_span])
                    trg_off1 = spans[target_span[0]][0]
                    trg_off2 = spans[target_span[-1]][1]
                    #trg_off1 = text.find(target_tokens)
                    #trg_off2 = trg_off1 + len(target_tokens)
                    target = [target_tokens, "{0}:{1}".format(trg_off1, trg_off2)]

                    # for each target, add an opinion to the list
                    opinions.append({"holder": holder,
                                     "target": target,
                                     "expression": expression,
                                     "label": label,
                                     "intensity": intensity,
                                     "idx": idx})

            else:
                target_span = markups[tspan].get("span")
                target_span = expand_span(target_span)
                target_tokens = " ".join([tokens[i] for i in target_span])

                trg_off1 = spans[target_span[0]][0]
                trg_off2 = spans[target_span[-1]][1]
                #trg_off1 = text.find(target_tokens)
                #trg_off2 = trg_off1 + len(target_tokens)
                target = [target_tokens, "{0}:{1}".format(trg_off1, trg_off2)]

                opinions.append({"holder": holder,
                                 "target": target,
                                 "expression": expression,
                                 "label": label,
                                 "intensity": intensity,
                                 "idx": idx})

        elif m.get("annotation_type") == "polar_target":
            idx = m.get("id")
            #print(idx)
            tspan = m.get("span")
            label = m.get("polar_target_polarity")

            target_span = expand_span(tspan)
            target_tokens = " ".join([tokens[i] for i in target_span])
            trg_off1 = spans[target_span[0]][0]
            trg_off2 = spans[target_span[-1]][1]
            #trg_off1 = text.find(target_tokens)
            #trg_off2 = trg_off1 + len(target_tokens)
            target = [target_tokens, "{0}:{1}".format(trg_off1, trg_off2)]

            # for each target, add an opinion to the list
            opinions.append({"holder": None,
                             "target": target,
                             "expression": None,
                             "label": label,
                             "intensity": "average",
                             "idx": idx})

    #
    new["text"] = text
    new["opinions"] = opinions
    #
    return new

def get_files(current_dir):
    base_files = [i for i in os.listdir(os.path.join(current_dir, "basedata")) if "xml" in i and "~" not in i]
    mark_files = [i.split("_words.xml")[0] + "_OpinionExpression_level.xml"
                  for i in base_files]
    return list(zip(base_files, mark_files))


if __name__ == "__main__":

    basedir = "../DarmstadtServiceReviewCorpus"

    for corpus in ["services", "universities"]:
        processed = []
        print(corpus)
        if "basedata" not in os.listdir(os.path.join(basedir, corpus)):
            for subdir in [i for i in os.listdir(os.path.join(basedir, corpus))]:
                current_dir = os.path.join(basedir, corpus, subdir)
                print(current_dir)
                ff = get_files(current_dir)
                for bfile, mfile in ff:
                    bfile = os.path.join(current_dir, "basedata", bfile)
                    mfile = os.path.join(current_dir, "markables", mfile)

                    o = get_opinions(bfile, mfile)
                    if len(o["opinions"]) > 0:
                        processed.append(o)

        else:
            current_dir = os.path.join(basedir, corpus)
            print(current_dir)
            ff = get_files(current_dir)
            for bfile, mfile in ff:
                bfile = os.path.join(current_dir, "basedata", bfile)
                mfile = os.path.join(current_dir, "markables", mfile)

                o = get_opinions(bfile, mfile)
                if len(o["opinions"]) > 0:
                    processed.append(o)

        os.makedirs(os.path.join("../processed", "darmstadt", corpus), exist_ok=True)
        train_idx = int(len(processed) * .7)
        dev_idx = int(len(processed) * .8)
        train = processed[:train_idx]
        dev = processed[train_idx:dev_idx]
        test = processed[dev_idx:]

        with open(os.path.join("../processed", "darmstadt", corpus, "train.json"), "w") as out:
            json.dump(train, out)
        with open(os.path.join("../processed", "darmstadt", corpus, "dev.json"), "w") as out:
            json.dump(dev, out)
        with open(os.path.join("../processed", "darmstadt", corpus, "test.json"), "w") as out:
            json.dump(test, out)

