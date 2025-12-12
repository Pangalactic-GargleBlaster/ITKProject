import SimpleITK as sitk
import numpy as np
from datetime import datetime

base_file_path = 'C:/Users/paolo'
# lung segmentation utility function
smoothing_filter = sitk.SmoothingRecursiveGaussianImageFilter()
smoothing_filter.SetSigma(5)
region_growing_filter = sitk.ConnectedThresholdImageFilter()
region_growing_filter.SetSeedList([(128, 256, 256),(384, 256, 256)])
region_growing_filter.SetLower(-1000)
region_growing_filter.SetUpper(-220)
# erosion_filter = sitk.BinaryErodeImageFilter()
# erosion_filter.SetKernelRadius(2)
mask_filter = sitk.MaskImageFilter()
def lungsBorder(image: sitk.Image) -> sitk.Image:
    smoothed_image = smoothing_filter.Execute(image)
    binary_image = region_growing_filter.Execute(smoothed_image)
    return sitk.Cast(binary_image, sitk.sitkFloat64)

image_viewer = sitk.ImageViewer()
image_viewer.SetApplication(base_file_path + '\\AppData\\Local\\Fiji\\fiji-windows-x64.exe')
reader = sitk.ImageSeriesReader()

reference_dicom_directory = base_file_path + "/Desktop/821/CovidScans/manifest-1608266677008/MIDRC-RICORD-1A/MIDRC-RICORD-1A-419639-000082/08-02-2002-NA-CT CHEST WITHOUT CONTRAST-04614/3.000000-0.625mm bone alg-26970/"
reference_series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(reference_dicom_directory)
reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(reference_dicom_directory, reference_series_IDs[0]))
starting_time = datetime.now()
reference_image = reader.Execute()
reference_image.SetOrigin([0,0,0])
reference_image = sitk.Cast(reference_image, sitk.sitkFloat64)
finished_loading_time = datetime.now()
reference_lungs = lungsBorder(reference_image)
segmented_lungs_time = datetime.now()
print("reference lung field ready")
# image_viewer.Execute(reference_lungs_border)

metadata_path = base_file_path + "/Desktop/821/CovidScans/manifest-1608266677008/metadata.csv"
registration = sitk.ImageRegistrationMethod()
registration.SetMetricAsMeanSquares()
registration.SetMetricSamplingStrategy(registration.RANDOM)
registration.SetMetricSamplingPercentage(0.02)
registration.SetOptimizerAsAmoeba(simplexDelta=0.01, numberOfIterations=200)
# registration.SetOptimizerAsGradientDescent(
#     learningRate=0.5,
#     numberOfIterations=200,
# 	convergenceWindowSize=100
# )

registration.SetInterpolator(sitk.sitkLinear)
registration.AddCommand(
	sitk.sitkIterationEvent,
	lambda: print(
		registration.GetOptimizerIteration(),
		registration.GetMetricValue(),
		list(registration.GetOptimizerPosition())
	)
)

with open(metadata_path, "r") as metadata_file:
	lines = metadata_file.readlines()
	# for line in lines:
	for line in [lines[47]]:
		if line.split(",")[8] == "0.625mm bone alg" and line.split(",")[6] == "CT CHEST WITHOUT CONTRAST":
			local_path = line.split(",")[15]
			dicom_directory = base_file_path + "/Desktop/821/CovidScans/manifest-1608266677008/"+local_path[1:]
			series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_directory)
			reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_directory, series_IDs[0]))
			image = reader.Execute()
			image.SetOrigin([0,0,0])
			image = sitk.Cast(image, sitk.sitkFloat64)
			lungs_only_image = lungsBorder(image)
			print("lung field to be registered ready")
			# image_viewer.Execute(lungs_border)
			# lungs_border.SetOrigin(reference_lungs_border.GetOrigin())
			registration.SetInitialTransform(sitk.Similarity3DTransform())
			# registration.SetOptimizerScalesFromPhysicalShift()
			registration.SetOptimizerScales([10, 10, 10, 0.01, 0.01, 0.01, 10])
			registration_starting_time = datetime.now()
			transform = registration.Execute(reference_lungs, lungs_only_image)
			registration_finished_time = datetime.now()
			# transform = sitk.Similarity3DTransform()
			# transform.SetScale(0.9)
			# transform.SetRotation([0, 0, -0.1305, 0.9914])  # rotation around z-axis
			# transform.SetTranslation((50,0,20))
			print(f"metric after transform: {registration.MetricEvaluate(reference_lungs, lungs_only_image)}")
			
			print(f"the transform for this image is {transform}")
			resampler = sitk.ResampleImageFilter()
			resampler.SetReferenceImage(reference_image)
			resampler.SetInterpolator(sitk.sitkLinear)
			resampler.SetDefaultPixelValue(-3024.0)
			# resampler.SetDefaultPixelValue(0)
			resampler.SetTransform(transform)
			registeredImage = resampler.Execute(image)
			resampling_finished_time = datetime.now()
			print(
				'TIMING STATS:\n' +
				f'Loading time: {finished_loading_time - starting_time}\n' +
				f'segmentation time: {segmented_lungs_time - finished_loading_time}\n' +
				f'registration time: {registration_finished_time - registration_starting_time}\n' +
				f'resampling_time: {resampling_finished_time - registration_finished_time}'
			)
			# registered_lungs = resampler.Execute(lungs_border)
			# image_viewer.Execute(registeredImage)
			# image_viewer.Execute(registered_lungs)
			# image_viewer.Execute(sitk.CheckerBoard(reference_lungs_border, registered_lungs, [8,8,1]))
			# image_viewer.Execute(sitk.Compose(reference_lungs_border, registered_lungs, reference_lungs_border/2 + registered_lungs/2))

			# TODO: use registered_image to run segmentation and then quantification. This will be called once per scan




			