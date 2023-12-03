from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
import math
import os
from sklearn.metrics.pairwise import cosine_similarity
import mplcursors  # Import mplcursors for cursor hover labels
import matplotlib.pyplot as plt
import matplotlib.cm as cm  # Import colormap for colors
import matplotlib.font_manager as fm

def song_pca(songs_metadata, song_ids, playlist_title='playlist', mode='default', mean=[], n_components=5):
    # Convert song metadata to a matrix (rows as songs, columns as features)
    songs_matrix = np.array(list(songs_metadata.values()))

    # Compute mean and variance to compare found songs, add to matrix/dictionary
    if (mode == 'playlist'):
        mean_features = np.mean(songs_matrix, axis=0)
        mean_features = [float(f'{val:.2f}') for val in mean_features] 
        songs_matrix = np.vstack([mean_features, songs_matrix])

        d_mean_features = {}
        d_mean_features['reference'] = mean_features
        songs_metadata = {**d_mean_features, **songs_metadata}

    # Standardize the data (mean=0, variance=1)
    scaler = StandardScaler()
    songs_std = scaler.fit_transform(songs_matrix)

    # Apply PCA
    if (mode == 'playlist'):
        n_components = math.floor(4*math.log(len(songs_metadata), 10)) #maps the n_components to a value based on the amount of tracks dynamically
        if (n_components > 12):
            n_components = 12

    pca = PCA(n_components)  # Define the number of principal components
    songs_pca = pca.fit_transform(songs_std)

    # Explained variance ratio
    explained_var_ratio = pca.explained_variance_ratio_

    # Calculate colors based on distances from mean and similarity ratios
    cosine_ratio = math.log(n_components, 10) - 0.1
    euclidean_ratio = 1-cosine_ratio
    if (mode == 'playlist'):
        mean = songs_pca[0]
    colors, similarity_scores = calculate_similarities(songs_pca, mean, cosine_ratio, euclidean_ratio)  # Using first point as mean

    # Sort songs by similarity scores
    indexlist = [i for i in range(len(similarity_scores))]
    
    #preserving similarity scores
    sorted_indices = []
    saved_similarity_scores = similarity_scores[:]
    num = int(input("Enter 1 for quicksort and 2 for mergesort: "))
    if num == 2:
        print("Proceeding with mergesort")
        sorted_indices = sorted(range(len(similarity_scores)), key=lambda i: similarity_scores[i], reverse=True)
        capture1, capture2 = mergeSortedIndicies(similarity_scores, indexlist)
        print("printing the indicies", sorted_indices, capture2)
        sorted_indices = capture2
    else:
        if (num != 1):
            print("Invalid input.")
        print("Proceeding with quicksort")
        sorted_indices = sorted(range(len(similarity_scores)), key=lambda i: similarity_scores[i], reverse=True)
        capture1, capture2 = quicksortWrapper(similarity_scores, indexlist, len(similarity_scores)-1, 0)
        print("printing the indicies", sorted_indices, capture2)
        sorted_indices = capture2

    similarity_scores = saved_similarity_scores

    # Retrieve top similar songs
    divisor = 0
    if (mode == 'playlist'):
        divisor = 2
    elif (mode == 'recommend'):
        divisor = 6

    top_similar_indices = sorted_indices[1:int(len(songs_metadata)/divisor)]  # Exclude the reference song itself
    top_similar_songs = [list(songs_metadata.keys())[index] for index in top_similar_indices]
    song_ids = [song_ids[index-1] for index in top_similar_indices]

    # create a pair of songs and ids
    songs_and_ids = {}
    length = math.floor(len(songs_metadata)/2)
    n = 0
    for song_name, song_id in zip(top_similar_songs, song_ids):
        if (n == length):
            break
        songs_and_ids[song_name] = song_id
        n += 1

    if (mode == 'recommend'):
        reference_song_index = 0  # Change this index to your chosen reference song
        reference_song_name = list(songs_metadata.keys())[reference_song_index]
        print(f"\n{playlist_title}:")
        for idx, song_index in enumerate(top_similar_indices):
            print(f"{top_similar_songs[idx]} {similarity_scores[song_index]:.2f}")
        print('\n')

    # Plot 2D representation of the data with colors
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(songs_pca[:, 0], songs_pca[:, 1], c=colors, alpha=1)

    # Create labels for annotations
    song_names = list(songs_metadata.keys())
    labels = [f"{song_names[i]}" for i in range(len(song_names))]

    # Use mplcursors to display annotations on hover
    cursor = mplcursors.cursor(scatter, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(f"{labels[sel.index]} {similarity_scores[sel.index]:.2f}"))

    return songs_and_ids, mean, n_components


