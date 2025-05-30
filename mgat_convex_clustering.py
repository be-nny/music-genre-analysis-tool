import argparse
import os.path
import config
import matplotlib
import numpy as np
import model
import logger

from sklearn.metrics import homogeneity_score, davies_bouldin_score, calinski_harabasz_score, silhouette_score
from model import models, utils
from plot_lib import plotter
from utils import get_genre_filter

matplotlib.use('TkAgg')

parser = argparse.ArgumentParser(prog='Music Genre Analysis Tool - Convex Clustering', formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-c", "--config", required=True, help="Config file")
parser.add_argument("-u", "--uuid", help="UUID of the preprocessed dataset to use, or a list of comma seperated uuid's")
parser.add_argument("-i", "--info", action="store_true", help="Returns a list of available datasets to use")
parser.add_argument("-l", "--lambda_val", default=30, type=int, help="Lambda value")
parser.add_argument("-k", "--k_val", default=50, type=int, help="K value")
parser.add_argument("-g", "--genres", help="Takes a comma-seperated string of genres to use (e.g., jazz,rock,blues,disco) - if set to 'all', all genres are used")


if __name__ == "__main__":
    args = parser.parse_args()
    config = config.Config(path=args.config)
    root = f"{config.OUTPUT_PATH}/_convex_clustering"
    if not os.path.exists(root):
        os.mkdir(root)

    logger = logger.get_logger()
    loader = utils.Loader(out=config.OUTPUT_PATH, uuid=args.uuid, logger=logger, batch_size=model.BATCH_SIZE)

    _, genre_filter = get_genre_filter(args.genres)
    loader.load(split_type="all", normalise=True, flatten=True, genre_filter=genre_filter)

    convex_cluster_model = models.ConvexCluster(loader=loader)
    lambda_values = np.logspace(-2, 1, args.lambda_val)
    u_path = convex_cluster_model.convex_cluster(lambda_vals=lambda_values, k=args.k_val)

    path = os.path.join(root, f"convex_clustering_{args.uuid}_{args.lambda_val}_{args.k_val}_{args.genres}.pdf")
    plotter.plot_convex_clusters(latent_space=convex_cluster_model.latent_space, u_path=u_path, y_true=convex_cluster_model.y_true, loader=loader, path=path)
    logger.info(f"Saved plot '{path}'")

    logger.info(f"homogeneity score: {homogeneity_score(convex_cluster_model.y_true, convex_cluster_model.y_pred):.4f}")
    logger.info(f"davies bouldin score: {davies_bouldin_score(convex_cluster_model.latent_space, convex_cluster_model.y_pred):.4f}")
    logger.info(f"calinski harabasz score: {calinski_harabasz_score(convex_cluster_model.latent_space, convex_cluster_model.y_pred):.4f}")
    logger.info(f"silhouette score: {silhouette_score(convex_cluster_model.latent_space, convex_cluster_model.y_pred):.4f}")
