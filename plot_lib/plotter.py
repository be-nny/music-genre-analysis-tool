import seaborn as sns

from sklearn.metrics import accuracy_score
from model import utils
from plot_lib import *

def plot_tree_map(cluster_stats: dict, path: str) -> None:
    """
    Creates a figure with a set of treemap subplots demonstrating which clusters have what genre in them.

    :param cluster_stats: cluster statistics
    :param path: path to save figure
    """
    n_cols = 4
    n_rows = int(np.ceil(len(cluster_stats) / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 4, n_rows * 4))
    axes = axes.flatten()

    for i, (cluster_key, values) in enumerate(cluster_stats.items()):
        labels = []
        sizes = []
        for key, value in values.items():
            labels.append(key)
            sizes.append(cluster_stats[cluster_key][key])

        category_codes, unique_categories = pd.factorize(np.array(list(values.keys())))
        colours = [CMAP(code) for code in category_codes]

        total = sum(sizes)
        percentages = [round(s/total, 2) for s in sizes]
        labels = [f"{l}: {p}" for l, p in zip(labels, percentages)]

        ax = axes[i]
        ax.set_axis_off()

        squarify.plot(
            sizes=sizes,
            label=labels,
            color=colours,
            ax=ax,
            text_kwargs={
                'color': 'black',
                'fontsize': 9,
                'fontweight': 'bold',
                'bbox': dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3')
            },
            pad=True,
        )
        ax.set_title(f"Cluster Statistics for Cluster {cluster_key}")

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')
    plt.close()

def plot_2d_kmeans_boundaries(latent_space: np.ndarray, kmeans, path: str, title: str, genre_filter: str, h: float = 0.02) -> None:
    """
    Plots the kmeans decision boundaries

    :param title: title
    :param latent_space: 2D latetn space
    :param kmeans: KMeans object
    :param path: path to save
    :param genre_filter: genre filter
    :param h: step size for the grid used to create the mesh for plotting the decision boundaries
    """

    # colour map
    colour_map = pypalettes.load_cmap("Benedictus")
    colours = [colour_map(i / (kmeans.n_clusters - 1)) for i in range(kmeans.n_clusters)]
    cmap = ListedColormap(colours)

    # plot the decision boundary
    x_min, x_max = latent_space[:, 0].min() - 1, latent_space[:, 0].max() + 1
    y_min, y_max = latent_space[:, 1].min() - 1, latent_space[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    # obtain labels for each point in mesh. Use last trained model.
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    Z = kmeans.predict(grid_points)

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1)
    plt.clf()
    img = plt.imshow(Z, interpolation="nearest", extent=(xx.min(), xx.max(), yy.min(), yy.max()), cmap=cmap, aspect="auto", origin="lower")
    plt.plot(latent_space[:, 0], latent_space[:, 1], "k.", markersize=2)

    # plot the centroids as a white X
    centroids = kmeans.cluster_centers_
    plt.scatter(centroids[:, 0], centroids[:, 1], marker="x", s=169, linewidths=3, color="w", zorder=10)
    plt.title(f"K-means Clustering Boundaries \n (genres: {genre_filter})")
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())

    # adding the colour bar
    colorbar = plt.colorbar(img, ticks=range(kmeans.n_clusters))
    colorbar.set_label('Cluster Labels', rotation=270, labelpad=15)
    colorbar.set_ticklabels([f"Cluster {i}" for i in range(kmeans.n_clusters)])
    plt.title(title)
    plt.savefig(path, bbox_inches='tight')

def plot_eigenvalues(path, pca_model, title) -> None:
    """
    Plot eigenvalues after pca transformation

    :param path: path to save figure
    :param pca_model: pca model
    :param title: title
    """

    plt.plot([i for i in range(1, pca_model.n_components + 1)], pca_model.explained_variance_, marker="o", linestyle="-", label="Eigenvalues")
    plt.xlabel("Number of Components")
    plt.ylabel("Explained Variance (log)")
    plt.yscale("log")
    plt.title(title)
    plt.savefig(path, bbox_inches='tight')
    plt.close()

