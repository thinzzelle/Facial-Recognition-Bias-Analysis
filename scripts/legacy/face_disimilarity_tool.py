from deepface import DeepFace
import time
import tensorflow as tf
from datetime import datetime
import multiprocessing
from functools import partial

exception_list = []
exception_write_to_file_count = 0


def _write_exceptions_to_file(model):
    filename = 'tmp2/' + model + '/exceptions.txt'
    with open(filename, 'w') as file:
        for exception in exception_list:
            file.write(str(exception) + '\n')

def _calculate_scores(race_metrics):
    total_test_count = race_metrics['Total Test Count']
    tp = race_metrics['True Positive']
    fp = race_metrics['False Positive']
    tn = race_metrics['True Negative']
    fn = race_metrics['False Negative']
    test_count = race_metrics['Total Test Count']

    if tp + fp == 0:
        precision = 'N/A'
    else:
        precision = tp / (tp + fp)

    if tp + fn == 0:
        recall = 'N/A'
    else:
        recall = tp / (tp + fn)

    if precision == 'N/A' or recall == 'N/A':
        f1_score = 'N/A'
    elif precision + recall == 0:
        f1_score = 'N/A'
    else:
        f1_score = 2 * precision * recall / (precision + recall)

    if test_count == 0:
        accuracy = 'N/A'
    else:
        accuracy = (tp + tn) / test_count

    if tn + fp == 0:
        specificity = 'N/A'
    else:
        specificity = tn / (tn + fp)

    return f1_score, accuracy, recall, precision, specificity

def _write_final_results_to_file(races, metrics, model, detector):
    filename = 'tmp2/' + model + '/Race_results.txt'

    try:
        with open(filename, 'w') as file:
            file.write(f'Model: {model}\nDetector: {detector}\n')
            for race in races:
                race_metrics = metrics[race]
                file.write(f'\n{race}\n')
                for key, value in race_metrics.items():
                    if key == 'Total Test Time':
                        file.write('\n')
                    file.write(f'\t{key}: {value}\n')

                test_time = race_metrics['Total Test Time']
                test_count = race_metrics['Total Test Count']
                average_test_time = test_time / test_count

                f1_score, accuracy, recall, precision, specificity =  _calculate_scores(race_metrics)

                file.write(f'\tAvg Test Time: {average_test_time} \n\n')
                file.write(f'\tF1 Score: {f1_score}\n')
                file.write(f'\tAccuracy: {accuracy}\n')
                file.write(f'\tRecall: {recall}\n')
                file.write(f'\tPrecision: {precision}\n')
                file.write(f'\tSpecificity: {specificity}\n')
    except Exception as e:
        print(str(e), race, model, detector)
        exception_info = [str(e), race, model, detector]
        exception_list.append(exception_info)
    

def _write_test_result_to_file(template_folder, template_image_index, test_folder, test_image_index, result, results_file, test_time):
    if len (template_folder) < 8:
        template_folder += ' '
    if len (test_folder) < 8:
        test_folder += ' '

    results_file.write(
        f'{template_folder}\t\t'
        f'{template_image_index}\t\t'
        f'{test_folder}\t\t'
        f'{test_image_index}\t\t'
        f'{int(result["verified"])}\t\t')

    if result['verified']:
        results_file.write("fp\t\t")
    elif not result['verified']:
        results_file.write("tn\t\t")
    else:
        results_file.write("error in _write_test_result_to_file()\t\t")

    results_file.write(f'{test_time:{1}.{2}}\n')


def _print_results_to_console(races, metrics, model, detector):
    print("\nModel:", model)
    print("Detector", detector)
    for race in races:
        print("\n", race)
        race_metrics = metrics[race]
        for key, value in race_metrics.items():
            if key == 'Total Test Time':
                print()
            print('\t', key + ':', value)

        test_time = race_metrics['Total Test Time']
        test_count = race_metrics['Total Test Count']
        average_test_time = test_time / test_count
        print(f'\tAvg Test Time: {average_test_time}\n')

        try:
            f1_score, accuracy, recall, precision, specificity =        _calculate_scores(race_metrics)

            print(f'\tF1 Score: {f1_score}')
            print(f'\tAccuracy: {accuracy}')
            print(f'\tRecall: {recall}')
            print(f'\tPrecision: {precision}')
            print(f'\tSpecificity: {specificity}\n')
        
        except Exception as e:
            print('_print_results_to_console()', str(e))



def _get_template_image(race, folder, i):
    image = '_000' + str(i) + '.jpg'
    return 'rfw/test/data/' + race + '/' + folder + '/' + folder + image


