# ML-HPGe-timing
Deep learning-based pulse shape analysis for improving the time resolution of the high purity Germanium detectors

## Description

### MuX experiment (PSI, Switzerland)

When registering signals by a particle detector in many cases it's crutial to know exact time of an particular event. For example, [the MuX experiment](https://www.psi.ch/en/ltp/mux) performs muonic atom spectroscopy by detecting the X-rays emmited from muonic atom from the muonic atoms (the hydrogen-like bound state of a negative muon with a nucleus). The X-rays are detected by high-purity germanium detectors, and knowing the exact time of a X-ray hit is crutial for the experiment aims.

### ELET algorithms vs deep learning-based approach

Conventional Extrapolated Leading-Edge timing (ELET) algorithms are used for improving the time resolution of particle detectors. However, tese algoritms have some significant cons:
* a need of a single set of parameters for predefined function for whole energy range;
* manual optimization.

Another possible way is using of deep learning-based aprroaches by building and training a neural network that can learn relationship between signal shape and time of signal rising edge. It would allow to:
* automate the process;
* More generalized approach: the builded network can be used for different different detectors with different electrical characteristics (gain, etc.)

the pre-trained CNN-based encoder (for compression of the original signal and extracting a feature vector) followed by a couple of dense layers (for determining the exact time of the signal rising edge). Pending task. Achievement of fairly good and promising interim results compared to conventional, non-ML based, algorithms: comparable and even slightly better time resolution, good metrics (relatively small MAE value, acceptable MSE value, r-squared value ~0.85-0.9), reproducible results for different datasets (with ~300-800k signal samples).

## NN for determining the time of the signal rising edge

### The idea

The registered signal is digitized and represented as 1-dimentional vector with 300 of ADC samples. Thus this is a tipical time series analysis task.

(IMAGE: Signal samples.png)
![Signal samples](images/Signal_samples.png)

At the first stage the CNN-based Autoencoder is used to compress the original signal and extract a 50-dimensional feature vector at the bottleneck:

(IMAGE: Autoencoder.png)

The the Decoder part of Autoencoder is replaced by a couple of regular ANN consisting of 2 dence layers:
(IMAGE:  En_TimeDet.png)
At this stage Encoder is already pre-trained and fixed, only dence layers part is fitted to the data. The original values time of signal rising edge t0 are used as labels.

The pre-trained Encoder + Dence layers architecture is picked isntead of just ANN of several dence layers because using of CNN in the Encoder part allows to reduce the dimension of input data by 6 times. Secondly CNNs use fewer parameters.
For example, the structure of the NN for determining the signal rising edge time value is presented bellow:
(IMAGE: En_TimeDet_Structure.png)
The Encoder consing of 4 Conv1D convolutional layers (with 20 filters and kernel size equals to 7), each followed by an AveragePooling1D layer. Then here comes a couple of Dence layers with 128, 64 and 1 neurons. The output of the last Dence layer gives the predicted value of t0 predicted. The NN with such desing has `20, 790 parameters` in total (including 5, 941 pre-traned Encoder parameters):
(IMAGE: NN_Architecture.png)
Connecting the 300-dimentional input layer directly with only 128 and 64 interim fully connected Dence layers gives `46, 849 parameters` in total. Then use of CNN-based Encoder part allows a gain in number of model parameters in more than twice.

### Detailed current structure of the NN

(IMAGE: Detailed_NNStructure.png)
![Detailed NN Structure](images/Detailed_NNStructure.png)
### Model highligts 
* Dimentionallity of the signal is reduced by pooling layers in the Encoder part in 2 steps: at first in 3 times and then in 2 times, in 6 times in total.
* Number of filters and kernel size were optimized using the GridSearch and Tensorboard toolkit for vizualisation of the results. The values of 20 and 7, respectively, were found as optimal ones based on the performance of the Autoencoder.
* RobustScaller was choosen for scalling the signals (input features) due to the presence of outliers in signals after splitting the dataset and fitting the scaller only on the part used for training the NN.

## Current results
The NN shows good and promising interim results compared to conventional ELET algorithms:
|Algorithm| Time resolution |
|--|--|
| ELET | typically up to 10 ns |
| DL-based | here: ~ 10 ns* |
\* *avarage time resolition is ~2.6 of ADC counts, which is equivalent of ~10 ns, considering the ADC sampling rate of 250 MHz* 

According to the metrics, MSE and RMSE values are higher than MAE value, which might be caused by data quality (noises, errors in manual labeling of datasets that were used for training, etc.)
