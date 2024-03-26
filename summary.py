import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tokenizer = PegasusTokenizer.from_pretrained("google/pegasus-cnn_dailymail")
model = PegasusForConditionalGeneration.from_pretrained("google/pegasus-cnn_dailymail")

def generate_summary(text):
    # Load fine-tuned Pegasus model and tokenizer
    # Load model directly


    

    # Split text into smaller chunks for processing
    max_chunk_length = 1024  # Maximum length of each chunk
    text_chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]

    # Generate summary for each chunk
    summaries = []
    for chunk in text_chunks:
        # Tokenize input chunk
        inputs = tokenizer(chunk, max_length=max_chunk_length, return_tensors='pt', truncation=True)

        # Generate summary for the chunk
        summary_ids = model.generate(inputs['input_ids'], num_beams=4, min_length=30, max_length=200, early_stopping=True)

        # Decode summary tokens for the chunk
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        summaries.append(summary)

    # Concatenate the summaries of all chunks
    final_summary = ' '.join(summaries)
    return final_summary