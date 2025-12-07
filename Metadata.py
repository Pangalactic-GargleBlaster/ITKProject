import SimpleITK as sitk

base_file_path = 'C:/Users/paolo'

image_viewer = sitk.ImageViewer()
image_viewer.SetApplication(base_file_path + '\\AppData\\Local\\Fiji\\fiji-windows-x64.exe')
reader = sitk.ImageSeriesReader()

smoothing_filter = sitk.SmoothingRecursiveGaussianImageFilter()
smoothing_filter.SetSigma(5)
region_growing_filter = sitk.ConnectedThresholdImageFilter()
region_growing_filter.SetSeedList([(128, 256, 256),(384, 256, 256)])
region_growing_filter.SetLower(-1000)
region_growing_filter.SetUpper(-220)
# erosion_filter = sitk.BinaryErodeImageFilter()
# erosion_filter.SetKernelRadius(2)
mask_filter = sitk.MaskImageFilter()
def lungsBorder(image: sitk.Image):
    smoothed_image = smoothing_filter.Execute(image)
    binary_image = region_growing_filter.Execute(smoothed_image)
    # eroded_image = erosion_filter.Execute(binary_image)
    # return sitk.SignedMaurerDistanceMap(
	# 	binary_image-eroded_image,
	# 	insideIsPositive=True,
	# 	squaredDistance=False
	# )
    # return sitk.Cast(binary_image-eroded_image, sitk.sitkFloat64)
    return sitk.Cast(binary_image, sitk.sitkFloat64)


metadata_path = base_file_path + "/Desktop/821/CovidScans/manifest-1608266677008/metadata.csv"
with open(metadata_path, "r") as metadata_file:
	lines = metadata_file.readlines()
	for line in lines:
		if line.split(",")[8] == "0.625mm bone alg":
			local_path = line.split(",")[15]
			dicom_directory = base_file_path + "/Desktop/821/CovidScans/manifest-1608266677008/"+local_path[1:]
			series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_directory)
			reader = sitk.ImageSeriesReader()
			reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_directory, series_IDs[0]))
			image = reader.Execute()
			print(f"line {lines.index(line)+1}, size {image.GetSize()}")
			# image_viewer.Execute(lungsBorder(image))
exit()

