import nibabel
import numpy as np
import matplotlib.pyplot as plt


def reconstruct(clustered_patches, file_names, x_patches_per_image, y_patches_per_image):

    # Create a numpy array which will contain ordered patches
    # Since full black patches were discarded we initialize this array with full zeros (black)
    patch_size = clustered_patches.shape[-1]
    tot_images = 8  # TODO: automatize it
    patches_per_image = x_patches_per_image * y_patches_per_image
    tot_patches = patches_per_image * tot_images
    shape = (tot_patches, patch_size, patch_size)  # shape of list of gray patches
    ordered_patches = np.full(shape, 0)  # np.zeros(shape)
    # we iterate over the patches name and we put the correspondent clustered image in the array of ordered patches
    for i, file_name in enumerate(file_names):
        # pick the image id and the position
        data = []  # x,y,z,id
        file_name_extract = file_name[:-4].replace("_", " ")
        for word in file_name_extract.split():
            if word.isdigit():
                data.append(int(word))
        curr_index = patches_per_image * int((data[-2] - 60) / 5) + data[0]*y_patches_per_image + data[1] + 1
        ordered_patches[curr_index] = clustered_patches[i]

    final_images = np.zeros((tot_images, int(patch_size * patches_per_image / y_patches_per_image),
                            int(patch_size * patches_per_image / x_patches_per_image)))  # 8 images 768x576
    for iteration in range(tot_images):
        for i in range(x_patches_per_image):  # along the rows
            for j in range(y_patches_per_image):  # along the columns
                if j == 0:
                    toAttachH = ordered_patches[iteration * patches_per_image + i * y_patches_per_image + j]
                else:
                    toAttachH = np.hstack((toAttachH, ordered_patches[iteration * patches_per_image + i * y_patches_per_image + j]))
            if i == 0:
                toAttachV = toAttachH
            else:
                toAttachV = np.vstack((toAttachV, toAttachH))
        final_images[iteration] = toAttachV

    for i, image in enumerate(final_images):
        original_image = nibabel.load("images/skull_stripped_images/brain2_img.nii").get_fdata()[:, :, 60 + 5 * i]
        label = nibabel.load("images/skull_stripped_images/brain2_label.nii").get_fdata()[:, :, 60 + 5 * i]
        fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(15, 8))
        axs[0].imshow(original_image, "gray")
        axs[0].set_title("Original image")
        axs[1].imshow(image, "gray")
        axs[1].set_title("Reconstructed image")
        axs[2].imshow(label, "gray")
        axs[2].set_title("Ground truth")
        plt.show()

    return final_images
