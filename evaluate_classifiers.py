from tensorflow import keras
from image_mod_functions import standardize_image, rgb2gray
import functools
import numpy as np
import time
import create_dataset
import classifier_definitions
import matplotlib.pyplot as plt
import loader_class


# define custom metric, needed as a dependency in keras.models.load_model
top3_acc = functools.partial(keras.metrics.top_k_categorical_accuracy, k=3)
top3_acc.__name__ = 'top3_acc'
dependencies = {'top3_acc' : top3_acc}

# load the dataset
dataLoader = create_dataset.DataLoader()
dataset = dataLoader.getDataset()[0]
# the eval dataset will not use the first 300 images
eval_dataset = dataLoader.getDataset(start_index=300)[0]

dataset = dataset.shuffle(100)

# performs timing and accuracy evaluations on a given model
# model must exist as a file in the /trained_models folder
def test_model(model_name, model_params, test_batch_size):
	model_type = model_params[0]
	layers = model_params[1]
	drop = model_params[2]
	lr = model_params[3]
	reg = model_params[4]
	batch = model_params[5]
	# load the model
	current_model = keras.models.load_model(f"trained_models/{model_name}", custom_objects=dependencies)
	timings = test_batch_size
	j = 0

	# determine accuracy on the final six people's expressions
	current_set = eval_dataset.batch(10)
	accuracy = current_model.evaluate(current_set)

	# for each total data batch, time the predictions
	for b in test_batch_size:
		current_set = dataset.batch(b)
		print(f"Timing batches of size {b} for {model_name}")

		i = 0
		average = 0

		for current_batch in current_set:
			startTime = time.time()
			current_model.predict(current_batch)
			batchPredictTime = time.time() - startTime
			if i == 0:
				average = batchPredictTime
			else:
				total = (average * i) + batchPredictTime
				average = total / (i + 1)

			i = i + 1
		timings[j] = float(average)
		j = j + 1

	# print(f"Times: {timings}")
	# return a numpy array of the parameters and evaluation data of the given model
	return np.concatenate((model_params, timings, float(accuracy[1]), float(accuracy[2])), axis=None)


def eval_best_models():
	# top 4 most successful SVMs
	svm1 = test_model("SVM-0#l3-d0.2-lr0.001-r0.1-b30.h5", ['SVM', 3, 0.2, 0.001, 0.1, 30], [1, 5, 10, 20])
	svm2 = test_model("SVM-1#l3-d0.4-lr0.001-r0.01-b30.h5", ['SVM', 3, 0.4, 0.001, 0.01, 30], [1, 5, 10, 20])
	svm3 = test_model("SVM-2#l3-d0.5-lr0.001-r0.01-b60.h5", ['SVM', 3, 0.5, 0.001, 0.01, 60], [1, 5, 10, 20])
	svm4 = test_model("SVM-3#l3-d0.3-lr0.001-r0.1-b60.h5", ['SVM', 3, 0.3, 0.001, 0.1, 60], [1, 5, 10, 20])

	# Latex format
	print(f"{svm1[0]} & {svm1[1]} & {svm1[2]} & {svm1[3]} & {svm1[4]} & {svm1[5]} & {svm1[6]:.4f} & {svm1[7]:.4f} & {svm1[8]:.4f} & {svm1[9]:.4f} & {svm1[10]:.4f} & {svm1[11]} & \hline")
	print(f"{svm2[0]} & {svm2[1]} & {svm2[2]} & {svm2[3]} & {svm2[4]} & {svm2[5]} & {svm2[6]:.4f} & {svm2[7]:.4f} & {svm2[8]:.4f} & {svm2[9]:.4f} & {svm2[10]:.4f} & {svm2[11]} & \hline")
	print(f"{svm3[0]} & {svm3[1]} & {svm3[2]} & {svm3[3]} & {svm3[4]} & {svm3[5]} & {svm3[6]:.4f} & {svm3[7]:.4f} & {svm3[8]:.4f} & {svm3[9]:.4f} & {svm3[10]:.4f} & {svm3[11]} & \hline")
	print(f"{svm4[0]} & {svm4[1]} & {svm4[2]} & {svm4[3]} & {svm4[4]} & {svm4[5]} & {svm4[6]:.4f} & {svm4[7]:.4f} & {svm4[8]:.4f} & {svm4[9]:.4f} & {svm4[10]:.4f} & {svm4[11]} & \hline")

	# resize the dataset for the CNNs
	dataset = classifier_definitions.reduceSize(dataset)
	eval_dataset = classifier_definitions.reduceSize(eval_dataset)

	# top 4 most successful CNNs
	cnn1 = test_model("CNN-0#l2-d0.2-lr0.001-b60.h5", ['CNN', 2, 0.2, 0.001, 'na', 60], [1, 5, 10, 20])
	cnn2 = test_model("CNN-1#l2-d0.4-lr0.001-b60.h5", ['CNN', 2, 0.4, 0.001, 'na', 60], [1, 5, 10, 20])
	cnn3 = test_model("CNN-2#l2-d0.3-lr0.001-b60.h5", ['CNN', 2, 0.3, 0.001, 'na', 60], [1, 5, 10, 20])
	cnn4 = test_model("CNN-3#l2-d0.5-lr0.001-b60.h5", ['CNN', 2, 0.5, 0.001, 'na', 60], [1, 5, 10, 20])

	print(f"{cnn1[0]} & {cnn1[1]} & {cnn1[2]} & {cnn1[3]} & NA & {cnn1[5]} & {cnn1[6]:.4f} & {cnn1[7]:.4f} & {cnn1[8]:.4f} & {cnn1[9]:.4f} & {cnn1[10]:.4f} & {cnn1[11]} & \hline")
	print(f"{cnn2[0]} & {cnn2[1]} & {cnn2[2]} & {cnn2[3]} & NA & {cnn2[5]} & {cnn2[6]:.4f} & {cnn2[7]:.4f} & {cnn2[8]:.4f} & {cnn2[9]:.4f} & {cnn2[10]:.4f} & {cnn2[11]} & \hline")
	print(f"{cnn3[0]} & {cnn3[1]} & {cnn3[2]} & {cnn3[3]} & NA & {cnn3[5]} & {cnn3[6]:.4f} & {cnn3[7]:.4f} & {cnn3[8]:.4f} & {cnn3[9]:.4f} & {cnn3[10]:.4f} & {cnn3[11]} & \hline")
	print(f"{cnn4[0]} & {cnn4[1]} & {cnn4[2]} & {cnn4[3]} & NA & {cnn4[5]} & {cnn4[6]:.4f} & {cnn4[7]:.4f} & {cnn4[8]:.4f} & {cnn4[9]:.4f} & {cnn4[10]:.4f} & {cnn4[11]} & \hline")


