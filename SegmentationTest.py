import SimpleITK as sitk
# import matplotlib.pyplot as plt
import numpy as np

print(sitk.Version())
base_file_path = 'C:/Users/paolo'

image_viewer = sitk.ImageViewer()
image_viewer.SetApplication(base_file_path + '\\AppData\\Local\\Fiji\\fiji-windows-x64.exe')
dicom_directory = base_file_path + "/Desktop/821/CovidScans/manifest-1608266677008/MIDRC-RICORD-1A/MIDRC-RICORD-1A-419639-000082/08-02-2002-NA-CT CHEST WITHOUT CONTRAST-04614/3.000000-0.625mm bone alg-26970/"
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_directory)
print(series_IDs)
reader = sitk.ImageSeriesReader()
reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_directory, series_IDs[0]))
image = reader.Execute()
#Casts the simple itk image to float64 so we can have fraction in filter
image = sitk.Cast(image, sitk.sitkFloat64)

#anisotropic filter
anisotropic_filter = sitk.CurvatureAnisotropicDiffusionImageFilter()

#filter parameters
anisotropic_filter.SetNumberOfIterations(5)
anisotropic_filter.SetConductanceParameter(3.0)

output_image = anisotropic_filter.Execute(image)

#Binary Thresholding
output_image = sitk.BinaryThreshold(output_image, lowerThreshold=-600, upperThreshold=-300,
                      insideValue=1, outsideValue=0)

kernel_radius = 2

# Opening: removes small noise
print("Applying morphological opening")
opening_filter = sitk.BinaryMorphologicalOpeningImageFilter()
opening_filter.SetKernelRadius(kernel_radius)
opening_filter.SetKernelType(sitk.sitkBall)
opening_filter.SetForegroundValue(1)
output_image = opening_filter.Execute(output_image)

# # Closing: fills small holes
# print("Applying morphological closing")
# closing_filter = sitk.BinaryMorphologicalClosingImageFilter()
# closing_filter.SetKernelRadius(kernel_radius)
# closing_filter.SetKernelType(sitk.sitkBall)
# closing_filter.SetForegroundValue(1)
# covid_closed = closing_filter.Execute(output_image)

image_viewer.Execute(output_image)