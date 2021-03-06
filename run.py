#!/usr/bin/env python
import random
import json
import numpy as np
import pandas as pd
import argparse
import base64

import aicrowd_helpers
import time
import traceback

import glob
import os
import json


"""
################################################################################################################
################################################################################################################
## Expected ENVIRONMENT Variables
################################################################################################################

* AICROWD_TEST_IMAGES_PATH : Absolute path to  folder containing all the test images
* AICROWD_TEST_METADATA_PATH : Absolute path to a CSV file containing extra metadata about each of the test images
* AICROWD_PREDICTIONS_OUTPUT_PATH : path where you are supposed to write the output predictions.csv
"""
AICROWD_TEST_IMAGES_PATH = os.getenv("AICROWD_TEST_IMAGES_PATH", "./data/validate_images_small/")
AICROWD_TEST_METADATA_PATH = os.getenv("AICROWD_TEST_METADATA_PATH", "./data/validate_labels_small.csv")
AICROWD_PREDICTIONS_OUTPUT_PATH = os.getenv("AICROWD_PREDICTIONS_OUTPUT_PATH", "random_prediction.csv")

# Note : These list of snake-species are the ones that are represented in the training set of this round 4
VALID_SNAKE_SPECIES = list(pd.read_csv("round4_classes.csv")["scientific_name"])

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0) # only difference

def get_random_prediction(image_id):
    predictions = [np.random.rand() for _ in VALID_SNAKE_SPECIES]
    predictions = softmax(predictions)
    return predictions

def run():
    ########################################################################
    # Register Prediction Start
    ########################################################################
    aicrowd_helpers.execution_start()


    ########################################################################
    # Load Tests Meta Data file
    #       and iterate over all its rows
    #
    #       Each Row contains the following information : 
    #
    #       - hashed_id  : a unique id for each test image
    #       - country    : Country where this image was taken
    #       - continent  : Continent where this image was taken
    ########################################################################    

    OUTPUT_LINES = []
    HEADER = ['hashed_id'] + VALID_SNAKE_SPECIES
    OUTPUT_LINES.append(",".join(HEADER))

    tests_df = pd.read_csv(AICROWD_TEST_METADATA_PATH)
    for _idx, row in tests_df.iterrows():
        image_id = row["hashed_id"]
        country = row["country"]
        continent = row["continent"]
        filename = "{}.jpg".format(image_id)
        filepath = os.path.join(AICROWD_TEST_IMAGES_PATH, filename)

        predictions = get_random_prediction(image_id)
        PREDICTION_LINE = [image_id] + [str(x) for x in predictions.tolist()]
        OUTPUT_LINES.append(",".join(PREDICTION_LINE))
        
        ########################################################################
        # Register Prediction
        #
        # Note, this prediction register is not a requirement. It is used to
        # provide you feedback of how far are you in the overall evaluation.
        # In the absence of it, the evaluation will still work, but you
        # will see progress of the evaluation as 0 until it is complete
        #
        # Here you simply announce that you completed processing a set of
        # image_ids
        ########################################################################
        aicrowd_helpers.execution_progress({
            "image_ids" : [image_id] ### NOTE : This is an array of image_ids 
        })


    # Write output
    fp = open(AICROWD_PREDICTIONS_OUTPUT_PATH, "w")
    fp.write("\n".join(OUTPUT_LINES))
    fp.close()
    ########################################################################
    # Register Prediction Complete
    ########################################################################
    aicrowd_helpers.execution_success({
        "predictions_output_path" : AICROWD_PREDICTIONS_OUTPUT_PATH
    })


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        aicrowd_helpers.execution_error(error)
