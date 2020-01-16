import json
import os
import pickle
import time

from sklearn.externals import joblib

from SVM_model import settings

BASE_DIR = "./SVM_model/"


def predict(file, filename):
    model = joblib.load(BASE_DIR + "saved_model/best_model")
    vec = pickle.load(open(BASE_DIR + "saved_model/feature_path", "rb"))
    list_data = []

    data = open(file, encoding="utf-8")
    load_file = json.load(data)

    for line in load_file:
        # load_file_id = line["_id"]["$oid"]
        load_file_title = line["title"]
        load_file_content = line["content"]
        list_data.append(load_file_title + load_file_content)

    test_term_doc_1 = vec.transform(list_data)

    preds = model.predict(test_term_doc_1)

    if os.path.exists(settings.RESULT_BASE_DIR) is False:
        os.makedirs(settings.RESULT_BASE_DIR)
    if os.path.exists(os.path.join(settings.RESULT_BASE_DIR, time.strftime("%Y%m%d"))) is False:
        os.makedirs(os.path.join(settings.RESULT_BASE_DIR, time.strftime("%Y%m%d")))

    filename = str(filename).replace(".json", "") + "_predict_1.json"
    fid = open(os.path.join(settings.RESULT_BASE_DIR, time.strftime("%Y%m%d") + "\\" + filename), "w", encoding="utf-8")

    list_out_data = []
    for i in range(len(preds)):
        info = dict()
        str_preds = str(preds[i]).replace(".0", "")
        if str_preds == "1":
            info["title"] = load_file[i]["title"]
            info["content"] = load_file[i]["content"]
            list_out_data.append(info)
    print(len(list_out_data))
    out_file = json.dumps(list_out_data, ensure_ascii=False)
    fid.write(out_file)
    fid.close()
