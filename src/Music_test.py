import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.utils import np_utils
music = numpy.loadtxt("D:/state_matrix.txt")
#music = numpy.loadtxt("/home/test/xurong/state_matrix.txt")
data = music[range(2800),:]
test = music[range(2800,3514),:]
seq_length = 16 # 之后试取32
dataX = []
dataY = []
for i in range(0, len(data) - seq_length, 1):
    seq_in = data[i:i + seq_length]
    seq_out = data[i + seq_length]
    dataX.append(seq_in)
    dataY.append(seq_out)
    #print( seq_in, '->', seq_out)

testX = []
testY = []
for i in range(0, len(test) - seq_length, 1):
    seq_in = test[i:i + seq_length]
    seq_out = test[i + seq_length]
    testX.append(seq_in)
    testY.append(seq_out)

X = numpy.reshape(dataX, (len(dataX), seq_length, 128)) #[samples, time steps, features]
y = numpy.reshape(dataY, (len(dataY), 128)) 
#y = np_utils.to_categorical(dataY)
model = Sequential()
model.add(LSTM(32, input_shape=(X.shape[1], X.shape[2])))
model.add(Dense(y.shape[1], activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X, y, epochs=50, batch_size=1, verbose=1)

model.summary()

testx = numpy.reshape(testX, (len(testX), seq_length, 128)) #[samples, time steps, features]
testy = numpy.reshape(testY, (len(testY), 128)) 
score = model.evaluate(testx, testy,batch_size=1, verbose=1)
print(score[1])