""" Data cleaning functions
"""

import difflib
import numpy as np
import pandas as pd
import textdistance

from csgo.analytics.distance import point_distance


# def clean_footsteps(df, max_dist=500):
#     """ A function to clean a dataframe of footsteps, as created by the match_parser
#     """
#     for r in range(0, df.RoundNum.max() + 1):
#         for p in df.SteamID.unique():
#             player_df = df[(df["RoundNum"] == r) & (df["SteamID"] == p)]
#             player_pos = []
#             player_pos_clean = []
#             for i, row in player_df.iterrows():
#                 player_pos.append((row["X"], row["Y"], row["Z"]))
#             for i, pos in enumerate(player_pos):
#                 if i == 0:
#                     player_pos_clean.append(0)
#                 else:
#                     player_pos_clean.append(
#                         distance.euclidean(list(pos), list(player_pos[i - 1]))
#                     )
#     return NotImplementedError


def associate_entities(game_names=[], entity_names=[], metric="lcss"):
    """A function to return a dict of associated entities. Uses longest common subsequence distance.
    Args:
        game_names (list)   : A list of names generated by the demofile
        entity_names (list) : A list of names
    Returns:
        entity_dict (dict) : A dictionary where the keys are entries in game_names
    """
    if metric.lower() == "lcss":
        dist_metric = textdistance.lcsseq.distance
    elif metric.lower() == "hamming":
        dist_metric = textdistance.hamming.distance
    elif metric.lower() == "levenshtein":
        dist_metric = textdistance.levenshtein.distance
    elif metric.lower() == "jaro":
        dist_metric = textdistance.jaro.distance
    elif metric.lower() == "difflib":
        entities = {}
        for gn in game_names:
            if gn is not None and gn is not np.nan:
                closest_name = difflib.get_close_matches(gn, entity_names, n=1, cutoff=0.0)
                if len(closest_name) > 0:
                    entities[gn] = closest_name[0]
                else:
                    entities[gn] = None
        entities[None] = None
        return entities
    else:
        raise ValueError("Metric can only be LCSS, Hamming, Levenshtein or Jaro")
    entities = {}
    for gn in game_names:
        if gn is not None and gn is not np.nan and gn != '':
            name_distances = []
            names = []
            if len(entity_names) > 0:
                for p in entity_names:
                    name_distances.append(dist_metric(gn.lower(), p.lower()))
                    names.append(p)
                entities[gn] = names[np.argmin(name_distances)]
                popped_name = entity_names.pop(np.argmin(name_distances))
        if gn == '':
            entities[gn] = None
    entities[None] = None
    return entities


def replace_entities(df, col_name, entity_dict):
    """A function to replace values in a Pandas df column given an entity dict, as created in associate_entities()

    Args:
        df (DataFrame)     : A Pandas DataFrame
        col_name (string)  : A column in the Pandas DataFrame
        entity_dict (dict) : A dictionary as created in the associate_entities() function
    """
    if col_name not in df.columns:
        raise ValueError("Column does not exist!")
    df[col_name].replace(entity_dict, inplace=True)
    return df


def remove_dupes(df, cols):
    """A function to remove duplicates by taking the first occurence

    Args:
        df (DataFrame) : A Pandas DataFrame
        cols (list)    : A list of columns to groupby on
    """
    return df.groupby(cols).first().reset_index()