def _get_test_image(race, folder, j):
    file = '_000' + str(j) + '.jpg'
    return 'rfw/test/data/' + race + '/' + folder + '/' + folder + file


def _calculate_test_result(result, race_metrics, test_time):
    
    print("Model Prediction:", result['verified'])

    if result['verified']:
        print("Result: \t  False Positive")
        race_metrics["False Positive"] += 1
    elif not result['verified']:
        print("Result: \t  True Negative")
        race_metrics["True Negative"] += 1

    race_metrics['Negative Test Count'] += 1
    race_metrics['Total Test Time'] += test_time
    race_metrics['Total Test Count'] += 1

    print("Test Time:\t", test_time)
    print("Total Test Count:\t", race_metrics['Total Test Count'])


def _run_tests(race, model, detector, folder_size_list, pair_list, metrics, test_limit, euclidean_distance):
    print("\n|||||||||| Race:", race, "||||||||||||||")

    global exception_list
    metrics_race = metrics[race]

    # Open results file for writing
    with open(f'tmp2/{model}/{race}_results.txt', 'w') as results_file:

        # Write the header of results file
        results_file.write('Template\t\t\t\tTest\t\t\t\t\tPredict\tResult\tTest Time\n')

        # iterate through each image in the folder
        count = 0
        for pair in pair_list:
          
            template_folder = pair[0]
            template_index = int(pair[1])
            template_image = _get_template_image(race, template_folder, template_index)

            test_folder = pair[2]
            test_index = int(pair[3])
            test_image = _get_test_image(race, test_folder, test_index)
            
            print(f"\nTemplate:{template_image}\tTest:{test_image}")

            try:
                # run model
                start_time = time.time()  # start the timer
                result = DeepFace.verify(template_image, test_image, model, detector, euclidean_distance)
                end_time = time.time()
                test_time = end_time - start_time
                tf.keras.backend.clear_session()

                _calculate_test_result(result, metrics_race, test_time)
                _write_test_result_to_file(template_folder, template_index, test_folder, test_index, result, results_file,  test_time)
            except Exception as e:
                print(str(e))
                exception_info = [str(e), race, count, template_folder, template_image, test_image]
                exception_list.append(exception_info)

            count += 1
            if count > test_limit:
                metrics_race['End Time'] = datetime.now()
                break

def _init_values(race):
    pairs_file_path = 'rfw/test/txts/' + race + '/' + race + '_pairs.txt'
    people_file_path = 'rfw/test/txts/' + race + '/' + race + '_people.txt'

    folder_size = []
    with open(people_file_path, 'r') as f:
        for line in f:
            group, num_people = line.strip().split('\t')
            folder_size.append((group, int(num_people)))

    pair_list = []
    with open(pairs_file_path, 'r') as f:
        for line in f:
            data = line.split('\t')
            data[-1] = data[-1].strip('\n')
            data_tuple = tuple(data)

            # only accept pairs from different files
            if len(data) == 4:
                pair_list.append(data_tuple)

    return folder_size, pair_list


def _init_metrics(race, metrics):
    metrics[race] = {
        'True Positive': 0,
        'True Negative': 0,
        'False Positive': 0,
        'False Negative': 0,
        'Positive Test Count': 0,
        'Negative Test Count': 0,
        'Total Test Count': 0,
        'Total Test Time': 0,
        'Start Time': datetime.now(),
        'End Time': ''
    }


def main():
    races = ['African', 'Asian', 'Caucasian', 'Indian']
    # races = ['African']
    model_list = ['DeepFace']
    euclidean_distance = 'euclidean'
    detector = 'mtcnn'
    metrics = {}
    test_limit = 10
    
    for model in model_list:
        for race in races:
            folder_size_list, pair_list = _init_values(race)
            _init_metrics(race, metrics)

            _run_tests(race, model, detector, folder_size_list, pair_list, metrics, test_limit, euclidean_distance)

        _print_results_to_console(races, metrics, model, detector)
        _write_final_results_to_file(races, metrics, model, detector)
        _write_exceptions_to_file(model)


if __name__ == "__main__":
    main()

# models = [
#   "VGG-Face", 
#   "Facenet", 
#   "Facenet512", 
#   "OpenFace", 
#   "DeepFace", 
#   "DeepID", 
#   "ArcFace", _
#   "Dlib", 
#   "SFace",
#   "GhostFaceNet",
# ]

# backends = [
#   'opencv',
#   'ssd',
#   'dlib',
#   'mtcnn',
#   'retinaface',
#   'mediapipe',
#   'yolov8',
#   'yunet',
#   'fastmtcnn',
# ]
# detector_backend = backends[1]
