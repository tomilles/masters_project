import numpy as np
import os
import torch
import torchaudio
import torchvision
import aifc
from matplotlib import pyplot as plt
import librosa

#stretching function from https://github.com/gaganbahga/time_stretch
def stretch(x, factor, nfft=2048):
    '''
    stretch an audio sequence by a factor using FFT of size nfft converting to frequency domain
    :param x: np.ndarray, audio array in PCM float32 format
    :param factor: float, stretching or shrinking factor, depending on if its > or < 1 respectively
    :return: np.ndarray, time stretched audio
    '''
    stft = librosa.core.stft(x, n_fft=nfft).transpose()  # i prefer time-major fashion, so transpose
    stft_rows = stft.shape[0]
    stft_cols = stft.shape[1]

    times = np.arange(0, stft.shape[0], factor)  # times at which new FFT to be calculated
    hop = nfft/4                                 # frame shift
    stft_new = np.zeros((len(times), stft_cols), dtype=np.complex_)
    phase_adv = (2 * np.pi * hop * np.arange(0, stft_cols))/ nfft
    phase = np.angle(stft[0])

    stft = np.concatenate( (stft, np.zeros((1, stft_cols))), axis=0)

    for i, time in enumerate(times):
        left_frame = int(np.floor(time))
        local_frames = stft[[left_frame, left_frame + 1], :]
        right_wt = time - np.floor(time)                        # weight on right frame out of 2
        local_mag = (1 - right_wt) * np.absolute(local_frames[0, :]) + right_wt * np.absolute(local_frames[1, :])
        local_dphi = np.angle(local_frames[1, :]) - np.angle(local_frames[0, :]) - phase_adv
        local_dphi = local_dphi - 2 * np.pi * np.floor(local_dphi/(2 * np.pi))
        stft_new[i, :] =  local_mag * np.exp(phase*1j)
        phase += local_dphi + phase_adv

    return librosa.core.istft(stft_new.transpose())


directory = "/Users/Tomi/Documents/bachata music/Bachata_normalized/1 bar/guira/"

target_frame = 36000

#loading and stretching audio clips

for filename in os.listdir(directory):
	if filename.endswith(".aiff"):

		waveform, sample_rate = torchaudio.load("{0}{1}".format(directory,filename))
		frames = waveform.size()

		rate = 11025
		waveform_resampled = torchaudio.transforms.Resample(sample_rate, new_freq=rate)(waveform[0,:].view(1,-1))

		frames = waveform_resampled.size()[1]

		shrinkrate = frames / target_frame		#stretching factor

		waveform_1 = waveform_resampled.numpy()[0]

		waveform_strethced_1 = stretch(waveform_1,shrinkrate,nfft = 500)

		# librosa.output.write_wav('{0}normalized/{1}'.format(directory,filename),waveform_strethced_1, rate)
		