def plot_3D(latent_space: np.ndarray, y_true: np.ndarray, path: str, title: str, logger, genre_filter: str, loader) -> None:
    """
    Plots a 3 dimensional latent representation in 3D space

    :param title: title
    :param latent_space: 3D latent space
    :param y_true: true labels
    :param path: path to save
    :param logger: logger
    :param genre_filter: genre filters
    :param loader: dataset loader
    :return: None
    """

    unique_labels = np.unique(y_true)
    str_labels = loader.decode_label(unique_labels)
    print(latent_space.shape)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(latent_space[:, 0], latent_space[:, 1], latent_space[:, 2], c=y_true, cmap=CMAP, alpha=0.7, s=10)
    colour_bar = plt.colorbar(scatter, ax=ax, label="Cluster Labels")
    colour_bar.set_ticks(unique_labels)
    colour_bar.set_ticklabels(str_labels)

    ax.set_title(f"3D Visualisation of Latent Space (genres: {genre_filter})")
    ax.set_xlabel("Axis 1")
    ax.set_ylabel("Axis 2")
    ax.set_zlabel("Axis 3")

    ax.grid(False)
    plt.title(title)
    plt.show()
    plt.savefig(path, bbox_inches='tight')
    logger.info(f"Saved plot '{path}'")

def plot_2D(latent_space: np.ndarray, y_true: np.ndarray, path: str, title: str, genre_filter: str, loader) -> None:
    """
    Plots a 2 dimensional latent representation in 2D space

    :param title: title
    :param latent_space: 2D latent space
    :param y_true: true labels
    :param path: path to save
    :param logger: logger
    :param genre_filter: genre filters
    :param loader: dataset loader
    :return: None
    """
    unique_labels = np.unique(y_true)
    str_labels = loader.decode_label(unique_labels)

    colours = [CMAP(i / (len(unique_labels) - 1)) for i in range(len(unique_labels))]
    cmap = ListedColormap(colours)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    scatter = ax.scatter(latent_space[:, 0], latent_space[:, 1], c=y_true, cmap=cmap, alpha=0.7, s=10)
    colour_bar = plt.colorbar(scatter, ax=ax, label="Cluster Labels")
    colour_bar.set_ticks(unique_labels)
    colour_bar.set_ticklabels(str_labels)

    ax.set_title(f"2D Visualisation of Latent Space (genres: {genre_filter})")
    ax.set_xlabel("Axis 1")
    ax.set_ylabel("Axis 2")
    ax.grid(False)
    plt.title(title)
    plt.savefig(path, bbox_inches='tight')

def plot_correlation_accuracy(latent_space, y_true, covariance_mat, label, max_n_neighbours: int = 100) -> None:
    """
    Plot the correlation accuracy as a line graph

    :param latent_space: the latent space
    :param y_true: true labels
    :param covariance_mat: covariance matrice, can be None
    :param label: legend label
    :param max_n_neighbours: the maximum number of neighbours
    """

    accuracy_scores = []
    for n in range(1, max_n_neighbours + 1):
        t_corr, p_corr = utils.correlation(latent_space=latent_space, y_true=y_true, covar=covariance_mat, n_neighbours=n)
        acc = accuracy_score(t_corr, p_corr)
        accuracy_scores.append(acc)

    plt.plot(range(1, max_n_neighbours + 1), accuracy_scores, label=label)
    plt.xlabel("Number of Neighbours")
    plt.ylabel("Accuracy")
    plt.legend()

