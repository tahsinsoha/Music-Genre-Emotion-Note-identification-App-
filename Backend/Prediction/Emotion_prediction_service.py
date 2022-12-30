import librosa
import tensorflow as tf
import numpy as np
import math

SAVED_MODEL_PATH = "./EmoModel.h5"
SAMPLES_TO_CONSIDER = 22050
SAMPLE_RATE = 22050
TRACK_DURATION = 4  # measured in seconds
SAMPLES_PER_TRACK = SAMPLE_RATE * TRACK_DURATION

class _Emotion_prediction_service:
    """Singleton class for keyword spotting inference with trained models.
    :param model: Trained model
    """

    model = None
    _mapping = [
        "Neutral",
        "Calm",
        "Happy",
        "Sad"
    ]
    _instance = None


    def predict_emotion(self, file_path):
        """
        :param file_path (str): Path to audio file to predict
        :return predicted_keyword (str): Keyword predicted by the model
        """

        # extract MFCC
        MFCCs = self.preprocess(file_path)

        # we need a 4-dim array to feed to the model for prediction: (# samples, # time steps, # coefficients, 1)
        MFCCs = MFCCs[np.newaxis, ...,np.newaxis]
        print("shape", MFCCs.shape)
        # get the predicted label
        predictions = self.model.predict(MFCCs)
        print(predictions)
        predicted_index = np.argmax(predictions, axis= 1)
        predicted_keyword = np.array(self._mapping)[predicted_index.astype(int)]
        return predicted_keyword[0]


    def preprocess(self, file_path, num_mfcc=13, n_fft=2048, hop_length=512, num_segments=2):
        """Extract MFCCs from audio file.
        :param file_path (str): Path of audio file
        :param num_mfcc (int): # of coefficients to extract
        :param n_fft (int): Interval we consider to apply STFT. Measured in # of samples
        :param hop_length (int): Sliding window for STFT. Measured in # of samples
        :return MFCCs (ndarray): 2-dim array with MFCC data of shape (# time steps, # coefficients)
        """

        # load audio file
        signal, sample_rate = librosa.load(file_path, sr= SAMPLE_RATE)

        samples_per_segment = int(SAMPLES_PER_TRACK / num_segments)
        num_mel_vectors_per_segment = math.ceil(samples_per_segment / hop_length)


        print("Eikhane ", SAMPLES_PER_TRACK, num_segments)
                # process all segments of audio file
        for d in range(num_segments):

                    # calculate start and finish sample for current segment
            start = samples_per_segment * d
            finish = start + samples_per_segment

                    # extract mfcc
            mfcc = librosa.feature.mfcc(signal[start:finish], sample_rate, n_mfcc=num_mfcc, n_fft=n_fft,
                                                hop_length=hop_length)
            mfcc = mfcc.T

            print("Eikhane ashe", samples_per_segment, start, finish, mfcc.shape)

            if len(mfcc) == num_mel_vectors_per_segment:
               return mfcc


def Emotion_prediction_service():
    """Factory function for Keyword_Spotting_Service class.
    :return _Keyword_Spotting_Service._instance (_Keyword_Spotting_Service):
    """

    # ensure an instance is created only the first time the factory function is called
    if _Emotion_prediction_service._instance is None:
        _Emotion_prediction_service._instance = _Emotion_prediction_service()
        _Emotion_prediction_service.model = tf.keras.models.load_model(SAVED_MODEL_PATH)
    return _Emotion_prediction_service._instance




if __name__ == "__main__":

    # create 2 instances of the keyword spotting service
    eps = Emotion_prediction_service()
    eps1 = Emotion_prediction_service()

    # check that different instances of the keyword spotting service point back to the same object (singleton)
    assert eps is eps1

    # make a prediction
    keyword = eps.predict_emotion("/content/drive/MyDrive/Emotions_original/disco/disco.00009.wav")
    print(keyword)