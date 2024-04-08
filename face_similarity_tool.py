# from deepface import DeepFace
#
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
#
#
# img1_path = 'rfw/test/data/African/m.0b0pdf/m.0b0pdf_0002.jpg'
# # img2_path = 'rfw/test/data/African/m.0b0pdf/m.0b0pdf_0003.jpg'
#
# img2_path = 'rfw/test/data/African/m.0fpgg4/m.0fpgg4_0003.jpg'
#
#
# model_name = 'Facenet'
#
#
# # works with SFace, OpenFace, DeepID, Facenet and Facenet512
# result = DeepFace.verify(img1_path, img2_path, model_name, detector_backend)          #returns boolean if first pic
#
# # print(result['verified'], result['model'], "Age:", obj[0]['age'], 'Emotion:', obj[0]['dominant_emotion'], 'Race:', obj[0]['dominant_race'], 'Gender:', obj[0]['dominant_gender'])
# print(result['verified'], result['model'])


from deepface import DeepFace

# Function to count true positives, true negatives, false positives, and false negatives
def _run_tests(model, detector, foler_size, pairs):
    data_folder = 'rfw/test/data'

    tp, tn, fp, fn = 0, 0, 0, 0
    test_count = 0

    num_photos = 1 #! ----Error
    image_list = [] #! ------ERROR

    with open(pairs, 'r') as f:
        for line in f:
            if test_count >= num_photos:  # Check a given number of photos
                break

            try:
                img1_id, img1_label, img2_id, img2_label = line.strip().split('\t')
                img1_path = [img_path for img_path, label in image_list if img1_id in img_path][0]
                img2_path = [img_path for img_path, label in image_list if img2_id in img_path][0]

                # Compare images
                result = DeepFace.verify(img1_path, img2_path, model, detector)

                if result['verified']:
                    if img1_label == img2_label:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if img1_label == img2_label:
                        fn += 1
                    else:
                        tn += 1

                test_count += 1

            except Exception as e:
                print("Exception occurred:", str(e))

    return tp, tn, fp, fn, test_count

def _find_folder_size_and_pairs(race):
    # Folder and file paths
    txt_folder = 'rfw/test/txts'

    pairs_file_path = txt_folder + '/' + race + '/' + race + '_pairs.txt'
    people_file_path = txt_folder + '/' + race + '/' + race + '_people.txt'
    # images_file_path = txt_folder + '/' + race + '/' + race + '_images.txt'

    print()
    # print(pairs_file, images_file_path, people_file_path)

    # Read image list
    # image_list = []
    # with open(images_file_path, 'r') as f:
    #
    #     count = 0
    #     for line in f:
    #         img_name, label = line.strip().split('\t')
    #         img_path = data_folder + '/' + race + '/' + img_name
    #
    #         # print(img_path, label)
    #         image_list.append((img_path, int(label)))
    #
    #         count += 1
    #         if count > 1:
    #             break
    #
    # print(image_list)

    # Read number of people

    folder_size = []
    with open(people_file_path, 'r') as f:
        count = 0
        for line in f:
            group, num_people = line.strip().split('\t')
            folder_size.append((group, int(num_people)))
            # count += 1
            # if count > 1:
            #     break

    pairs = {}
    with open(pairs_file_path, 'r') as f:
        count = 0
        for line in f:
            if count > 1:
                break

    return folder_size, pairs

# Main function
def main():
    races = ['African', 'Asian', 'Caucasian', 'Indian']


    folder_size = []    # list of tuples containing folder name and number of people in folder
    pairs = {}          # pairs from the same folder only

    # DeepFace settings
    model = 'Facenet'
    detector = 'mtcnn'

    for race in races:
        folder_size, pairs = _find_folder_size_and_pairs(race)

        print("Race:", race)

        print(folder_size)
        print(pairs)

        # tp, tn, fp, fn, test_count = _run_tests(model, detector, folder_size, pairs)

        # print("True Positives:", tp)
        # print("True Negatives:", tn)
        # print("False Positives:", fp)
        # print("False Negatives:", fn)
        # print("Total Tests:", test_count)
        # print("Total People:", num_people)
        # print()

if __name__ == "__main__":
    main()
