from transformers import pipeline

# classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")

classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli", device=0)

def zero_shot_classification(sequence_to_classify, candidate_labels):
    prediction = classifier(sequence_to_classify, candidate_labels)
    return prediction

def test_zero_shot_classification():
    sequence_to_classify = "Angela Merkel is a politician in Germany and leader of the CDU"
    candidate_labels = ["economy", "politics", "entertainment", "environment"]
    output = zero_shot_classification(sequence_to_classify, candidate_labels)
    print(output)