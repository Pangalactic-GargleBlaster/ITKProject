import SimpleITK as sitk

metadata_path = "C:/Users/admin/Desktop/821/CovidScans/manifest-1608266677008/metadata.csv"
with open(metadata_path, "r") as metadata_file:
	lines = metadata_file.readlines()
	for line in lines:
		if line.split(",")[8] == "0.625mm bone alg":
			local_path = line.split(",")[15]
			dicom_directory = "C:/Users/admin/Desktop/821/CovidScans/manifest-1608266677008/"+local_path[1:]
			series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_directory)
			reader = sitk.ImageSeriesReader()
			reader.SetFileNames(sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_directory, series_IDs[0]))
			image = reader.Execute()
			print(image.GetSize())
exit()

