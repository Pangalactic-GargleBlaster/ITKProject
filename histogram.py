import SimpleITK as sitk
from matplotlib import pyplot
image_viewer = sitk.ImageViewer()
image_viewer.SetApplication('C:\\Users\\admin\\AppData\\Local\\Fiji\\fiji-windows-x64.exe')
dicom_directory = "C:/Users/admin/Desktop/821/CovidScans/manifest-1608266677008/MIDRC-RICORD-1A/MIDRC-RICORD-1A-419639-000082/08-02-2002-NA-CT CHEST WITHOUT CONTRAST-04614/3.000000-0.625mm bone alg-26970/"
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_directory)
print(series_IDs)
reader = sitk.ImageSeriesReader()
reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_directory, series_IDs[0]))
image = reader.Execute()
print(f"Image size: {image.GetSize()}")
print(f"Image spacing: {image.GetSpacing()}")
print(f"First pixel: {image.GetPixel([0,0,0])}")