def plot_shannon_entropy(n_clusters, avg_shannon_vals, label: str) -> None:
    """
    Plot the shannon entropy of the total cluster space

    :param n_clusters: list of total number of clusters
    :param avg_shannon_vals: list of average shannon values
    :param label: legend label
    """

    plt.plot(n_clusters, avg_shannon_vals, label=label, alpha=0.7)
    plt.xticks(ticks=n_clusters, labels=[str(int(x)) for x in n_clusters])
    plt.xlabel("Number of Clusters")
    plt.ylabel("Average Shannon Entropy")
    plt.legend()

def plot_correlation_conf_mat(cf_matrix, class_labels, n_neighbours, path, **kwargs) -> None:
    """
    Plot the confusion matrix

    :param cf_matrix: confusion matrix
    :param class_labels: class labels
    :param n_neighbours: number of nearest neighbours
    :param path: path to save
    :param kwargs: kwargs corresponding to 'f1_score', 'precision', 'recall', and 'accuracy'
    """

    f1 = kwargs["f1_score"]
    precision = kwargs["precision"]
    recall = kwargs["recall"]
    accuracy = kwargs["accuracy"]
    metrics_str = f"Accuracy: {accuracy:.2%}, Precision: {precision:.2%}, Recall: {recall:.2%}, F1 Score: {f1:.2%}"

    sns.heatmap(cf_matrix, annot=True, fmt="d", xticklabels=class_labels, yticklabels=class_labels)
    plt.xlabel("Predicted Neighbour Labels")
    plt.ylabel("True Label")
    plt.title(f"Confusion Matrix when nearest_neighbours={n_neighbours} \n{metrics_str}")
    plt.savefig(path, bbox_inches='tight')
    plt.close()

def plot_convex_clusters(latent_space, u_path, loader, y_true, path):
    """
    Plot the convex clustering heirarchy

    :param latent_space: latent space
    :param u_path: cluster centre path
    :param loader: data loader
    :param y_true: true labels
    :param path: path to save
    """

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    # plot cluster center paths
    for i in range(len(latent_space)):
        cluster_path = np.array([U[i] for U in u_path])
        ax.plot(cluster_path[:, 0], cluster_path[:, 1], color="black", alpha=0.3)
        ax.scatter(cluster_path[:, 0], cluster_path[:, 1], color="black", s=3, alpha=0.3)

    # create colour bar labels
    unique_labels = np.unique(y_true)
    str_labels = loader.decode_label(unique_labels)
    colours = [CMAP(i / (len(unique_labels) - 1)) for i in range(len(unique_labels))]
    cmap = ListedColormap(colours)

    scatter = ax.scatter(latent_space[:, 0], latent_space[:, 1], c=y_true, cmap=cmap, s=20)
    colour_bar = plt.colorbar(scatter, ax=ax, label="Cluster Labels")
    colour_bar.set_ticks(unique_labels)
    colour_bar.set_ticklabels(str_labels)

    ax.set_title("Convex Clustering")
    ax.set_xlabel("Axis 1")
    ax.set_ylabel("Axis 2")
    plt.savefig(path, bbox_inches='tight')
    plt.close()

def plot_classifier_scores(data: dict, classifier_labels: list, path: str) -> None:
    """
    Plot classifier scores on a bar chart

    :param data: score data
    :param classifier_labels: classifier names
    :param path: path to save
    :return:
    """

    x = np.arange(len(classifier_labels))
    width = 0.1
    multiplier = 0

    fig, ax = plt.subplots(figsize=(20, 6))

    for signal_processor, accuracy_scores in data.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, accuracy_scores, width, label=signal_processor)
        ax.bar_label(rects, padding=3, fmt="%.2f")
        multiplier += 1

    ax.set_title("Comparison of the Accuracy Between a set of Multi-classifiers and Different Preprocessed Datasets")
    ax.set_ylabel("Accuracy Scores")
    ax.set_title("Classifier Accuracy Scores per Signal Processor")
    ax.set_xticks(x + width, classifier_labels)
    ax.legend()
    plt.savefig(path, bbox_inches='tight')
    plt.close()