import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np

print(sitk.Version())

image_viewer = sitk.ImageViewer()
image_viewer.SetApplication("C:\\Users\\kevta\\Fiji\\fiji-windows-x64.exe")
#image_viewer.Execute(sitk.ReadImage("C:\\Users\\kevta\\VSProjects\\TestComp\\compiling.png"))
image = sitk.ReadImage("C:\\Users\\kevta\\VSProjects\\TestComp\\compiling.png")
#Casts the simple itk image to float64 so we can have fraction in filter
image = sitk.Cast(image, sitk.sitkFloat64)

#averaging filter
kernel_data = np.array([[1, 1, 1], 
                        [1, 1, 1], 
                        [1, 1, 1]], dtype=np.uint8)/9.0
print(f"according to numpy {kernel_data.dtype}")
kernel = sitk.GetImageFromArray(kernel_data)
convolution_filter = sitk.ConvolutionImageFilter()
output_image = convolution_filter.Execute(image, kernel)
image_viewer.Execute(output_image)
