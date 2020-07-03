import os

class CycleGAN():
	def __init__(self):
		self.lib_path = "ML_models/CycleGAN_lib"
		self.style_name_to_model_name = {
			"Van Gogh": "van_gogh",
			"Cezanne": "cezanne",
			"Monet": "monet",
			"Ukiyoe": "ukiyoe"
		}

	def process(self, img_path, style_name):
		style_name = self.style_name_to_model_name[style_name]
		checkpoints = "--checkpoints_dir ML_models/models"
		dataroot = "--dataroot {}".format(img_path)
		model_name = "--name {}".format(style_name)
		result_dir = "--results_dir {}".format(img_path)
		other_settings = "--model test --no_dropout --gpu_ids -1"
		os.system("python {}/test.py {} {} {} {} {} ".format(
			self.lib_path, checkpoints, dataroot, model_name,
			result_dir, other_settings
		))
		return "{}/{}/test_latest/images/photo_fake.png".format(img_path, style_name)

		