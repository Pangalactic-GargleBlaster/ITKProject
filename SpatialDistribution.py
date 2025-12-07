import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
import json
import os

print(sitk.Version())

# Setup image viewer (optional, for final viewing)
image_viewer = sitk.ImageViewer()
image_viewer.SetApplication("C:\\Users\\kevta\\Fiji\\fiji-windows-x64.exe")


# Load DICOM series
dicom_directory = "C:/Users/kevta/Biomedical Scans/manifest-1608266677008/MIDRC-RICORD-1A/MIDRC-RICORD-1A-419639-000082/08-02-2002-NA-CT CHEST WITHOUT CONTRAST-04614/3.000000-0.625mm bone alg-26970/"
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_directory)
print(f"Series IDs: {series_IDs}")

reader = sitk.ImageSeriesReader()
reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_directory, series_IDs[0]))
image = reader.Execute()

# Cast to float for processing
image = sitk.Cast(image, sitk.sitkFloat64)

# B1 Algorithm: Anisotropic Diffusion Filter
print("Applying anisotropic diffusion filter...")
anisotropic_filter = sitk.CurvatureAnisotropicDiffusionImageFilter()
anisotropic_filter.SetTimeStep(0.03)
anisotropic_filter.SetNumberOfIterations(5)
anisotropic_filter.SetConductanceParameter(3.0)
filtered_image = anisotropic_filter.Execute(image)

# Step 1: Segment Lung Fields
print("Segmenting lung fields...")
lung_lower_threshold = -1000
lung_upper_threshold = -400

lung_mask = sitk.BinaryThreshold(
    filtered_image,
    lowerThreshold=lung_lower_threshold,
    upperThreshold=lung_upper_threshold,
    insideValue=1,
    outsideValue=0
)

# Clean up lung mask with morphology
lung_opening = sitk.BinaryMorphologicalOpeningImageFilter()
lung_opening.SetKernelRadius(3)
lung_opening.SetKernelType(sitk.sitkBall)
lung_opening.SetForegroundValue(1)
lung_mask_clean = lung_opening.Execute(lung_mask)

# Step 2: Segment COVID regions (ground-glass opacity)
print("Segmenting COVID regions...")
covid_lower_threshold = -700
covid_upper_threshold = -300

covid_segmented = sitk.BinaryThreshold(
    filtered_image, 
    lowerThreshold=covid_lower_threshold, 
    upperThreshold=covid_upper_threshold,
    insideValue=1,
    outsideValue=0
)

# Morphological Operations on COVID segmentation
kernel_radius = 2

# Opening: removes small noise
print("Applying morphological opening...")
opening_filter = sitk.BinaryMorphologicalOpeningImageFilter()
opening_filter.SetKernelRadius(kernel_radius)
opening_filter.SetKernelType(sitk.sitkBall)
opening_filter.SetForegroundValue(1)
covid_opened = opening_filter.Execute(covid_segmented)

# Closing: fills small holes
print("Applying morphological closing...")
closing_filter = sitk.BinaryMorphologicalClosingImageFilter()
closing_filter.SetKernelRadius(kernel_radius)
closing_filter.SetKernelType(sitk.sitkBall)
closing_filter.SetForegroundValue(1)
covid_closed = closing_filter.Execute(covid_opened)

# Step 3: Intersect COVID with lung fields (only keep COVID in lungs)
print("Intersecting COVID regions with lung fields...")
covid_in_lungs = sitk.And(covid_closed, lung_mask_clean)

# Step 4: Connected Component Analysis
print("Performing connected component analysis...")
connected_components = sitk.ConnectedComponent(covid_in_lungs)
labeled_image = sitk.RelabelComponent(connected_components, minimumObjectSize=100)

# Step 5: Quantitative Characterization
print("\n=== QUANTITATIVE ANALYSIS ===")

# Label statistics for shape analysis
label_shape_stats = sitk.LabelShapeStatisticsImageFilter()
label_shape_stats.Execute(labeled_image)

# Intensity statistics
label_intensity_stats = sitk.LabelIntensityStatisticsImageFilter()
label_intensity_stats.Execute(labeled_image, filtered_image)

num_regions = label_shape_stats.GetNumberOfLabels()
print(f"\nNumber of detected COVID regions: {num_regions}")

# Get image spacing for physical measurements
spacing = image.GetSpacing()
print(f"Image spacing: {spacing} mm")


smoothing_filter = sitk.SmoothingRecursiveGaussianImageFilter()
smoothing_filter.SetSigma(5)
smoothed_image = smoothing_filter.Execute(image)
print("smoothed the image")

region_growing_filter = sitk.ConnectedThresholdImageFilter()
region_growing_filter.SetSeedList([(128, 256, 256),(384, 256, 256)])
region_growing_filter.SetLower(-1000)
region_growing_filter.SetUpper(-200)
binary_image = region_growing_filter.Execute(smoothed_image)
erosion_filter = sitk.BinaryErodeImageFilter()
erosion_filter.SetKernelRadius(2)
binary_image = erosion_filter.Execute(binary_image)
inverse_binary_image = 1 - binary_image
print("binarized image")

mask_filter = sitk.MaskImageFilter()

# apply the lung mask over the covid in lungs image to only get the segmentation in the lungs
covid_test = mask_filter.Execute(covid_in_lungs, binary_image)
covid_test_array = sitk.GetArrayFromImage(covid_test)



# find the voxels where covid has been segmented will be in (z,y,x) coordinates 
covid_location = np.argwhere(covid_test_array > 0)

# Get that point from the covid mask image and correctly converts where the coordinates should go
graph_points = []
for z, y, x in covid_location:
    point = covid_test.TransformIndexToPhysicalPoint((int(x), int(y), int(z)))
    graph_points.append(point)

# Make the graph of point into a numpy graph
graph_points_np = np.array(graph_points)

# Create a3d plot to fit the points
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# scatter(x, y, z, color, marker, size)
ax.scatter(graph_points_np[:, 0], graph_points_np[:, 1], graph_points_np[:, 2], c='r', marker='o', s=1)

# Label axis
ax.set_xlabel('X axis (mm)')
ax.set_ylabel('Y axis (mm)')
ax.set_zlabel('Z axis (mm)')
ax.set_title('Spatial Distribution of Segmentation')

# Y-axis view
# ax.view_init(elev=30, azim=0)

# X-axis view
# ax.view_init(elev=30, azim=90) 

# Z-axis view
# ax.view_init(elev=90, azim=0)

plt.show()

# images used for plot
image_viewer.Execute(covid_test)
