# setup sitk
import SimpleITK as sitk
from matplotlib import pyplot
image_viewer = sitk.ImageViewer()
image_viewer.SetApplication('C:\\Users\\admin\\AppData\\Local\\Fiji\\fiji-windows-x64.exe')

# import one image
dicom_directory = "C:/Users/admin/Desktop/821/CovidScans/manifest-1608266677008/MIDRC-RICORD-1A/MIDRC-RICORD-1A-419639-000082/08-02-2002-NA-CT CHEST WITHOUT CONTRAST-04614/3.000000-0.625mm bone alg-26970/"
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_directory)
print(series_IDs)
reader = sitk.ImageSeriesReader()
reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_directory, series_IDs[0]))
image = reader.Execute()
print(f"Image size: {image.GetSize()}")
print(f"Image spacing: {image.GetSpacing()}")
print(f"First pixel: {image.GetPixel([0,0,0])}")

# calculate the histogram manually
x_size, y_size, z_size = image.GetSize()
pixel_value_counts = {}
for z in range(1):
	for y in range(y_size):
		for x in range(x_size):
			pixel = image.GetPixel([x,y,z])
			if pixel > -2000:
				current_pixel_value_count = pixel_value_counts.get(pixel, 0)
				pixel_value_counts[pixel] = current_pixel_value_count + 1
	print(f'processed one slice: {z}')

# plot the histogram
pyplot.scatter(pixel_value_counts.keys(), pixel_value_counts.values())
pyplot.show()