def calculate_similarities(points, mean, cosine_ratio, euclidean_ratio):
    similarity_scores = [(cosine_ratio * cosine_similarity([mean], [point])[0][0]) +
                         (euclidean_ratio * (1 / (1 + np.linalg.norm(mean - point)))) for point in points]

    # Min-Max scaling to standardize similarity scores to the range of 1 to 100
    max_similarity = max(similarity_scores)
    min_similarity = min(similarity_scores)
    scaled_similarities = [100 * (score - min_similarity) / (max_similarity - min_similarity) if max_similarity != min_similarity else 50 for score in similarity_scores]

    tint_values = [1 - (similarity / 100) for similarity in scaled_similarities]
    colors = [cm.Blues(1 - tint + 0.2) for tint in tint_values]
    return colors, scaled_similarities

def mergeSortedIndicies(scores, indexes):
    # this creates a range of numbers and sorts them according to their score
    if len(scores) == 1:
        return scores, indexes
    middle = len(scores) // 2
    leftlist = scores[:middle]
    rightlist = scores[middle:]
    leftindexlist = indexes[:middle]
    rightindexlist = indexes[middle:]

    leftlist, leftindexlist = mergeSortedIndicies(leftlist, leftindexlist)
    rightlist, rightindexlist = mergeSortedIndicies(rightlist, rightindexlist)

    leftindex = 0
    rightindex = 0
    mainindex = 0
    #while loop for when both lists are still in use

    while leftindex < len(leftlist) and rightindex < len(rightlist):
        if leftlist[leftindex] >= rightlist[rightindex]:
            indexes[mainindex] = leftindexlist[leftindex]
            scores[mainindex] = leftlist[leftindex]
            leftindex += 1
        else:
            indexes[mainindex] = rightindexlist[rightindex]
            scores[mainindex] = rightlist[rightindex]
            rightindex+=1
        mainindex +=1
    

    while leftindex < len(leftindexlist):
        indexes[mainindex] = leftindexlist[leftindex]
        scores[mainindex] = scores[leftindex]
        mainindex += 1
        leftindex+=1
    

    while rightindex < len(rightindexlist):
        indexes[mainindex] = rightindexlist[rightindex]
        scores[mainindex] = scores[leftindex]
        mainindex += 1
        rightindex += 1
    
    return scores, indexes

def quicksortPartition(array, indicies, high, low):
    #we choose the ending of the array as the pivot element
    pivotelement  = array[high]
    pivotindex = indicies[high]
    #we have iterators i and j that go through the low and high portions of the array
    i = low -1
    for j in range(low, high):
        if array[j] >= pivotelement:
            i +=1
            temp = array[i]
            temp1 = indicies[i]
            array[i] = array[j]
            indicies[i] = indicies[j]
            array[j] = temp
            indicies[j] = temp1
    # now we need to put the pivot in the right spot
    array[high] = array[i+1]
    indicies[high] = indicies [i+1]
    array[i+1] = pivotelement
    indicies[i+1] = pivotindex
    
    return i+1, array, indicies

def quicksortWrapper(array, indicies, high, low):
    if low < high:
        the_partition, newarray, newindicies = quicksortPartition(array, indicies, high, low)
        array = newarray
        indicies = newindicies

        #now we do recursion on the array
        newarray, newindicies = quicksortWrapper(array, indicies, the_partition-1, low)

        array = newarray
        indicies = newindicies
        newarray, newindicies = quicksortWrapper(array, indicies, high, the_partition +1)
        array = newarray
        indicies = newindicies
    return array, indicies
