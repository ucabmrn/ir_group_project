import matplotlib.pyplot as plt
import numpy as np
import time
import csv
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
np.random.seed(1234)


def data_power_consumption(path_to_dataset,
                           sequence_length=50,
                           ratio=1.0):

    max_values = ratio * 2049280

    with open(path_to_dataset) as f:
        data = csv.reader(f, delimiter=";")
        power = []
        nb_of_values = 0
        for line in data:
            try:
                power.append([float(line[6]), float(line[7]), float(line[8])])
                nb_of_values += 1
            except ValueError:
                pass
            # 2049280.0 is the total number of valid values, i.e. ratio = 1.0
            if nb_of_values >= max_values:
                break

    print "Data loaded from csv. Formatting..."

    result = []
    for index in range(len(power) - sequence_length):
        result.append(power[index: index + sequence_length])
    result = np.array(result)  # shape (2049230, 50)

    result_mean = result.mean()
    result -= result_mean
    print "Shift : ", result_mean
    print "Data  : ", result.shape

    row = round(0.9 * result.shape[0])
    train = result[:row, :]
    np.random.shuffle(train)
    X_train = train[:, :-1]
    y_train = train[:, -1]
    X_test = result[row:, :-1]
    y_test = result[row:, -1]

    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 3))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 3))

    return [X_train, y_train, X_test, y_test]


def build_model():
    model = Sequential()
    layers = [3, 50, 100, 3]

    model.add(LSTM(
        input_dim=layers[0],
        output_dim=layers[1],
        return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(
        layers[2],
        return_sequences=False))
    model.add(Dropout(0.2))

    model.add(Dense(
        output_dim=layers[3]))
    model.add(Activation("linear"))

    start = time.time()
    model.compile(loss="mse", optimizer="rmsprop")
    print "Compilation Time : ", time.time() - start
    return model


def run_network(model=None, data=None):
    global_start_time = time.time()
    epochs = 1
    ratio = 0.1
    sequence_length = 50
    path_to_dataset = '../../data/house/household_power_consumption.txt'

    if data is None:
        print 'Loading data... '
        X_train, y_train, X_test, y_test = data_power_consumption(
            path_to_dataset, sequence_length, ratio)
    else:
        X_train, y_train, X_test, y_test = data

    print '\nData Loaded. Compiling...\n'

    if model is None:
        model = build_model()

    try:
        model.fit(
            X_train, y_train,
            batch_size=512, nb_epoch=epochs, validation_split=0.05)
        predicted = model.predict(X_test)
        # predicted = np.reshape(predicted, (predicted.size,))
    except KeyboardInterrupt:
        print 'Training duration (s) : ', time.time() - global_start_time
        return model, y_test, 0

    # try:
    #     fig = plt.figure()
    #     ax = fig.add_subplot(111)
    #     ax.plot(y_test[:100, 0])
    #     plt.plot(predicted[:100, 0])
    #     plt.show()
    except Exception as e:
        print str(e)
    print 'Training duration (s) : ', time.time() - global_start_time

    return model, y_test, predicted

if __name__ == '__main__':
   model, y_test, predicted = run_network()
   fig1 = plt.figure()
   ax1 = fig1.add_subplot(111)
   ax1.plot(y_test[:1000, 0], label = "True Values: sub_metering1")
   ax1.plot(predicted[:1000, 0], label = "Predicted Values: sub_metering1")
   plt.legend()
   plt.title("True Values and Predicted Values of sub_metering1 for the first 1000 samples")

   fig2 = plt.figure()
   ax2 = fig2.add_subplot(111)
   ax2.plot(y_test[:1000, 1], label = "True Values: sub_metering2")
   ax2.plot(predicted[:1000, 1], label = "Predicted Values: sub_metering2")
   plt.legend()
   plt.title("True Values and Predicted Values of sub_metering2 for the first 1000 samples")

   fig3 = plt.figure()
   ax3 = fig3.add_subplot(111)
   ax3.plot(y_test[:1000, 2], label = "True Values: sub_metering3")
   ax3.plot(predicted[:1000, 2], label = "Predicted Values: sub_metering3")
   plt.legend()
   plt.title("True Values and Predicted Values of sub_metering3 for the first 1000 samples")



   MSE = np.mean(np.square(y_test-predicted))
   # plt.xlim([0, 1000])
   print "the mean squared test error is: ", MSE
   plt.show()