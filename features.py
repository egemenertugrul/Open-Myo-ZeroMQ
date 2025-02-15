import math

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import make_pipeline


def disjoint_segmentation(emg, n_samples=150):
    n_segments = int(np.floor(emg.shape[0] / n_samples))  # number of segments
    length = 0
    segmented_emg = np.zeros((n_samples, n_segments))
    for s in range(n_segments):
        for n in range(length, n_samples + length):
            print(n, length, s)
            segmented_emg[n - length, s] = emg[
                n]  # 2D matrix with a EMG signal divided in s segments, each one with n samples
        length = length + n_samples
    length = 0
    return segmented_emg


def disjoint_segmentation_2(emg, n_samples=150):
    signal = emg
    div = signal.shape[0] / n_samples
    n_segments = int(np.floor(div))  # number of segments
    needs_pad = int(np.ceil(div)) != n_segments

    if needs_pad:
        # frac1 = (signal.shape[0] / (n_samples / 2)) % 1
        frac2 = (signal.shape[0] / n_samples) % 1
        if frac2 > 0.5:
            n_pads = int(n_samples - np.round(frac2 * n_samples))
            # print(signal.shape[0], n_pads)
            signal = np.pad(signal, pad_width=((0, n_pads), (0, 0)), mode='median')
            n_segments = n_segments + 1

    # length = 0
    # segmented_emg = np.zeros((n_samples, n_segments))
    # for s in range(n_segments):
    #     for n in range(length, n_samples + length):
    #         print(n, length, s)
    #         segmented_emg[n - length, s] = emg[
    #             n]  # 2D matrix with a EMG signal divided in s segments, each one with n samples
    #     length = length + n_samples
    # length = 0
    segments = []
    for seg in range(n_segments):
        s = seg * n_samples
        segments.append(signal[s:s + n_samples])

    return np.array(segments)


def overlapping_segmentation(region, n_samples=52, skip=5):
    (region_x, region_y) = region
    total_duration = len(region_x)
    # expected_segment_count = math.floor(((total_duration - n_samples) / skip) + 1)
    segmented_emg = []

    if total_duration < n_samples:
        print(f"No sample of size {n_samples} is found.")
        return None
    elif total_duration == n_samples:
        segmented_emg.append((region_x, region_y))
    else:
        idx = 0
        while idx + n_samples <= total_duration:
            s = idx
            e = idx + n_samples
            segmented_emg.append((region_x[s:e], region_y[s:e]))
            idx += skip

    # print(expected_segment_count, len(segmented_emg))

    return np.array(segmented_emg)


def overlapping_segmentation_2(region, n_samples=52, skip=5):
    total_duration = len(region)
    # expected_segment_count = math.floor(((total_duration - n_samples) / skip) + 1)
    segmented_emg = []
    idx = 0
    while idx + n_samples <= total_duration:
        s = idx
        e = idx + n_samples
        segmented_emg.append(region[s:e])
        idx += skip

    # print(expected_segment_count, len(segmented_emg))

    return np.array(segmented_emg)


def mav(segment):
    mav = np.mean(np.abs(segment))
    return mav


# MAX: 128
def rms(segment):
    rms = np.sqrt(np.mean(np.power(segment, 2)))
    return rms


def var(segment):
    var = np.var(segment)
    return var


def ssi(segment):
    ssi = np.sum(np.abs(np.power(segment, 2)))
    return ssi


# MAX: segment length - 1 (e.g. 51)
def zc(segment):
    nz_segment = list()
    nz_indices = np.nonzero(segment)[0]  # Finds the indices of the segment with nonzero values
    for i in nz_indices:
        nz_segment.append(segment[i])  # The new segment contains only nonzero values
    nz_segment_length = len(nz_segment)
    zc = 0
    for n in range(nz_segment_length - 1):
        if ((nz_segment[n] * nz_segment[n + 1] < 0) and np.abs(nz_segment[n] - nz_segment[n + 1]) >= 1e-4):
            zc = zc + 1
    return zc


# MAX: 13005
def wl(segment):
    wl = np.sum(np.abs(np.diff(segment)))
    return wl


if __name__ == '__main__':
    a = [-128, 127] * 26
    print(zc(a))


# def ssc(segment):
#    N = len(segment)
#    ssc = 0
#    for n in range(1,N-1):
#        if (segment[n]-segment[n-1])*(segment[n]-segment[n+1])>=1e-4:
#            ssc += 1
#    return ssc

def ssc(segment):
    segment_length = len(segment)
    ssc = 0
    for n in range(1, segment_length - 1):
        if ((segment[n] > segment[n - 1] and segment[n] > segment[n + 1])
                or (segment[n] < segment[n - 1] and segment[n] < segment[n + 1])
                and ((np.abs(segment[n] - segment[n + 1]) >= 1e-4)
                     or (np.abs(segment[n] - segment[n - 1]) >= 1e-4))):
            ssc += 1
    return ssc


def wamp(segment):
    segment_length = len(segment)
    wamp = 0
    for n in range(segment_length - 1):
        if np.abs(segment[n] - segment[n + 1]) > 1e-4:
            wamp += 1
    return wamp


def features(segment, feature_list):
    features = np.zeros((1, len(segment) * len(feature_list)))
    i = 0
    for feature in feature_list:
        features[0, i] = feature(segment[0])
        features[0, i + 1] = feature(segment[1])
        features[0, i + 2] = feature(segment[2])
        features[0, i + 3] = feature(segment[3])
        features[0, i + 4] = feature(segment[4])
        features[0, i + 5] = feature(segment[5])
        features[0, i + 6] = feature(segment[6])
        features[0, i + 7] = feature(segment[7])
        i += len(segment)
    return features


def feature_scaling(feature_matrix, target, reductor=None, scaler=None):
    lda = LDA(n_components=2)
    minmax = MinMaxScaler(feature_range=(-1, 1))
    if not reductor:
        reductor = lda.fit(feature_matrix, target)
    feature_matrix_lda = reductor.transform(feature_matrix)
    if not scaler:
        scaler = minmax.fit(feature_matrix_lda)
    feature_matrix_scaled = scaler.transform(feature_matrix_lda)
    return feature_matrix_scaled, reductor, scaler


def generate_target(n_samples, labels):
    target = list()
    for l in range(len(labels)):
        for s in range(n_samples):
            target.append(labels[l])
    target_array = np.array(target).ravel()
    return target_array
