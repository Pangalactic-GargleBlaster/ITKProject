import SimpleITK as sitk

# lung segmentation utility function
smoothing_filter = sitk.SmoothingRecursiveGaussianImageFilter()
smoothing_filter.SetSigma(5)
region_growing_filter = sitk.ConnectedThresholdImageFilter()
region_growing_filter.SetSeedList([(128, 256, 256),(384, 256, 256)])
region_growing_filter.SetLower(-1000)
region_growing_filter.SetUpper(-200)
erosion_filter = sitk.BinaryErodeImageFilter()
erosion_filter.SetKernelRadius(1)
mask_filter = sitk.MaskImageFilter()
def lungsBorder(image: sitk.Image):
    smoothed_image = smoothing_filter.Execute(image)
    binary_image = region_growing_filter.Execute(smoothed_image)
    eroded_image = erosion_filter.Execute(binary_image)
    return sitk.SignedMaurerDistanceMap(binary_image-eroded_image)


image_viewer = sitk.ImageViewer()
image_viewer.SetApplication('C:\\Users\\admin\\AppData\\Local\\Fiji\\fiji-windows-x64.exe')
reader = sitk.ImageSeriesReader()

reference_dicom_directory = "C:/Users/admin/Desktop/821/CovidScans/manifest-1608266677008/MIDRC-RICORD-1A/MIDRC-RICORD-1A-419639-000082/08-02-2002-NA-CT CHEST WITHOUT CONTRAST-04614/3.000000-0.625mm bone alg-26970/"
reference_series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(reference_dicom_directory)
reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(reference_dicom_directory, reference_series_IDs[0]))
reference_image = reader.Execute()
reference_image = sitk.Cast(reference_image, sitk.sitkFloat64)
reference_lungs = lungsBorder(reference_image)
print("reference lung field ready")
image_viewer.Execute(reference_image)

metadata_path = "C:/Users/admin/Desktop/821/CovidScans/manifest-1608266677008/metadata.csv"
registration = sitk.ImageRegistrationMethod()
registration.SetMetricAsJointHistogramMutualInformation()
registration.SetOptimizerAsAmoeba(0.1, 100)
registration.SetInterpolator(sitk.sitkLinear)
registration.AddCommand(sitk.sitkIterationEvent,
               lambda: print(registration.GetOptimizerIteration(),
							 registration.GetMetricValue(),
                             list(registration.GetOptimizerPosition())))

with open(metadata_path, "r") as metadata_file:
	lines = metadata_file.readlines()
	for line in lines:
		if line.split(",")[8] == "0.625mm bone alg" and line.split(",")[6] == "CT CHEST WITHOUT CONTRAST":
			local_path = line.split(",")[15]
			dicom_directory = "C:/Users/admin/Desktop/821/CovidScans/manifest-1608266677008/"+local_path[1:]
			series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_directory)
			reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_directory, series_IDs[0]))
			image = reader.Execute()
			image = sitk.Cast(image, sitk.sitkFloat64)
			lungs_only_image = lungsBorder(image)
			print("lung field to be registered ready")
			registration.SetInitialTransform(sitk.Similarity3DTransform())
			transform = registration.Execute(reference_lungs, lungs_only_image)
			print(f"the transform for this image is {transform}")
			resampler = sitk.ResampleImageFilter()
			resampler.SetReferenceImage(reference_image)
			resampler.SetInterpolator(sitk.sitkLinear)
			resampler.SetTransform(transform)
			registeredImage = resampler.Execute(image)
			image_viewer.Execute(registeredImage)



			