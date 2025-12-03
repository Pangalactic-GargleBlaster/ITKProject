import SimpleITK as sitk

# read image
image_viewer = sitk.ImageViewer()
image_viewer.SetApplication('C:\\Users\\paolo\\AppData\\Local\\Fiji\\fiji-windows-x64.exe')
dicom_directory = "C:/Users/paolo/Desktop/821/CovidScans/manifest-1608266677008/MIDRC-RICORD-1A/MIDRC-RICORD-1A-419639-000082/08-02-2002-NA-CT CHEST WITHOUT CONTRAST-04614/3.000000-0.625mm bone alg-26970/"
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_directory)
reader = sitk.ImageSeriesReader()
reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_directory, series_IDs[0]))
image = reader.Execute()
image = sitk.Cast(image, sitk.sitkFloat64)
print("read the image")

# process image
smoothing_filter = sitk.SmoothingRecursiveGaussianImageFilter()
smoothing_filter.SetSigma(5)
# smoothing_filter = sitk.CurvatureAnisotropicDiffusionImageFilter()
# smoothing_filter.SetNumberOfIterations(5)
# smoothing_filter.SetConductanceParameter(3.0)
smoothed_image = smoothing_filter.Execute(image)
print("smoothed the image")

# threshold_filter = sitk.BinaryThresholdImageFilter()
# threshold_filter.SetLowerThreshold(-900.0)
# threshold_filter.SetUpperThreshold(-200.0)
# binary_image = threshold_filter.Execute(smoothed_image)
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

# opening_filter = sitk.BinaryMorphologicalOpeningImageFilter()
# opening_filter.SetKernelRadius(RADIUS)
# closing_filter = sitk.BinaryMorphologicalClosingImageFilter()
# closing_filter.SetKernelRadius(RADIUS)
# binary_image = closing_filter.Execute(opening_filter.Execute(binary_image))
# print("ran opening and closing")

mask_filter = sitk.MaskImageFilter()
lung_masked_image = mask_filter.Execute(image, binary_image)
non_lung_masked_image = mask_filter.Execute(image, inverse_binary_image)

# display image
image_viewer.Execute(lung_masked_image)
image_viewer.Execute(non_lung_masked_image)
exit()