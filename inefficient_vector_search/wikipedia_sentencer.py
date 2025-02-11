with open("Hot_dog.txt", 'r') as original, open("Hot_dog_sentences.txt", 'w') as sentences:
    for line in original:
        for sentence in line.split('. '):
            sentence_stripped = sentence.strip()
            if not sentence_stripped.isspace() and len(sentence_stripped.split(' ')) > 4:
                sentences.write(sentence_stripped+"\n")
