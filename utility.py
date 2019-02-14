from yaml_reader import YamlReader


def write_to_file(actual_data, yml: YamlReader, name):
    ftune = yml.tuningfrequency()
    with open(name+'.txt', 'w') as f:
        f.write('Recording name: ' + name + ', ' +
                'Start record [UTC]: ' + str(yml.start_record_time()) + ', ' +
                'End record [UTC]: ' + str(yml.end_record_time()) + ', ' +
                'TCA [s after start of recording]: ' + str(actual_data["tca"]) + ', ' +
                'FCA [Hz]: ' + str(actual_data["fca"] + ftune) + '\n')
        f.write('Time after start of recording [s], Left Signal Frequency [Hz], Left Signal Power [dB], '
                'Center Frequency [Hz], Right Signal Frequency [Hz], Right Signal Power [dB]\n')
        for time, left, lpower, center, right, rpower in zip(actual_data["left"]["times"],
                                                             actual_data["left"]["freqs"],
                                                             actual_data["left"]["power"],
                                                             actual_data["carrier"]["freqs"],
                                                             actual_data["right"]["freqs"],
                                                             actual_data["right"]["power"]):
            f.write(str(time) + ', ' + str(left + ftune) + ', ' + str(lpower) + ', ' + str(center + ftune) + ', '
                    + str(right + ftune) + ', ' + str(rpower) + '\n')
        f.close()
