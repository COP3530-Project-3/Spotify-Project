Goal: Take in a playlist and generate a radio based on the contents of this playlist (another list of songs)

Approaches:

Feature Distribution: Analyze the distribution of audio features within the playlist. Instead of averaging, identify patterns in feature distributions that indicate dominant characteristics. For example, if most songs have high energy or danceability, it suggests a more upbeat playlist.

Dimension Reduction Techniques:         

Principal Component Analysis (PCA): Reduce the dimensionality of audio features while retaining essential information. Visualizing these reduced dimensions reveal underlying patterns that define the playlist's vibe.  
Feature Matrix: Store audio features in a matrix data structure.  
Transformed Feature Space: Store transformed or reduced dimensions in arrays or matrices.  
Explained Variance Ratios: Store the explained variance ratios (from PCA) using lists or arrays.  

Cosine/Euclidean similarity:  
Compare the orientation/distance of songs in the transformed space to the weighted distribution of features in the playlist. This will allow us to determine similarity.
