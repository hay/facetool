# Inspired by < https://www.pyimagesearch.com/2018/07/09/face-clustering-with-python/ >

from sklearn.cluster import DBSCAN
from .path import Path
from .util import force_mkdir
import logging
import numpy as np
import shutil

class Clusterer:
    def cluster_encodings(self, encodings):
        logging.debug(f"Clustering {len(encodings)} encodings")

        clt = DBSCAN(
            metric = "euclidean"
        )

        # Generate a list so we also have an index
        faces = [ { "file" : k, "encoding" : v } for k, v in encodings.items()]
        faces_encodings = [ i["encoding"] for i in faces ]

        clt.fit(np.array(faces_encodings))
        output = []

        for fid in np.unique(clt.labels_):
            if fid < 0:
                # Skip outliers
                continue

            fid_items = np.where(clt.labels_ == fid)

            output.append({
                "count" : len(fid_items[0]),
                "files" : [ faces[index]["file"] for index in fid_items[0]],
                "id" : int(fid)
            })

        return output

    def move_files(self, clusters, directory):
        for cluster in clusters:
            cluster_id = cluster["id"]
            cluster_path = Path(directory) / str(cluster_id)
            force_mkdir(cluster_path)

            for path in cluster["files"]:
                new_path = Path(cluster_path) / Path(path).name
                logging.debug(f"Copying '{path}' to '{new_path}'")
                shutil.copy(path, new_path)