# compare sample predictions from the top 2 models
def sample_best_models():
	# load the two models from memory
	best_svm = loader_class.ReadyModel("BestSVM")
	best_cnn = loader_class.ReadyModel("BestCNN")

	best_svm.model.summary()
	best_cnn.model.summary()

	dataLoader = create_dataset.DataLoader()
	dataset = dataLoader.getDataset(start_index=300)[0]

	# grid output dimensions
	batch_size = 6
	num_columns = 3

	print("Loading batch of sample...", end="\r", flush=True)
	batchSample = iter(dataset.shuffle(200).batch(batch_size)).next()[0].numpy()  # pulls 5 sample images
	print("Making batch prediction...", end="\r", flush=True)
	svm_results = best_svm.classify(batchSample)
	cnn_results = best_cnn.classify(batchSample)

	fig3 = plt.figure(constrained_layout=True)
	rows = (batch_size // num_columns)
	# plt.title("Best SVM Predictions")

	if batch_size % num_columns != 0:
		rows = rows + 1

	gs = fig3.add_gridspec(rows * 3, num_columns)

	for index, result in enumerate(svm_results):
		current_axis = fig3.add_subplot(
			gs[((index // num_columns) * 3):((index // num_columns) * 3 + 2), (index % num_columns)])
		barchart_1 = fig3.add_subplot(gs[(index // num_columns) * 3 + 2, (index % num_columns)])
		current_axis.imshow(batchSample[index] / 255)  # normalize to prevent clipping
		current_axis.set_axis_off()
		for subIndex, emote in enumerate(result):
			barchart_1.bar(emote[1], emote[0] * 100)

	plt.show()
	plt.clf()

	fig3 = plt.figure(constrained_layout=True)
	rows = (batch_size // num_columns)
	# plt.title("Best CNN Predictions")

	if batch_size % num_columns != 0:
		rows = rows + 1

	gs = fig3.add_gridspec(rows * 3, num_columns)

	for index, result in enumerate(cnn_results):
		current_axis = fig3.add_subplot(
			gs[((index // num_columns) * 3):((index // num_columns) * 3 + 2), (index % num_columns)])
		barchart_1 = fig3.add_subplot(gs[(index // num_columns) * 3 + 2, (index % num_columns)])
		current_axis.imshow(batchSample[index] / 255)  # normalize to prevent clipping
		current_axis.set_axis_off()
		for subIndex, emote in enumerate(result):
			barchart_1.bar(emote[1], emote[0] * 100)

	plt.show()


sample_best_models()
